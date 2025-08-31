"""Classes and methods needed to publish posts on a Fediverse instance."""

import asyncio
import re
import tempfile
import traceback
from pathlib import Path

import puremagic
import yt_dlp
import yt_dlp.utils
from feedparser import FeedParserDict
from httpx import AsyncClient
from minimal_activitypub.client_2_server import ActivityPub
from minimal_activitypub.client_2_server import ClientError
from minimal_activitypub.client_2_server import NetworkError
from minimal_activitypub.client_2_server import RatelimitError
from stamina import retry
from stamina import retry_context
from whenever import ZonedDateTime

from feed2fedi.collect import FeedReader
from feed2fedi.collect import get_file
from feed2fedi.control import Actions
from feed2fedi.control import Configuration
from feed2fedi.control import FeedInfo
from feed2fedi.control import IgnoringLogger
from feed2fedi.control import PostRecorder


class Fediverse:
    """Helper class to publish posts on a fediverse instance from rss feed items."""

    def __init__(self, config: Configuration, post_recorder: PostRecorder) -> None:
        self.config = config
        self.post_recorder = post_recorder

    async def publish(
        self,
        items: list[FeedParserDict],
        feed: FeedInfo,
        post_limit: int | None,
        client: AsyncClient,
    ) -> int:
        """Publish posts to fediverse instance from content in the items list.

        :param post_limit: Optional; Number of statuses to post before returning
        :param items: Rss feed items to post
        :param feed: Section of config for current feed
        :param client: httpx AsyncClient to use for posting to fedi instance.

        :returns int: Number of new statuses posted.
        """
        statuses_posted = 0
        fediverse = ActivityPub(
            instance=self.config.fedi_instance,
            client=client,
            access_token=self.config.fedi_access_token,
        )
        for attempt in retry_context(on=NetworkError, attempts=3):
            with attempt:
                await fediverse.determine_instance_type()
                await fediverse.verify_credentials()

        if isinstance(feed.max_attachments, int):
            max_media = min(fediverse.max_attachments, feed.max_attachments)
        else:
            max_media = fediverse.max_attachments

        for item in items:
            if await self.post_recorder.duplicate_check(identifier=item.link):
                continue

            filter_action_drop, sensitive, spoiler_text = await self._apply_filters(feed, item)

            if filter_action_drop:
                continue

            status = ""
            if feed.prefix:
                status += f"{feed.prefix} - "
            status += self.config.bot_post_template.format(**item.params).replace("\\n", "\n")

            try:
                media_ids = await self._post_media(fediverse, feed, item, max_media)

                posted_status = await self._post_actual_status(fediverse, media_ids, sensitive, spoiler_text, status)

                print(f"Posted {posted_status['content']} to Fediverse at\n{posted_status['url']}")

                await self.post_recorder.log_post(shared_url=item.link)

                statuses_posted += 1
                if post_limit and statuses_posted >= post_limit:
                    break

            except RatelimitError:
                reset = fediverse.ratelimit_reset
                seconds = reset.timestamp() - ZonedDateTime.now("UTC").timestamp()
                print(
                    f'!!! Server "cool down" - waiting until {reset:%Y-%m-%d %H:%M:%S %z} '
                    f"({round(number=seconds)} seconds)"
                )
                await asyncio.sleep(delay=seconds)

            except ClientError as error:
                print(f"!!! Encountered error: {error}")
                traceback.print_tb(error.__traceback__)
                print("\nLog article to avoid repeat of error")
                await self.post_recorder.log_post(shared_url=item.link)

        return statuses_posted

    @retry(on=NetworkError, attempts=3)
    async def _post_actual_status(self, fediverse, media_ids, sensitive, spoiler_text, status):
        """Post actual status. This has been refactored into its own method to be able to apply retry logic."""
        posted_status = await fediverse.post_status(
            status=status,
            visibility=self.config.bot_post_visibility,
            media_ids=media_ids,
            sensitive=sensitive,
            spoiler_text=spoiler_text,
        )
        return posted_status

    async def _post_media(self, fediverse, feed, item, max_media) -> list[str] | None:
        """Post media if configured to do so."""
        media_ids: list[str] | None = None
        if self.config.bot_post_media and max_media:
            media_ids = await Fediverse._post_video(
                fediverse=fediverse,
                item=item,
                post_videos=feed.post_videos,
            )

            if not media_ids:
                media_ids = await Fediverse._post_images(
                    fediverse=fediverse,
                    item=item,
                    max_images=max_media,
                    image_selector=self.config.bot_post_image_selector,
                    supported_mime_types=fediverse.supported_mime_types,
                )
        return media_ids

    @staticmethod
    async def _apply_filters(feed, item) -> tuple[bool, bool, str | None]:
        """Apply filters to item."""
        filter_action_drop = False
        sensitive = False
        spoiler_text = None
        for item_filter in feed.filters:
            if item_filter.do_check(item):
                if item_filter.action == Actions.DROP:
                    filter_action_drop = True
                    continue
                elif item_filter.action == Actions.SEARCH_REPLACE:
                    search = item_filter.action_params["search"]
                    replace = item_filter.action_params["replace"]
                    item.params["content_html"] = re.sub(search, replace, item.params["content_html"])
                    item.params["content_markdown"] = re.sub(search, replace, item.params["content_markdown"])
                    item.params["content_plaintext"] = re.sub(search, replace, item.params["content_plaintext"])
                elif item_filter.action == Actions.MARK_CW:
                    sensitive = True
                    spoiler_text = item_filter.action_params
        return filter_action_drop, sensitive, spoiler_text

    @staticmethod
    @retry(on=NetworkError, attempts=3)
    async def _post_video(
        fediverse: ActivityPub,
        item: FeedParserDict,
        post_videos: bool,
    ) -> list[str]:
        """Post media to fediverse instance and return media ID.

        :param fediverse: ActivityPub api instance
        :param item: Feed item to load media from
        :param post_videos: Boolean indicating whether videos should be posted.
        :returns:
            List containing no, one  or multiple strings of the media id after upload
        """
        media_ids: list[str] = []
        filenames: list[str] = []

        if not post_videos:
            return media_ids

        try:
            filenames = await Fediverse._get_video(item)
        except yt_dlp.utils.DownloadError:
            # Skip and go to next processing type
            pass

        if len(filenames) > 0:
            for filename in filenames:
                magic_info = puremagic.magic_file(filename=filename)
                mime_type = magic_info[0].mime_type
                try:
                    if mime_type:
                        with Path(filename).open(mode="rb") as file:
                            media = await fediverse.post_media(file=file, mime_type=mime_type)
                        media_ids.append(media.get("id"))
                except ClientError as error:
                    raise ClientError from error
                finally:
                    Path(filename).unlink()

        return media_ids

    @staticmethod
    async def _get_video(item) -> list[str]:
        """Download videos."""
        filenames: list[str] = []
        ydl_opts = {
            "quiet": "true",
            "logger": IgnoringLogger(),
            "no_warnings": "true",
            "ignoreerrors": "true",
            "outtmpl": "%(id)s.%(ext)s",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(item.link, download=True)
            ydl_info = ydl.sanitize_info(info)
            if ydl_info and ydl_info.get("requested_downloads"):
                for dl in ydl_info.get("requested_downloads"):
                    if filename := dl.get("filepath"):
                        filenames.append(filename)
        return filenames

    @staticmethod
    @retry(on=NetworkError, attempts=3)
    async def _post_images(
        fediverse: ActivityPub,
        item: FeedParserDict,
        image_selector: str,
        supported_mime_types: list[str],
        max_images: int = 1,
    ) -> list[str]:
        """Post media to fediverse instance and return media ID.

        :param fediverse: ActivityPub api instance
        :param item: Feed item to load media from
        :param max_images: number of images to post. Defaults to 1
        :param supported_mime_types:  List of strings representing mime types supported by the instance server

        :returns:
            List containing no, one  or multiple strings of the media id after upload
        """
        media_ids: list[str] = []
        media_urls = FeedReader.determine_image_url(item, image_selector)

        for url in media_urls:
            if len(media_ids) == max_images:
                break

            with tempfile.TemporaryFile() as temp_image_file:
                mime_type = await get_file(img_url=url, file=temp_image_file, supported_mime_types=supported_mime_types)
                if mime_type:
                    temp_image_file.seek(0)
                    media = await fediverse.post_media(
                        file=temp_image_file,
                        mime_type=mime_type,
                    )
                    media_ids.append(media["id"])

        return media_ids
