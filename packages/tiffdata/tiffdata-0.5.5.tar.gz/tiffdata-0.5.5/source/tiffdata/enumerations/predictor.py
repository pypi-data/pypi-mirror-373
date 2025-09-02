from __future__ import annotations

from enumerific import Enumeration, anno


class Predictor(Enumeration, aliased=True):
    """The Predictor class provides enumerations for the Predictor type."""

    NoPredictor = anno(
        1,
        name="NoPredictor",
    )

    Horizontal = anno(
        2,
        name="Horizontal",
    )

    FloatingPoint = anno(
        3,
        name="FloatingPoint",
    )
