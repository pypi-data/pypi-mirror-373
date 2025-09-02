from tiffdata.logging import logger
from tiffdata.structures.offset import Offset
from tiffdata.structures.file.base import Element
from tiffdata.enumerations import Format
from tiffdata.exceptions import TIFFDataError

from deliciousbytes import (
    ByteOrder,
    UInt16,
    UInt32,
    UInt64,
)

logger = logger.getChild(__name__)


class Container(Element):
    """The Container class represents the root container for a TIFF file image."""

    _order: ByteOrder = None
    _format: Format = None
    _first: Offset = None

    def __init__(self, order: ByteOrder, format: Format, first: Offset, **kwargs):
        super().__init__(**kwargs)

        self.order = order
        self.format = format
        self.first = first
        self.label = "$"  # "$" is commonly used to denote the root node in XML/JSON

    @property
    def order(self) -> ByteOrder:
        return self._order

    @order.setter
    def order(self, order: ByteOrder):
        if not isinstance(order, ByteOrder):
            raise TypeError(
                "The 'order' argument must reference a ByteOrder enumeration option!"
            )

        self._order: ByteOrder = order

    @property
    def format(self) -> Format:
        return self._format

    @format.setter
    def format(self, format: Format):
        if not isinstance(format, Format):
            raise TypeError(
                "The 'format' argument must reference a Format enumeration option!"
            )
        self._format: Format = format

    @property
    def first(self) -> Offset:
        return self._first

    @first.setter
    def first(self, first: Offset):
        if not isinstance(first, Offset):
            raise TypeError(
                "The 'first' argument must reference an Offset class instance!"
            )
        self._first: Offset = first

    @Element.length.getter
    def length(self) -> int:
        """Provide an overridden implementation of the length property getter method."""

        if self.format is Format.ClassicTIFF:  # 8 bytes
            return (
                2  # length of byte order mark (2 bytes: 'MM' or 'II')
                + 2  # length of TIFF format specifier (2 bytes: '42' or '43')
                + 4  # length of offset to first IFD (4 bytes, 32 bit unsigned integer)
            )
        elif self.format is Format.BigTIFF:  # 16 bytes
            return (
                2  # length of byte order mark (2 bytes: 'MM' or 'II')
                + 2  # length of TIFF format specifier (2 bytes: '42' or '43')
                + 2  # length of offset value in bytes (2 bytes, 16 bit unsigned integer)
                + 2  # length of padding value in bytes (2 bytes, 16 bit unsigned integer)
                + 8  # length of offset value in bytes (8 bytes, 64 bit unsigned integer)
            )
        else:
            raise TIFFDataError(
                "Unsupported TIFF format; must be Classic of Big TIFF only!"
            )

    def encode(self, order: ByteOrder = None, format: Format = None) -> bytes:
        if not isinstance(order, ByteOrder):
            raise TypeError(
                "The 'order' argument must reference a ByteOrder enumeration option!"
            )

        if not isinstance(format, Format):
            raise TypeError(
                "The 'format' argument must reference a Format enumeration option!"
            )

        encoded: bytearray = bytearray()

        # Encode byte order mark: MM for big endian (Motorolla), II for litte endian (Intel)
        # Regardless of the TIFF file format, this always occupies two bytes
        if order is ByteOrder.MSB:
            encoded += b"MM"
        elif order is ByteOrder.LSB:
            encoded += b"II"

        # Encode the file format specifier: 42 for Classic TIFF, 43 for Big TIFF
        # Regardless of the TIFF file format, this always occupies two bytes (UInt16)
        if format is Format.ClassicTIFF:
            encoded += UInt16(42).encode(order)
        elif format is Format.BigTIFF:
            encoded += UInt16(43).encode(order)

        # Encode the offset to the first (0th) IFD
        if format is Format.ClassicTIFF:
            # For Classic TIFF, this occupies four bytes (UInt32)
            encoded += UInt32(self.first.target).encode(order)
        elif format is Format.BigTIFF:
            # For Big TIFF, the header also includes a two byte value denoting the size
            # of the value holding the offset, followed by two bytes of padding, finally
            # followed by the offset to the first (0th) IFD in eight bytes (UInt64)
            encoded += UInt16(8).encode(order)
            encoded += UInt16(0).encode(order)
            encoded += UInt64(self.first.target).encode(order)

        return bytes(encoded)
