from __future__ import annotations

from enumerific import Enumeration, anno


class FillOrder(Enumeration, aliased=True):
    """The FillOrder class provides enumerations for the FillOrder type."""

    MSB2LSB = anno(
        1,
        description="Pixels are encoded from the most significant bit to least significant bit",
        name="MSB2LSB",
    )

    LSB2MSB = anno(
        2,
        description="Pixels are encoded from the least significant bit to most significant bit",
        name="LSB2MSB",
    )
