from __future__ import annotations

from enumerific import Enumeration, anno


class ExtraSamples(Enumeration, aliased=True):
    """The ExtraSamples class provides enumerations for the ExtraSamples type."""

    Unspecified = anno(
        0,
        name="Unspecified",
    )

    AssociatedAlpha = anno(
        1,
        name="AssociatedAlpha",
    )

    UnassociatedAlpha = anno(
        2,
        name="UnassociatedAlpha",
    )
