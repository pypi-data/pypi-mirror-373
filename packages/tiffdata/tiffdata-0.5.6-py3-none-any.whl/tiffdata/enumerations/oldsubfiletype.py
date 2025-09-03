from __future__ import annotations

from enumerific import Enumeration, anno


class OldSubFileType(Enumeration, aliased=True):
    """The OldSubFileType class provides enumerations for the OldSubFileType type."""

    Image = anno(
        1,
        name="Image",
    )

    ReducedImage = anno(
        2,
        name="ReducedImage",
    )

    Page = anno(
        3,
        name="Page",
    )
