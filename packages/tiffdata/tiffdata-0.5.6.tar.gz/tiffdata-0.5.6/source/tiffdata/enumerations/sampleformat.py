from __future__ import annotations

from enumerific import Enumeration, anno


class SampleFormat(Enumeration, aliased=True):
    """The SampleFormat class provides enumerations for the SampleFormat type."""

    UInt = anno(
        1,
        name="uint",
    )

    UnsignedInteger = UInt

    Int = anno(
        2,
        name="int",
    )

    Float = anno(
        3,
        name="float",
    )

    Undefined = anno(
        4,
        name="Undefined",
    )

    Void = Undefined

    ComplexInt = anno(
        5,
        name="ComplexInt",
    )

    ComplexFloat = anno(
        6,
        name="ComplexFloat",
    )
