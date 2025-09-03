from tiffdata.logging import logger
from tiffdata.structures.file.base import Element
from tiffdata.structures.file.data import Data

logger = logger.getChild(__name__)


class Tile(Data):
    """The Tile class represents a TIFF tile which contains a tile of image data."""

    _index: int = None

    def __init__(self, index: int, **kwargs):
        super().__init__(**kwargs)

        self.index = index

    @Element.label.getter
    def label(self) -> str:
        return f"#{self.index}"

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}(index: {self.index}, offset: {self.offset}, length: {self.length})>"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(index: {self.index}, offset: {self.offset}, length: {self.length}) @ {hex(id(self))}>"

    @property
    def index(self) -> int:
        return self._index

    @index.setter
    def index(self, index: int):
        if not (isinstance(index, int) and index >= 0):
            raise TypeError("The 'index' argument must have a positive integer value!")
        self._index = index
