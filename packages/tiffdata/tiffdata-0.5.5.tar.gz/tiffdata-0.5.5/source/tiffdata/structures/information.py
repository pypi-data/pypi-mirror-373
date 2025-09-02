from tiffdata.logging import logger
from tiffdata.enumerations import Format

from deliciousbytes import ByteOrder

logger = logger.getChild(__name__)


class Information(object):
    """The Information class holds structural information about a TIFF file."""

    _filepath: str = None
    _filesize: int = None
    _order: ByteOrder = None
    _format: Format = None
    _offset: int = None

    @property
    def filepath(self) -> str | None:
        return self._filepath

    @filepath.setter
    def filepath(self, filepath: str):
        if filepath is None:
            pass
        elif not isinstance(filepath, str):
            raise TypeError("The 'filepath' argument, must have a string value!")

        self._filepath = filepath

    @property
    def filesize(self) -> int | None:
        return self._filesize

    @filesize.setter
    def filesize(self, filesize: int):
        if filesize is None:
            pass
        elif not isinstance(filesize, int):
            raise TypeError("The 'filesize' argument, must have an integer value!")

        self._filesize = filesize

    @property
    def order(self) -> ByteOrder | None:
        return self._order

    @order.setter
    def order(self, order: ByteOrder):
        if order is None:
            pass
        elif not isinstance(order, ByteOrder):
            raise TypeError(
                "The 'order' argument, must reference a ByteOrder enumeration option!"
            )

        self._order = order

    @property
    def format(self) -> Format | None:
        return self._format

    @format.setter
    def format(self, format: Format):
        if format is None:
            pass
        elif not isinstance(format, Format):
            raise TypeError(
                "The 'format' argument, must reference a Format enumeration option!"
            )

        self._format = format

    @property
    def offset(self) -> int | None:
        """Get the first offset."""

        return self._offset

    @offset.setter
    def offset(self, offset: int):
        """Set the first offset."""

        if not isinstance(offset, int):
            raise TypeError("The 'offset' argument, must have an integer value!")
        elif not offset >= 0:
            raise ValueError(
                "The 'offset' argument, must have a positive integer value!"
            )

        self._offset = offset

    @property
    def first(self) -> int | None:
        """An alias for the first offset property."""

        return self._offset
