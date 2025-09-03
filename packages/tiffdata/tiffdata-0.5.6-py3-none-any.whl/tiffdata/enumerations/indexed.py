from __future__ import annotations

from enumerific import Enumeration, anno


class Indexed(Enumeration, aliased=True):
    """The Indexed class provides enumerations for the Indexed type."""

    NotIndexed = anno(
        0,
        name="NotIndexed",
    )
