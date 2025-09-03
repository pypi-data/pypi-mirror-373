"""Backports for <3.11 Python functionality."""

import sys
from enum import Enum


if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    class StrEnum(str, Enum):
        """Backport of Python 3.11's StrEnum."""
        pass
