from __future__ import annotations

from enumerific import Enumeration, anno


class CleanFaxData(Enumeration, aliased=True):
    """The CleanFaxData class provides enumerations for the CleanFaxData type."""

    All = anno(
        0,
        name="All",
    )

    Clean = All

    Regenerated = anno(
        1,
        name="Regenerated",
    )

    Unclean = Regenerated

    Present = anno(
        2,
        name="Present",
    )
