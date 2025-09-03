from __future__ import annotations

from enumerific import anno

from tiffdata.enumerations.datatype import DataType
from tiffdata.enumerations.tifftag import TIFFTag


class InteroperabilityTag(TIFFTag, aliased=True):
    """The InteroperabilityTag class provides enumerations for the InteroperabilityTag type."""

    InteroperabilityIndex = anno(
        1,
        type=DataType.ASCII,
        name="InteroperabilityIndex",
    )
