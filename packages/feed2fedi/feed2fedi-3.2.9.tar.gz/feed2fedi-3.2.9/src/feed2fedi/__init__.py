"""Module specific values and logic."""

from importlib.metadata import version
from typing import Final

__version__: Final[str] = version(str(__package__))

DISPLAY_NAME: Final[str] = "Feed2Fedi"
WEBSITE: Final[str] = "https://codeberg.org/MarvinsMastodonTools/feed2fedi"

POST_RECORDER_SQLITE_DB: Final[str] = "cache.sqlite"
FILE_ENCODING: Final[str] = "UTF-8"
