from __future__ import annotations

from enumerific import Enumeration, anno


class ResolutionUnit(Enumeration, aliased=True):
    """The ResolutionUnit class provides enumerations for the ResolutionUnit type."""

    NoUnit = anno(
        1,
        description="No resolution unit of measurement applies",
        name="NoUnit",
    )

    Inch = anno(
        2,
        name="Inch",
    )

    IN = Inch

    Centimetre = anno(
        3,
        name="Centimetre",
    )

    Centimeter = Centimetre

    CM = Centimetre
