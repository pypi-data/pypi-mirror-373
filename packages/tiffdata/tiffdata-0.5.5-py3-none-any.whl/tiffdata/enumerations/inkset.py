from __future__ import annotations

from enumerific import Enumeration, anno


class InkSet(Enumeration, aliased=True):
    """The InkSet class provides enumerations for the InkSet type."""

    CMYK = anno(
        1,
        name="CMYK",
    )

    NotCMYK = anno(
        2,
        name="NotCMYK",
    )

    MultiInk = NotCMYK
