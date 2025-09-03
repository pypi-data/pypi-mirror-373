from enumerific import Enumeration


class Format(Enumeration):
    """The Format enumeration provides a controlled list of the supported TIFF file
    formats; the library supports the two current existing file formats; Classic TIFF,
    which has a unique identifier of 42, and Big TIFF, which has a unique identifier
    of 43. If other TIFF file formats are developed in the future, and support is added
    to the library, their mnemonics and unique identifiers will be added here."""

    ClassicTIFF = 42
    BigTIFF = 43
