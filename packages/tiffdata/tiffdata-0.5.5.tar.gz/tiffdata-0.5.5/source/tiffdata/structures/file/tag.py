from __future__ import annotations

from tiffdata.logging import logger
from tiffdata.structures.file.base import Element
from tiffdata.structures.file.data import Data
from tiffdata.structures.file import ifd
from tiffdata.structures.offset import Offset
from tiffdata.structures import Attributes

from tiffdata.enumerations import (
    Format,
    DataType,
    TIFFTag,
)

from tiffdata.exceptions import (
    TIFFDataError,
    TIFFDataParseError,
)

from tiffdata.types import (
    Value,
)

from deliciousbytes import (
    ByteOrder,
    UInt16,
    UInt32,
    UInt64,
    Bytes,
    Bytes32,
    Bytes64,
    BytesView,
)
from deliciousbytes.utilities import hexbytes

import builtins
import io


logger = logger.getChild(__name__)


class Tag(Element):
    """The Tag class represents an Image File Directory (IFD) Tag in a TIFF file.

    An IFD Tag comprises of the following components, consisting of 12 bytes:
    +---------------+-----------------------------------------------------------------+
    | Tag ID        | Two bytes holding the tag ID                                    |
    +---------------+-----------------------------------------------------------------+
    | Data Type     | Two bytes holding the data type indicator, from those below:    |
    |               | * 0 = Empty                                                     |
    |               | * 1 = Byte - 8-bit unsigned byte integer                        |
    |               | * 2 = ASCII - 8-bit holding 7-bit ASCII code, null-terminated   |
    |               | * 3 = Short - 16-bit unsigned short integer                     |
    |               | * 4 = Long - 32-bit unsigned long integer                       |
    |               | * 5 = Rational - two longs; holding numerator and denominator   |
    |               | * 6 = SByte - 8-bit signed byte integer                         |
    |               | * 7 = Undefined - 8-bit byte holding any value per field specs  |
    |               | * 8 = SShort - 16-bit signed short integer                      |
    |               | * 9 = SLong (Signed) - 32-bit signed integer (2's compliment)   |
    |               | * 10 = SRational (Signed) - signed rational of two signed-longs |
    |               | * 11 = Float (Signed) 32-bit float - IEEE-754 single-precision  |
    |               | * 12 = Double (Signed) 64-bit float - IEEE-754 double-precision |
    |               | * 13 = ClassicIFD - 32-bit unsigned integer for sub IFD offset  |
    |               | * 16 = LongLong - 64-bit signed long long integer               |
    |               | * 17 = ULongLong - 64-bit unsigned long long integer            |
    |               | * 18 = BigIFD - 64-bit unsigned integer for sub IFD offset      |
    |               | * 129 = UTF-8 - 8-bit byte UTF-8 string, null-terminated        |
    +---------------+-----------------------------------------------------------------+
    | Data Count    | Four or eight bytes holding the count of values that follow     |
    +---------------+-----------------------------------------------------------------+
    | Data / Offset | Four or eight bytes holding the data or an offset to the data   |
    +---------------+-----------------------------------------------------------------+
    """

    _id: UInt16 = None
    _name: str = None
    _type: UInt16 = None
    _count: UInt32 = None
    _data: Bytes32 | Bytes64 = None
    _subs: list[IFD] = None
    _ifd: IFD = None
    _tiff: TIFF = None
    _attributes: dict[str, object] = None
    _updated: bool = False

    def __init__(
        self,
        id: UInt16,
        type: UInt16 | DataType,
        count: UInt32 = 1,
        data: Bytes = None,
        subs: list[ifd.IFD] = None,
        offset: Offset | int = 0,
        name: str = None,
        tiff: TIFF = None,
        **attributes: dict[str, object],
    ):
        super().__init__(offset=offset)

        self._tiff: TIFF = tiff

        if not isinstance(id, int):
            raise TypeError("The 'id' argument must have an integer value!")
        elif not 1 <= id <= UInt16.MAX:
            raise TypeError(
                "The 'id' argument must have an integer value between 1 - %d!"
                % (UInt16.MAX)
            )

        self._id: UInt16 = UInt16(id)

        if isinstance(type, int):
            if DataType.validate(type) is True:
                self._type: UInt16 = UInt16(type)
            else:
                raise TypeError(
                    "The 'type' argument must have a valid data type values!"
                )
        elif isinstance(type, DataType):
            self._type: UInt16 = UInt16(type.value)
        else:
            raise TypeError(
                "The 'type' argument must have an integer or DataType enumeration value, not %s!"
                % (builtins.type(type))
            )

        if not isinstance(count, int):
            raise TypeError(
                "The 'count' argument must have an integer value, not %s!"
                % (builtins.type(count))
            )
        elif not 1 <= count <= UInt32.MAX:
            raise TypeError(
                "The 'count' argument must have an integer value between 1 - %d!"
                % (UInt32.MAX)
            )

        self._count: UInt32 = UInt32(count)

        if data is None:
            pass
        elif isinstance(data, Bytes32):
            self._data: Bytes32 = data
        elif isinstance(data, Bytes64):
            self._data: Bytes64 = data
        elif isinstance(data, Bytes):
            self._data: Bytes = data
        else:
            raise TypeError(
                "The 'data' argument must have a Bytes value, not %s!"
                % (builtins.type(data))
            )

        if subs is None:
            self._subs: list[IFD] = []
        elif not isinstance(subs, list):
            raise TypeError("The 'subs' argument must have a list value!")
        else:
            for sub in subs:
                if not isinstance(sub, ifd.IFD):
                    raise TypeError(
                        "Each entry in the 'subs' list must be an IFD class instance!"
                    )

                sub.carrier = self

            self._subs: list[IFD] = subs

        self._name = name

        self._attributes: dict[str, object] = attributes

    def __len__(self) -> int:
        return len(self._subs)

    def __iter__(self) -> Tag:
        for sub in self._subs:
            yield sub

    def __bool__(self) -> bool:
        return True

    def __getattr__(self, name: str) -> object | None:
        # logger.debug("Tag.__getattr__(name: %s)" % (name))

        if name.startswith("_"):
            return object.__getattribute__(self, name)
        elif name in dir(self):
            return object.__getattribute__(self, name)
        elif name in self._attributes:
            return self._attributes[name]
        else:
            raise AttributeError(f"The Tag class has no '{name}' attribute!")

    def __setattr__(self, name: str, value: object):
        if name.startswith("_") or name in dir(self):
            return super().__setattr__(name, value)
        else:
            self._attributes[name] = value

    def clone(self, offset: int = None) -> Tag:
        return Tag(
            id=self.id,
            type=self.type,
            count=self.count,
            data=self.data,
            offset=offset,
            subs=self.subs,
            tiff=self.tiff,
            **self.attributes,
        )

    @Element.label.getter
    def label(self) -> str:
        return f"{self.id}#{self.name}"

    @property
    def attributes(self) -> Attributes:
        """The 'attributes' property returns the tag's Attributes instance."""

        return self._attributes

    @property
    def tiff(self) -> TIFF:
        """The 'name' property returns the tag's parent TIFF instance."""

        return self._tiff

    @property
    def id(self) -> UInt16:
        """The 'name' property returns the tag's ID."""

        return self._id

    @property
    def name(self) -> str:
        """The 'name' property returns the tag's name."""

        return self._name

    @property
    def type(self) -> UInt16:
        """The data type represented as an byte-encoded integer."""

        return self._type

    @property
    def datatype(self) -> DataType:
        """The data type represented as a DataType enumeration option."""

        return DataType.reconcile(self._type)

    @property
    def datasize(self) -> int:
        """Compute the size in bytes of the data held by or referenced by the tag."""

        return self.count * int(self.datatype.size / 8)

    @property
    def dataoffset(self) -> int:
        return int(self.attributes.get("dataoffset", 0))

    @property
    def new(self) -> bool:
        return bool(self.attributes.get("new", False))

    @new.setter
    def new(self, new: bool):
        if not isinstance(new, bool):
            raise TypeError("The 'new' argument must have a boolean value!")
        self.attributes["new"] = new

    @property
    def updated(self) -> bool:
        return self._updated

    @updated.setter
    def updated(self, updated: bool):
        if not isinstance(updated, bool):
            raise TypeError("The 'updated' argument must have a boolean value!")

        self._updated = updated

    @property
    def count(self) -> UInt32:
        """The number of data values of the specified type that follow in the data."""

        return self._count

    @count.setter
    def count(self, count: int):
        if not isinstance(count, int):
            raise TypeError("The 'count' argument must have an integer value!")
        elif not count >= 1:
            raise ValueError("The 'count' argument must have an integer value >= 1!")

        self._count = count

    @property
    def data(self) -> Bytes | None:
        """The data value itself, if it fits in the four bytes available, or a pointer
        to the data if it won't fit, which could be to the beginning of another IFD."""

        return self._data

    @data.setter
    def data(self, data: bytes | bytearray = None):
        if data is None:
            self._data = None
        elif isinstance(data, (bytes, bytearray)):
            self._data = Bytes(data)
        else:
            raise TypeError("The 'data' argument must have a bytes or bytearray value!")

    @property
    def _values(self) -> tuple[Type]:
        pass

    @property
    def subs(self) -> list[IFD]:
        """The 'subs' property returns the list of sub-IFDs associated with the tag."""

        return self._subs

    @property
    def sub(self) -> IFD | None:
        if len(self._subs) > 0:
            return self._subs[0]

    @sub.setter
    def sub(self, sub: IFD) -> IFD:
        """The 'sub' property setter allows a sub-IFD to be associated with the tag."""

        if not isinstance(sub, ifd.IFD):
            raise TypeError("The 'sub' argument must reference an IFD class instance!")

        # sub._label = f"{self.ifd.label}.{len(self._subs)}"

        sub.parent = self

        self._subs.append(sub)

        # sub.chain(self)

        return self

    @property
    def ifd(self) -> IFD | None:
        return self._ifd

    @ifd.setter
    def ifd(self, ifd: IFD):
        from tiffdata.structures.file.ifd import IFD

        if not isinstance(ifd, IFD):
            raise TypeError("The 'ifd' argument must reference an IFD class instance!")

        self._ifd = ifd

    @property
    def hasIFDs(self) -> bool:
        return len(self._subs) > 0

    @Element.length.getter
    def length(self) -> int:
        """Provide an overridden implementation of the length property getter method."""

        if self.tiff.info.format is Format.ClassicTIFF:
            return (
                2  # length of tag identifier field
                + 2  # length of data type field
                + 4  # length of data count field
                + 4  # length of internal data (or offset to external data) field
            )
        elif self.tiff.info.format is Format.BigTIFF:
            return (
                2  # length of tag identifier field
                + 2  # length of data type field
                + 8  # length of data count field
                + 8  # length of internal data (or offset to external data) field
            )
        else:
            raise TIFFDataError(
                "Unsupported TIFF format; must be Classic of Big TIFF only!"
            )

    def size(self, format: Format) -> int:
        """Compute the size in bytes of the Tag as well as any externally stored data
        associated with the tag. The size is computed with reference to the TIFF format
        as this determines whether offsets are stored as 4 byte unsigned longs or as
        8 byte unsigned long longs, as well as affecting the lengths of other fields.

        All IFD Tags comprise the following components:
        +---------------+-------------------------------------------------------------+
        | Tag ID        | Two bytes holding the tag ID                                |
        +---------------+-------------------------------------------------------------+
        | Data Type     | Two bytes holding the data type indicator (see above list)  |
        +---------------+-------------------------------------------------------------+
        | Data Count    | Four bytes holding the count of data values that follow     |
        +---------------+-------------------------------------------------------------+
        | Data / Offset | Four or eight bytes holding the data or offset to the data  |
        +---------------+-------------------------------------------------------------+
        """

        if not isinstance(format, Format):
            raise TypeError(
                "The 'format' argument must reference a Format enumeration class option!"
            )

        size: int = 0

        if format is Format.ClassicTIFF:
            size += 2  # 2 bytes for the UInt16 encoded tag ID

            size += 2  # 2 bytes for the UInt16 encoded tag data type ID

            size += 4  # 4 bytes for the UInt32 encoded tag data value count

            size += 4  # 4 bytes for the UInt32 encoded next Tag offset
        elif format is Format.BigTIFF:
            size += 2  # 2 bytes for the UInt16 encoded tag count

            size += 2  # 2 bytes for the UInt16 encoded tag data type ID

            size += 8  # 4 bytes for the UInt32 encoded tag data value count

            size += 8  # 4 bytes for the UInt32 encoded next Tag offset

        return size

    def external(self, format: Format) -> bool:
        """Determine if the tag must store its data externally based on the size of the
        data and the maxmimum number of bytes available to store data within the tag."""

        if not isinstance(format, Format):
            raise TypeError(
                "The 'format' argument must reference a Format enumeration class option!"
            )

        if format is Format.ClassicTIFF:
            maxdatasize: int = 4
        elif format is Format.BigTIFF:
            maxdatasize: int = 8

        return self.datasize > maxdatasize

    def chain(self, carrier: Element, subs: bool = False) -> Element:
        """Support chaining the current element to the specifed (carrier) element."""

        logger.debug(
            "%s[%s].chain(carrier: %s[%s], subs: %s)"
            % (
                self.klass,
                self.label,
                carrier.klass,
                carrier.label,
                subs,
            )
        )

        if not isinstance(carrier, Element):
            raise TypeError(
                "The 'carrier' argument must reference a Element class instance!"
            )
        elif carrier is self:
            raise ValueError(
                "The 'carrier' argument for %s cannot be a circular reference to itself!"
                % (self)
            )

        if not isinstance(subs, bool):
            raise TypeError("The 'subs' argument must have a boolean value!")

        carrier = super().chain(carrier)

        if subs is True:
            for sub in self.subs:
                carrier = sub.chain(carrier)

        return carrier

    def encode(self, order: ByteOrder = ByteOrder.MSB, format: Format = None) -> bytes:
        logger.debug(f" > {self}.encode(order: {order}, format: {format})")

        if not isinstance(order, ByteOrder):
            raise TypeError(
                "The 'order' argument must reference a ByteOrder enumeration option!"
            )

        if not isinstance(format, Format):
            raise TypeError(
                "The 'format' argument must reference a Format enumeration option!"
            )

        encoded: list[bytes] = []

        idbytes: bytes = self.id.encode(order=order)

        logger.debug(f" > encoded id ({self.id}) to {hexbytes(idbytes)}")

        typebytes: bytes = self.type.encode(order=order)

        logger.debug(f" > encoded type ({self.type}) to {hexbytes(typebytes)}")

        # Assemble the bytes that represent the Tag metadata and data
        encoded.append(idbytes)  # Tag ID, always 2 bytes
        encoded.append(typebytes)  # Data type, always 2 bytes

        if format is Format.ClassicTIFF:
            countbytes: bytes = UInt32(self.count).encode(order=order)
            logger.debug(f" > encoded count ({self.count}) to {hexbytes(countbytes)}")
            encoded.append(countbytes)  # Data count; 4 bytes
        elif format is Format.BigTIFF:
            countbytes: bytes = UInt64(self.count).encode(order=order)
            logger.debug(f" > encoded count ({self.count}) to {hexbytes(countbytes)}")
            encoded.append(countbytes)  # Data count; 8 bytes

        if self.data:
            if format is Format.ClassicTIFF and len(self.data) > 4:
                pass
            elif format is Format.BigTIFF and len(self.data) > 8:
                pass

        # The tag data is stored externally if it is larger than the available space in
        # the tag, which is either 4 bytes for Classic TIFF or 8 bytes of Big TIFF; when
        # the data is stored externally the tag's data field is used to store the offset
        # otherwise, the data is just stored internally in the tag's data field.

        # If the tag has externally stored data (datum), we need to encode its offset
        if isinstance(self.datum, Data):
            offset: bytes = None

            if format is Format.ClassicTIFF:
                offset = UInt32(self.datum.offset.target).encode(order=order)
            elif format is Format.BigTIFF:
                offset = UInt64(self.datum.offset.target).encode(order=order)
            else:
                raise TIFFDataError(
                    f"Unsupported TIFF file format, '{format}', encountered!"
                )

            logger.debug(
                f" > Tag({self.id}#{self.name})[with-datum].encode() offset => {self.datum.offset.target} => {hexbytes(offset)}"
            )

            logger.debug(f" > encoded external data offset to {hexbytes(offset)}")

            encoded.append(offset)  # Pointer/Offset to the data
        else:  # Otherwise, the tag has internally stored data, which is held directly
            # TODO: Consider padding data values that are shorter than necessary
            if format is Format.ClassicTIFF and not (self.data and len(self.data) == 4):
                raise ValueError(
                    "The Tag's embedded data must be 4 bytes long for Classic TIFF files!"
                )
            elif format is Format.BigTIFF and not (self.data and len(self.data) == 8):
                raise ValueError(
                    "The Tag's embedded data must be 8 bytes long for Big TIFF files!"
                )

            logger.debug(f" > encoded data to {hexbytes(self.data)}")

            encoded.append(self.data)  # Data; Four/Eight bytes

        return b"".join(encoded) if encoded else None

    @classmethod
    def decode(
        cls,
        tiff: TIFF,
        handle: io.BufferedReader,
        offset: int,
        format: Format,
        order: ByteOrder,
    ) -> Tag:
        """Parse the raw bytes of an Tag into an Tag data structure."""

        from tiffdata.structures.ifd import IFD

        logger.debug(
            "%s.decode(tiff: %s, handle: %s, offset: %d, order: %s)",
            cls.__name__,
            tiff,
            handle,
            offset,
            order,
        )

        if not isinstance(handle, io.BufferedReader):
            raise TypeError(
                "The 'handle' argument must have an io.BufferedReader value!"
            )

        if not isinstance(offset, int):
            raise TypeError("The 'offset' argument must have an integer value!")

        if not isinstance(format, Format):
            raise TypeError(
                "The 'format' argument must reference a Format enumeration option!"
            )

        if not isinstance(order, ByteOrder):
            raise TypeError(
                "The 'order' argument must reference a ByteOrder enumeration option!"
            )

        attributes: Attributes = Attributes(raw=Attributes())

        handle.seek(offset)

        attributes.offset: int = offset

        if tiff.format is Format.ClassicTIFF:
            countsize: int = 4
            datasize: int = 4
        elif tiff.format is Format.BigTIFF:
            countsize: int = 8
            datasize: int = 8

        # logger.debug(" > tell => %s" % (handle.tell()))

        # The IFD Tag ID always occupies 2 bytes in both Classic and Big TIFF formats
        attributes.raw.id = rawid = handle.read(2)

        # logger.debug(" > read => %s" % (hexbytes(rawid)))
        # logger.debug(" > tell => %s" % (handle.tell()))

        # Decode the raw Tag ID into an unsigned integer
        attributes.id = id = UInt16.decode(value=rawid, order=tiff.byteorder)

        debug: bool = False or (
            id
            in [
                256,  # ImageWidth
                271,  # Camera Make
            ]
        )

        if debug:
            logger.debug(
                " > count size => %s (bytes reserved for count in a tag)" % (countsize)
            )
            logger.debug(
                " > data size => %s (bytes reserved for data in a tag)" % (datasize)
            )

        if (tag := TIFFTag.reconcile(id)) is None:
            logger.warning(f"Unable to reconcile Tag ID, '{id}', to Tag enumeration!")

            raise TIFFDataParseError(
                f"Unable to reconcile Tag ID, '{id}', to Tag enumeration, expected {TIFFTag}, found {builtins.type(tag)}!"
            )

        attributes.tag = tag

        attributes.name = tag.name if tag else None

        if debug:
            logger.debug(" > id => %s (%s)" % (id, tag.name if tag else None))
            logger.debug(" > tell => %s" % (handle.tell()))

        attributes.raw.type = rawtype = handle.read(2)

        if debug:
            logger.debug(" > type (raw) => %s" % (hexbytes(rawtype)))

        # The data type field occupies 2 bytes in both the Classic and Big TIFF formats
        type: UInt16 = UInt16.decode(value=rawtype, order=tiff.byteorder)

        if not isinstance(datatype := DataType.reconcile(type), DataType):
            logger.warning(
                f"Unable to reconcile Tag data type, '{type}', to DataType enumeration!"
            )

            # TODO: Should this always raise an exception, or be configurable?
            raise TIFFDataParseError(
                f"Unable to reconcile Tag data type, '{type}', to DataType enumeration!"
            )

        if debug:
            logger.debug(
                " > tag: %s (%s), type: %s" % (tag, builtins.type(tag.type), tag.type)
            )

        if len(tag.types) >= 1 and not datatype in tag.types:
            logger.info(
                "The '%s' tag reports that its data is encoded as %s which does not match the expected %s datatype(s)!",
                tag.name,
                datatype,
                tag.types,
            )

            datatype = tag.types[0]

        attributes.type: DataType = datatype

        if debug:
            logger.debug(
                " > type => %s (%s, %s bytes, %s bits)"
                % (type, datatype.name, int(datatype.size / 8), datatype.size)
            )
            logger.debug(" > tell => %s" % (handle.tell()))

        attributes.raw.count = rawcount = handle.read(countsize)

        if debug:
            logger.debug(" > read => %s" % (hexbytes(rawcount)))
            logger.debug(" > tell => %s" % (handle.tell()))

        attributes.count = count = UInt32.decode(value=rawcount, order=tiff.byteorder)

        if debug:
            logger.debug(" > count => %s" % (count))

        # Calculate the data length based on the tag count and tag data type byte size
        attributes.length = length = (
            (count * int(datatype.size / 8)) if datatype else count
        )

        if debug:
            logger.debug(" > length => %s bytes" % (length))

        attributes.raw.data = rawdata = handle.read(datasize)

        if debug:
            logger.debug(" > data (tag, order) => %s" % (tiff.byteorder))
            logger.debug(" > data (tag, raw) => %s" % (hexbytes(rawdata)))

        # We hold the raw data in data
        data: Bytes = Bytes.decode(value=rawdata, order=None)

        if debug:
            logger.debug(" > data (tag) => %s" % (hexbytes(data)))

        # If the calculated length is greater than the data length supported by the tag
        # this means that the data is not held in the tag, but rather elsewhere in the
        # image with the offset being held in the tag's data; that is if data is small
        # enough to be stored directly in the tag it will be, otherwise, its stored in
        # image elsewhere with the tag's data value being used to hold the offset:
        if length > datasize:
            if tiff.format is Format.ClassicTIFF:
                offset: UInt32 = UInt32.decode(value=data, order=tiff.byteorder)
            elif tiff.format is Format.BigTIFF:
                offset: UInt64 = UInt64.decode(value=data, order=tiff.byteorder)

            if debug:
                logger.debug(" > offset (len>ds) (tag) => %s" % (offset))

            currentoffset: int = handle.tell()
            handle.seek(offset)
            rawdata: bytes = handle.read(length)
            data: Bytes = Bytes.decode(value=rawdata, order=None)  # , order=order)
            handle.seek(currentoffset)

            if debug:
                logger.debug(" > data (new) => %s" % (hexbytes(data, limit=20)))

        attributes.raw.data = rawdata  # data will be in the file's endianness when read
        attributes.data = data  # data will always be in msb order after Bytes.decode()

        if debug:
            logger.debug(" > tell   => %s" % (handle.tell()))
            logger.debug(" > offset => %s" % (offset))

        attributes.subs: list[IFD] = []

        if datatype and isinstance(klass := datatype.type, builtins.type):
            # number of bytes that should have been encoded for the type
            typesize: int = int(datatype.size / 8)

            values: list[object] = []

            if datatype in (DataType.ASCII, DataType.Byte, DataType.Undefined):
                typesize = len(data)

            view: BytesView = BytesView(
                data=data,
                order=tiff.byteorder,
                split=typesize,
            )

            # Iterate over the tag's data slicing the data up into sections based on the
            # number of bytes needed for the current data type (typesize):
            # for index, valdata in enumerate(
            #     [data[i : i + typesize] for i in range(0, len(data), typesize)], start=1
            # ):

            # logger.debug(" > typesize => %s / %s / %s" % (typesize, len(data), len(view)))

            for index, valdata in enumerate(view, start=1):
                if debug:
                    logger.debug(
                        " > view[%d]  => %s / %s / %s / %s"
                        % (
                            index,
                            builtins.type(valdata),
                            klass,
                            tiff.byteorder,
                            hexbytes(valdata),
                        )
                    )

                if len(valdata) != typesize:
                    logger.error(
                        f"The value is the wrong length; must be {typesize}, but is: {len(valdata)}!"
                    )

                # NOTE: That although ASCII strings are composed of one or more bytes, as they are comprised of
                # individual single byte values, endianness does not apply to the individual bytes, unlike say a
                # multi-byte Unicode string such as UTF-16, where those multi-byte sequences could be stored in
                # big or little endian order; as such when we decode ASCII strings held in TIFF/EXIF tags, we can
                # expect the bytes to be in the correct spelling order regardless of the endianness of the file!

                if datatype is DataType.ASCII:
                    # NOTE: The null-byte terminator (b'\x00') needs to be removed before decoding and it needs
                    # to be added back to any ASCII strings when saved so that they are correctly terminated:
                    valdata = valdata.rstrip(b"\00")

                    # Note: We do not specify the byte order when decoding ASCII as it
                    # is a sequence of individual bytes unaffected by byte order:
                    decoded = klass.decode(value=bytes(valdata))
                else:
                    decoded = klass.decode(value=bytes(valdata), order=tiff.byteorder)

                # logger.debug(">" * 100)

                if debug:
                    logger.debug(" > value[%d] => %s" % (index, hexbytes(valdata)))
                    logger.debug(" > decoded   => %s" % (decoded))

                values.append(decoded)

                # As an Tag can hold either 4 or 8 bytes of data, there could be padding, which we skip if we
                # have already read and decoded (noted by index) the expected number of values (noted by count)
                if len(values) == count:
                    break

            if debug:
                logger.debug(
                    " > values => %s %s"
                    % (
                        values if len(values) <= 20 else values[0:20],
                        tag.get("unit", "") if tag else "",
                    )
                )

            attributes.values = values

            if tag.isIFD is True:
                if debug:
                    logger.debug(" >>> this tag is an IFD")

                for suboffset in values:
                    if not isinstance(suboffset, int):
                        raise TypeError("The 'suboffset' value must be an integer!")

                    if debug:
                        logger.debug(f"  >>> offset (sub IFD offset) >>> {suboffset}")

                    while suboffset > 0:
                        if debug:
                            logger.debug(f"  >>> offset (current) >>> {suboffset}")

                        if isinstance(
                            ifd := tiff._parse_ifd(
                                handle=handle,
                                offset=suboffset,
                            ),
                            IFD,
                        ):
                            attributes.subs.append(ifd)

                            if (suboffset := ifd.next) == 0:
                                break
                        else:
                            break

        return Tag(**attributes)

    @classmethod
    def _decode(
        cls,
        value: bytes,
        order: ByteOrder,
        format: Format,
    ) -> Tag:
        if not isinstance(value, bytes):
            raise TypeError("The 'value' argument must have a bytes value!")

        if not isinstance(order, ByteOrder):
            raise TypeError(
                "The 'order' argument must reference a ByteOrder enumeration option!"
            )

        id: UInt16 = UInt16.decode(value=value[0:2], order=order)

        type: UInt16 = UInt16.decode(value=value[2:4], order=order)

        count: UInt32 = UInt32.decode(value=value[4:8], order=order)

        type: DataType = DataType.reconcile(type)

        length: int = count * type.value.size

        if format is Format.ClassicTIFF:
            data: Bytes = Bytes32.decode(value=value[8:length], order=order)
        elif format is Format.BigTIFF:
            data: Bytes = Bytes64.decode(value=value[8:length], order=order)

        return Tag(id=id, type=type.value, count=count, data=data)
