from __future__ import annotations

from enumerific import Enumeration, anno


class Orientation(Enumeration, aliased=True):
    """The Orientation class provides enumerations for the Orientation type."""

    TopLeft = anno(
        1,
        name="TopLeft",
    )

    TopRight = anno(
        2,
        name="TopRight",
    )

    BottomRight = anno(
        3,
        name="BottomRight",
    )

    BottomLeft = anno(
        4,
        name="BottomLeft",
    )

    LeftTop = anno(
        5,
        name="LeftTop",
    )

    RightTop = anno(
        6,
        name="RightTop",
    )

    RightBottom = anno(
        7,
        name="RightBottom",
    )

    LeftBottom = anno(
        8,
        name="LeftBottom",
    )
