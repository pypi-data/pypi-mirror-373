from __future__ import annotations

from enumerific import Enumeration, anno


class Compression(Enumeration, aliased=True):
    """The Compression class provides enumerations for the Compression type."""

    NA = anno(
        1,
        name="None",
    )

    CCITTRLE = anno(
        2,
        name="CCITTRLE",
    )

    CCITTT4 = anno(
        3,
        name="CCITTT4",
    )

    CCITTFAX3 = CCITTT4

    CCITTT6 = anno(
        4,
        name="CCITTT6",
    )

    CCITTFAX4 = CCITTT6

    LZW = anno(
        5,
        name="LZW",
    )

    OldJPEG = anno(
        6,
        name="OldJPEG",
        lossy=True,
    )

    JPEG = anno(
        7,
        name="JPEG",
        lossy=True,
    )

    AdobeDeflate = anno(
        8,
        name="AdobeDeflate",
    )

    T85 = anno(
        9,
        name="T85",
    )

    T43 = anno(
        10,
        name="T43",
    )

    NeXT = anno(
        32766,
        name="NeXT",
    )

    CCITTRLEW = anno(
        32771,
        name="CCITTRLEW",
    )

    PackBits = anno(
        32773,
        name="PackBits",
    )

    ThunderScan = anno(
        32809,
        name="ThunderScan",
    )

    IT8CTPad = anno(
        32895,
        name="IT8CTPad",
    )

    IT8LW = anno(
        32896,
        name="IT8LW",
    )

    IT8MP = anno(
        32897,
        name="IT8MP",
    )

    IT8BL = anno(
        32898,
        name="IT8BL",
    )

    PixarFilm = anno(
        32908,
        name="PixarFilm",
    )

    PixarLog = anno(
        32909,
        name="PixarLog",
    )

    Deflate = anno(
        32946,
        name="Deflate",
    )

    DCS = anno(
        32947,
        name="DCS",
    )

    JPEG2000YCbCr = anno(
        33003,
        name="JPEG2000YCbCr",
        lossy=True,
    )

    JPEG2000Lossy = anno(
        33004,
        name="JPEG2000Lossy",
        lossy=True,
    )

    JPEG2000RGB = anno(
        33005,
        name="JPEG2000RGB",
        lossy=True,
    )

    JBIG = anno(
        34661,
        name="JBIG",
    )

    SGILog = anno(
        34676,
        name="SGILOG",
    )

    SGILog24 = anno(
        34677,
        name="SGILOG24",
    )

    JPEG2000 = anno(
        34712,
        name="JPEG2000",
        lossy=True,
    )

    LERC = anno(
        34887,
        name="LERC",
        lossy=True,
    )

    LZMA = anno(
        34925,
        name="LZMA",
    )

    ZSTD = anno(
        50000,
        name="ZSTD",
    )

    WEBP = anno(
        50001,
        name="WEBP",
        lossy=True,
    )

    JXL = anno(
        50002,
        name="JXL",
    )
