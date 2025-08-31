"""Module containing utilities and helper methods."""

import configparser
from itertools import zip_longest
from pathlib import Path
from typing import Annotated

import msgspec
import msgspec.json
import typer
from minimal_activitypub import Visibility

from feed2fedi.control import BOT_POST_IMAGE_SELECTOR_DEFAULT
from feed2fedi.control import Configuration
from feed2fedi.control import FeedInfo


def convert_config_json(  # nocl
    config_file: Annotated[
        Path,
        typer.Option(
            "--config-file",
            "-c",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="filename and optional path to old config INI file",
        ),
    ],
    config_json: Annotated[
        Path,
        typer.Option(
            "--config-json",
            "-j",
            file_okay=True,
            dir_okay=False,
            writable=True,
            resolve_path=True,
            help="filename and optional path to new config JSON file",
        ),
    ],
) -> None:
    """Convert a .conf file to a .json config file."""
    config_ini = configparser.ConfigParser()
    with config_file.open(mode="r", encoding="UTF-8") as old_config_file:
        config_ini.read_file(f=old_config_file)

    old_feeds = [feed for _key, feed in config_ini.items(section="Feeds")]
    old_prefixes = [prefix for _key, prefix in config_ini.items(section="Prefixes")]

    new_feeds: list[FeedInfo] = []
    for feed, prefix in zip_longest(old_feeds, old_prefixes, fillvalue=""):
        new_feeds.append(FeedInfo(url=feed, prefix=prefix, max_attachments=1))

    new_config = Configuration(
        bot_post_visibility=Visibility(config_ini.get(section="Bot", option="post_visibility")),
        bot_post_media=bool(config_ini.get(section="Bot", option="post_media")),
        bot_post_image_selector=BOT_POST_IMAGE_SELECTOR_DEFAULT,
        bot_post_template="{title}\n\n{link}",
        cache_max_age=int(config_ini.get(section="Cache", option="max-age")),
        cache_db_path=config_ini.get(section="Cache", option="db-path"),
        fedi_instance=config_ini.get(section="Fediverse", option="instance"),
        fedi_access_token=config_ini.get(section="Fediverse", option="access-token"),
        feeds=new_feeds,
    )

    with config_json.open(mode="wb") as new_config_file:
        json_config = msgspec.json.encode(new_config)
        new_config_file.write(msgspec.json.format(json_config, indent=4))


def start_conversion() -> None:
    """Start the conversion process."""
    typer.run(convert_config_json)
