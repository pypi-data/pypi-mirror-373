from __future__ import annotations

from enumerific import Enumeration, anno


class T4Options(Enumeration, flags=True):
    """The T4Options class provides enumerations for the T4Options type."""

    TwoDimensionalEncoding = anno(
        1,
        name="TwoDimensionalEncoding",
    )

    Uncompressed = anno(
        2,
        name="Uncompressed",
    )

    FillBits = anno(
        4,
        name="FillBits",
    )
