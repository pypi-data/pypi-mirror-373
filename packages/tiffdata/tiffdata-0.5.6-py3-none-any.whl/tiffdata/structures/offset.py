from __future__ import annotations

from tiffdata.logging import logger

logger = logger.getChild(__name__)


class Offset(object):
    """The Offset class represents source and target offsets of data within an image."""

    _source: int = None
    _target: int = None
    _padded: bool = False

    def __init__(self, source: int = None, target: int = None, padded: bool = False):
        if source is None:
            self._source: int = 0
        elif not isinstance(source, int):
            raise TypeError("The 'source' argument must have an integer value!")
        elif not source >= 0:
            raise ValueError(
                "The 'source' argument must have a positive integer value!"
            )
        else:
            self._source: int = source

        if target is None:
            self._target: int = 0
        elif not isinstance(target, int):
            raise TypeError("The 'target' argument must have an integer value!")
        elif not target >= 0:
            raise ValueError(
                "The 'target' argument must have a positive integer value!"
            )
        else:
            self._target: int = target

        if not isinstance(padded, bool):
            raise TypeError("The 'padded' argument must have a boolean value!")
        else:
            self._padded: bool = padded

    def __str__(self) -> str:
        return f"<Offset(source: {self.source}, target: {self.target})>"

    @property
    def source(self) -> int | None:
        return self._source

    @source.setter
    def source(self, source: int):
        if not isinstance(source, int):
            raise TypeError("The 'source' argument must have an integer value!")
        elif not source >= 0:
            raise ValueError(
                "The 'source' argument must have a positive integer value!"
            )
        self._source: int = source

    @property
    def target(self) -> int | None:
        return self._target

    @target.setter
    def target(self, target: int):
        if not isinstance(target, int):
            raise TypeError("The 'target' argument must have an integer value!")
        elif not target >= 0:
            raise ValueError(
                "The 'target' argument must have a positive integer value!"
            )
        self._target: int = target

    @property
    def padded(self) -> bool:
        return self._padded

    @padded.setter
    def padded(self, padded: bool):
        if not isinstance(padded, bool):
            raise TypeError("The 'padded' argument must have a boolean value!")
        self._padded: bool = padded

    def copy(self) -> Offset:
        """Create a copy of the current Offset object, with a copy of its values."""
        return Offset(source=self.source, target=self.target, padded=self.padded)
