from __future__ import annotations

from enumerific import Enumeration, anno


class PhotometricInterpretation(Enumeration, aliased=True):
    """The PhotometricInterpretation class provides enumerations for the PhotometricInterpretation type."""

    WhiteIsZero = anno(
        0,
        name="WhiteIsZero",
    )

    BlackIsZero = anno(
        1,
        name="BlackIsZero",
    )

    RGB = anno(
        2,
        name="RGB",
    )

    Palette = anno(
        3,
        name="Palette",
    )

    Mask = anno(
        4,
        name="Mask",
    )

    ColourSeparation = anno(
        5,
        name="ColourSeparation",
    )

    ColorSeparation = ColourSeparation

    YCbCr = anno(
        6,
        name="YCbCr",
    )

    CIELab = anno(
        8,
        name="CIELab",
    )

    ICCLab = anno(
        9,
        name="ICCLab",
    )

    ITULab = anno(
        10,
        name="ITULab",
    )

    CFA = anno(
        32803,
        name="CFA",
    )

    LogL = anno(
        32844,
        name="LogL",
    )

    LogLuv = anno(
        32845,
        name="LogLuv",
    )
