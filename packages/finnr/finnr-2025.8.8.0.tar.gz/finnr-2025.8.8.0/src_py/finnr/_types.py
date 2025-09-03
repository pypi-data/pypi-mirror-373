from __future__ import annotations

from enum import Enum
from typing import Annotated
from typing import Any
from typing import Protocol

from docnote import ClcNote


class Singleton(Enum):
    UNKNOWN = 'unknown'
    MISSING = 'missing'


class DateLike(Protocol):
    """Something is date-like if it includes a year, month, and
    day as attributes. We include this for convenience, so that
    users can bring their own datetime library.

    Note that month and day must both be 1-indexed, ie,
    2025-01-01 would be represented by ``{year: 2025, month: 1,
    day: 1}``.
    """
    year: Annotated[
        int | Any,
        ClcNote('''Must be an int or int-like. Annotated to include
            ``Any`` to support properties, as used by eg. ``whenever``.
            ''')]
    month: Annotated[
        int | Any,
        ClcNote('''Must be an int or int-like. Annotated to include
            ``Any`` to support properties, as used by eg. ``whenever``.
            ''')]
    day: Annotated[
        int | Any,
        ClcNote('''Must be an int or int-like. Annotated to include
            ``Any`` to support properties, as used by eg. ``whenever``.
            ''')]
