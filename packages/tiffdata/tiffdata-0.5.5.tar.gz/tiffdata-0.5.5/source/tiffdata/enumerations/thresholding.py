from __future__ import annotations

from enumerific import Enumeration, anno


class Thresholding(Enumeration, aliased=True):
    """The Thresholding class provides enumerations for the Thresholding type."""

    Bilevel = anno(
        1,
        name="Bilevel",
    )

    Halftone = anno(
        2,
        name="Halftone",
    )

    ErrorDiffuse = anno(
        3,
        name="ErrorDiffuse",
    )
