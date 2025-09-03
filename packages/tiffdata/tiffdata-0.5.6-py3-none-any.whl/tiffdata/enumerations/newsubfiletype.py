from __future__ import annotations

from enumerific import Enumeration, anno


class NewSubFileType(Enumeration, flags=True):
    """The NewSubFileType class provides enumerations for the NewSubFileType type."""

    ReducedImage = anno(
        1,
        name="ReducedImage",
    )

    Page = anno(
        2,
        name="Page",
    )

    Mask = anno(
        4,
        name="Mask",
    )

    Macro = anno(
        8,
        name="Macro",
    )

    MRC = anno(
        16,
        name="MRC",
    )
