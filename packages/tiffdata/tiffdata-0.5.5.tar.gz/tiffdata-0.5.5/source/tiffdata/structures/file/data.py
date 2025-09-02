from tiffdata.logging import logger

from tiffdata.structures.file.base import Element

from tiffdata.enumerations.format import Format
from tiffdata.enumerations.datatype import DataType

from deliciousbytes import ByteOrder

logger = logger.getChild(__name__)


class Data(Element):
    """The Data class represents arbitrary data held within the image."""

    _data: bytes = None
    _type: DataType = None
    _length: int = None
    _parent: Element = None

    def __init__(
        self,
        data: bytes | bytearray = None,
        length: int = None,
        type: DataType = None,
        parent: Element = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.data = data
        self.length = length if isinstance(length, int) else len(data) if data else 0
        self.type = type
        self.parent = parent

    def __str__(self):
        return f"<Data(offset: {self.offset}, length: {self.length}, parent: {self.parent})>"

    @Element.label.getter
    def label(self) -> str:
        return self.parent.label if self.parent else "?"

    @property
    def parent(self) -> Element:
        return self._parent

    @parent.setter
    def parent(self, parent: Element):
        if parent is None:
            self._parent = None
        elif isinstance(parent, Element):
            self._parent = parent
        else:
            raise TypeError(
                "The 'parent' argument must reference a Element class instance!"
            )

    @property
    def data(self) -> bytes | None:
        return self._data

    @data.setter
    def data(self, data: bytes | bytearray | None):
        if data is None:
            self._data = None
            self._length = 0
        elif isinstance(data, (bytes, bytearray)):
            self._data = bytes(data)
            self._length = len(data)
        else:
            raise TypeError("The 'data' argument must have a bytes or bytearray value!")

    @property
    def type(self) -> DataType:
        return self._type or DataType.Undefined

    @type.setter
    def type(self, type: DataType | None):
        if type is None:
            self._type = None
        elif isinstance(type, DataType):
            self._type = type
        else:
            raise TypeError(
                "The 'type' argument, if specified, must reference a DataType enumeration option!"
            )

    @property
    def length(self) -> int:
        return self._length or 0

    @length.setter
    def length(self, length: int):
        if not isinstance(length, int):
            raise TypeError("The 'length' argument must have an integer value!")
        elif not length >= 0:
            raise ValueError(
                "The 'length' argument must have a positive integer value!"
            )

        self._length = length

    def encode(self, order: ByteOrder = ByteOrder.MSB, format: Format = None) -> bytes:
        if not isinstance(order, ByteOrder):
            raise TypeError(
                "The 'order' argument must reference a ByteOrder enumeration option!"
            )

        if not isinstance(format, Format):
            raise TypeError(
                "The 'format' argument must reference a Format enumeration option!"
            )

        encoded: list[bytes] = []

        if isinstance(self.data, (bytes, bytearray)):
            # Assemble the bytes that represent the IFD metadata and data
            encoded.append(self.data)

        return b"".join(encoded)
