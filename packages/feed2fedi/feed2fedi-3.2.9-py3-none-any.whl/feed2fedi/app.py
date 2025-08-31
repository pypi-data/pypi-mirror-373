"""Main processing and main entry point methods for Feed2Fedi."""

import asyncio
import sys
import traceback
from pathlib import Path
from typing import Annotated

import typer
from httpx import AsyncClient
from minimal_activitypub.client_2_server import ActivityPubError

from feed2fedi import DISPLAY_NAME
from feed2fedi import __version__
from feed2fedi.collect import FeedReader
from feed2fedi.control import PostRecorder
from feed2fedi.control import load_config
from feed2fedi.publish import Fediverse


async def main(config_file: Path, post_limit: int | None = None):
    """Read configuration and feeds, then make posts while avoiding duplicates.

    :param post_limit: Optional; number of new statuses to post before exiting. Default is "None" and if so we process
        all entries in all configured RSS/Atom feeds.
    :param config_file: Path and file name of file to use for reading and storing configuration from
    """
    error_encountered = False

    print(f"Welcome to {DISPLAY_NAME} {__version__}")

    config = await load_config(config_file_path=Path(config_file))

    async with (
        PostRecorder(history_db_path=config.cache_db_path) as post_recorder,
        AsyncClient(http2=True, timeout=30) as client,
    ):
        await post_recorder.prune(max_age_in_days=config.cache_max_age)

        fediverse = Fediverse(config=config, post_recorder=post_recorder)

        statuses_posted = 0
        for feed in config.feeds:
            items = FeedReader(feed=feed.url).items

            try:
                statuses_posted += await fediverse.publish(items=items, feed=feed, post_limit=post_limit, client=client)
            except ActivityPubError as publishing_error:
                error_encountered = True
                print(f"Encountered the following error during publishing feed items:\n{publishing_error}")
                traceback.print_tb(publishing_error.__traceback__)
                break

            if post_limit and statuses_posted >= post_limit:
                break

    if error_encountered:
        sys.exit(1)


async def import_urls(config_file: Path, url_file: Path) -> None:
    """Start import of URLS into cache db.

    :param config_file: Path and file name of file to use for reading and storing configuration from
    :param url_file: Path and file name to file to be imported
    """
    print(f"Welcome to {DISPLAY_NAME} {__version__}")
    print("\nImporting URLS into cache db from ...")

    config = await load_config(config_file_path=Path(config_file))

    post_recorder = PostRecorder(history_db_path=config.cache_db_path)
    await post_recorder.db_init()

    await post_recorder.import_urls(url_file=Path(url_file))

    await post_recorder.close_db()


def start_main() -> None:
    """Start processing, i.e. main entry point."""
    try:
        typer.run(start_main_shim)
    except asyncio.CancelledError:
        pass


def start_main_shim(
    config_file: Annotated[
        Path,
        typer.Option(
            "--config-file",
            "-c",
            file_okay=True,
            dir_okay=False,
            writable=True,
            resolve_path=True,
            help="filename and optional path to config file",
        ),
    ] = Path("./config.json"),
    post_limit: Annotated[
        int | None,
        typer.Option(
            "--limit",
            "-l",
            help="Limit how many new statuses should be posted",
        ),
    ] = None,
) -> None:
    """Start Feed2Fedi."""
    asyncio.run(main(config_file=config_file, post_limit=post_limit))


def start_import_shim(
    url_file: Annotated[
        Path,
        typer.Option(
            "--url-file",
            help="Path and file name to file to be imported. It should contain one URL per line",
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    config_file: Annotated[
        Path,
        typer.Option(
            "--config-file",
            "-c",
            file_okay=True,
            dir_okay=False,
            writable=True,
            resolve_path=True,
            help="filename and optional path to config file",
        ),
    ] = Path("./config.json"),
) -> None:
    """Import of URLS into cache db."""
    asyncio.run(import_urls(config_file=config_file, url_file=url_file))


def start_import() -> None:
    """Call start import shim for typer."""
    typer.run(start_import_shim)
