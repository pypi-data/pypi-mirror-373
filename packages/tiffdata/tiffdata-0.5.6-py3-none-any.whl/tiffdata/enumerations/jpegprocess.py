from __future__ import annotations

from enumerific import Enumeration, anno


class JPEGProcess(Enumeration, aliased=True):
    """The JPEGProcess class provides enumerations for the JPEGProcess type."""

    Baseline = anno(
        1,
        name="Baseline",
    )

    LosslessHuffman = anno(
        14,
        name="LosslessHuffman",
    )

    Huffman = LosslessHuffman
