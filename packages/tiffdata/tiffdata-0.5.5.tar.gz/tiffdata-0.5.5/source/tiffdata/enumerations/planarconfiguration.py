from __future__ import annotations

from enumerific import Enumeration, anno


class PlanarConfiguration(Enumeration, aliased=True):
    """The PlanarConfiguration class provides enumerations for the PlanarConfiguration type."""

    Chunky = anno(
        1,
        name="Chunky",
    )

    Planar = anno(
        2,
        name="Planar",
    )
