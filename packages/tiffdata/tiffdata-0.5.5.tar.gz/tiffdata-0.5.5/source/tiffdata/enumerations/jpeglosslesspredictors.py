from __future__ import annotations

from enumerific import Enumeration, anno


class JPEGLosslessPredictors(Enumeration, aliased=True):
    """The JPEGLosslessPredictors class provides enumerations for the JPEGLosslessPredictors type."""

    A = anno(
        1,
        name="A",
        predictor="A",
    )

    B = anno(
        2,
        name="B",
        predictor="B",
    )

    C = anno(
        3,
        name="C",
        predictor="C",
    )

    APlusBMinusC = anno(
        4,
        name="APlusBMinusC",
        predictor="A+B-C",
    )

    APlusHalfBMinusC = anno(
        5,
        name="APlusHalfBMinusC",
        predictor="A+((B-C)/2)",
    )

    BPlusHalfAMinusC = anno(
        6,
        name="BPlusHalfAMinusC",
        predictor="B+((A-C)/2)",
    )

    HalfAPlusB = anno(
        7,
        name="HalfAPlusB",
        predictor="(A+B)/2",
    )
