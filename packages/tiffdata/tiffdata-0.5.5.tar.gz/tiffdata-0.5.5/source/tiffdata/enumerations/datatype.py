from enumerific import Enumeration, anno

from tiffdata.types import (
    Int8,
    UInt8,
    SignedShort,
    UnsignedShort,
    SignedLong,
    UnsignedLong,
    SignedLongLong,
    UnsignedLongLong,
    SignedRational,
    UnsignedRational,
    Float,
    Double,
    Bytes,
    ASCII,
    UTF8,
)


class DataType(Enumeration):
    """The DataType enumeration provides a controlled list of data types that are used
    within TIFF IFD Tags. The enumeration option integer values map to those defined by
    the TIFF file format specification. The additional annotation values detailed below
    are used by the TIFFData library to simplify working with the various types."""

    Empty = anno(
        0,
        size=0,
        type=None,
        description="Empty",
    )

    Byte = anno(
        1,
        size=8,
        type=UInt8,
        description="Unsigned byte (UInt8)",
    )

    ASCII = anno(
        2,
        size=8,
        type=ASCII,
        encoding="ASCII",
        description="ASCII encoded nul-terminated string",
    )

    Short = anno(
        3,
        size=16,
        type=UnsignedShort,
        description="Unsigned short integer (UInt16)",
    )

    Long = anno(
        4,
        size=32,
        type=UnsignedLong,
        description="Unsigned long integer (UInt32)",
    )

    Rational = anno(
        5,
        size=64,
        type=UnsignedRational,
        description="Unsigned rational – two unsigned long integers (UInt32) representing a numerator and denominator",
    )

    SByte = anno(
        6,
        size=8,
        type=Int8,
        description="Signed byte (Int8)",
    )

    Undefined = anno(
        7,
        size=8,
        type=Bytes,
        description="Undefined binary data",
    )

    SShort = anno(
        8,
        size=16,
        type=SignedShort,
        description="Signed short integer (Int16)",
    )

    SLong = anno(
        9,
        size=32,
        type=SignedLong,
        description="Signed long integer (Int32)",
    )

    SRational = anno(
        10,
        size=32,
        type=SignedRational,
        description="Signed rational – two signed long integers (Int32) representing a numerator and denominator",
    )

    Float = anno(
        11,
        size=32,
        type=Float,
        description="Signed 32-bit float – an IEEE-754 single-precision float",
    )

    Double = anno(
        12,
        size=64,
        type=Double,
        description="Signed 64-bit float – an IEEE-754 double-precision float",
    )

    ClassicIFD = anno(
        13,
        size=32,
        type=UnsignedLong,
        description="Unsigned long (UInt32) used to hold the location of an IFD (Image File Directory) in the Classic TIFF file format",
    )

    LongLong = anno(
        16,
        size=64,
        type=UnsignedLongLong,
        description="Unsigned long long (UInt64)",
    )

    SLongLong = anno(
        17,
        size=64,
        type=SignedLongLong,
        description="Signed long long (Int64)",
    )

    BigIFD = anno(
        18,
        size=64,
        type=UnsignedLongLong,
        description="Unsigned long long (UInt64) used to hold the location of an IFD (Image File Directory) in the Big TIFF file format",
    )

    UTF8 = anno(
        129,
        size=8,
        type=UTF8,
        encoding="UTF-8 encoded string",
    )
