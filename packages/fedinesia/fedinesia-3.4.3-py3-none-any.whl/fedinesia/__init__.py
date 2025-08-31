"""Package 'fedinesia' level definitions."""

from importlib.metadata import version
from typing import Final

__version__: Final[str] = version(str(__package__))

__package_name__: Final[str] = str(__package__)
__display_name__: Final[str] = str(__package__.title()) if __package__ else __package_name__
USER_AGENT: Final[str] = f"{__display_name__}"

CLIENT_WEBSITE: Final[str] = "https://codeberg.org/marvinsmastodontools/fedinesia"

PROGRESS_ID_KEY = "last_deleted_id"
