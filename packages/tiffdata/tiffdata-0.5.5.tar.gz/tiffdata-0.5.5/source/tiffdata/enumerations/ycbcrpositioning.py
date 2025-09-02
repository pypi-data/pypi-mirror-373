from __future__ import annotations

from enumerific import Enumeration, anno


class YCbCrPositioning(Enumeration, aliased=True):
    """The YCbCrPositioning class provides enumerations for the YCbCrPositioning type."""

    Centered = anno(
        1,
        name="Centered",
    )

    Cosited = anno(
        2,
        name="Cosited",
    )
