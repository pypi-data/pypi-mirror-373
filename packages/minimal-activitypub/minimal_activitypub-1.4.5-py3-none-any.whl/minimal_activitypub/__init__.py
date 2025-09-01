"""Package 'minimal_activitypub' level definitions."""

import sys
from enum import Enum
from importlib.metadata import version
from typing import Any
from typing import Dict
from typing import Final

__display_name__: Final[str] = "Minimal-ActivityPub"
__version__: Final[str] = version(str(__package__))

USER_AGENT: Final[str] = f"{__display_name__}_v{__version__}_Python_{sys.version.split()[0]}"

Status = Dict[str, Any]


class Visibility(str, Enum):
    """Enumerating possible Visibility values for statuses."""

    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"
    DIRECT = "direct"


class SearchType(str, Enum):
    """Enumerating possible type values for status searches."""

    ACCOUNTS = "accounts"
    HASHTAGS = "hashtags"
    STATUSES = "statuses"
