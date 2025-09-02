from __future__ import annotations

from enumerific import Enumeration, anno


class T6Options(Enumeration, flags=True):
    """The T6Options class provides enumerations for the T6Options type."""

    Uncompressed = anno(
        2,
        name="Uncompressed",
    )
