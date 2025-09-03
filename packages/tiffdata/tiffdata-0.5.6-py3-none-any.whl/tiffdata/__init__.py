from __future__ import annotations

from tiffdata.logging import logger

from tiffdata.enumerations import (
    Format,
    DataType,
    TIFFTag,
)

from tiffdata.exceptions import (
    TIFFDataFileError,
    TIFFDataFileFormatError,
    TIFFDataError,
    TIFFDataReadError,
    TIFFDataParseError,
    TIFFDataWriteError,
)

from tiffdata.structures import (
    Attributes,
    Information,
    Offset,
    Element,
    Container,
    IFD,
    IFDNext,
    Tag,
    Data,
    Strip,
    Tile,
)

from deliciousbytes import (
    ByteOrder,
    UInt,
    UInt16,
    UInt32,
    UInt64,
    Bytes,
    BytesView,
)

from deliciousbytes.utilities import hexbytes

import os
import io
import typing
import builtins
import tempfile
import time

logger = logger.getChild(__name__)


class TIFF(object):
    """The TIFF class represents TIFF format files and their raw data."""

    _filehandle: object = None
    _info: Information = None
    _prolog: bytes = None
    _container: Container = None
    _ifds: list[IFD] = None

    def __new__(cls, filepath: str, **kwargs) -> TIFF:
        """Handle creating new instances of the TIFF class, which based on the format of
        the TIFF file, will result in the creation of a ClassicTIFF or BigTIFF subclass
        instance. Thiis is achived by parsing the first four header bytes of the file,
        from which the byte order and file format can be determined; this information is
        then used to determine which TIFF subclass to create an instance of."""

        logger.debug(
            "%s.__new__(cls: %s, filepath: %s, kwargs: %s)",
            cls.__name__,
            cls,
            filepath,
            kwargs,
        )

        if not isinstance(filepath, str):
            raise TypeError("The 'filepath' argument must have a string value!")
        elif not len(filepath := filepath.strip()) > 0:
            raise ValueError("The 'filepath' argument must be a non-empty string!")
        elif not os.path.exists(filepath):
            raise TIFFDataFileError(
                "The 'filepath' argument must reference a file that exists!"
            )
        elif not os.path.isfile(filepath):
            raise TIFFDataFileError(
                "The 'filepath' argument must reference a file, not another filesystem object like a directory!"
            )

        tiffclass: TIFF = cls

        if cls is TIFF:
            # Parse the first few header bytes to determine the TIFF file format
            if isinstance(info := cls._parse_header(filepath, new=True), Information):
                # Based on the format, create the appropriate subclass instance
                if info.format is Format.ClassicTIFF:
                    tiffclass = ClassicTIFF
                elif info.format is Format.BigTIFF:
                    tiffclass = BigTIFF
                else:
                    raise TIFFDataParseError(
                        f"The specified file, '{filepath}', is not a valid TIFF file!"
                    )
            else:
                raise TIFFDataParseError(
                    f"The specified file, '{filepath}', is not a valid TIFF file!"
                )

        return super().__new__(tiffclass)

    def __init__(self, filepath: str, **kwargs):
        """Handle initialising the TIFF class."""

        logger.debug(
            "%s.__init__(self: %s, filepath: %s, kwargs: %s)",
            self.__class__.__name__,
            self,
            filepath,
            kwargs,
        )

        if isinstance(info := self._parse_header(filepath), Information):
            self._info = info
        else:
            raise TIFFDataParseError(
                f"The specified file, '{filepath}', is not a valid TIFF file!"
            )

        self._ifds: list[IFD] = []

        self._parse()

    def __del__(self):
        """The __del__() method is called when the current instance is manually deleted
        or when the garbage collector automatically removes it from memory once all the
        references have gone out of scope. We can take advantage of this to do perform
        clean-up, which may not have been performed manually, such as closing files."""

        logger.debug("%s.__del__()", self.__class__.__name__)

        self._close()

    def __enter__(self):
        """Support use of the TIFF class via the 'with' context manager."""

        logger.debug("%s.__enter__()", self.__class__.__name__)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Support use of the TIFF class via the 'with' context manager."""

        logger.debug("%s.__exit__()", self.__class__.__name__)

        self._close()

    def __len__(self) -> int:
        """Return the number of IFDs held within the current TIFF file."""

        length: int = 0

        for index, ifd in enumerate(self.ifds, start=1):
            length += 1

            if len(ifd.subs) > 0:
                for subindex, subifd in enumerate(ifd.subs, start=(index + 1)):
                    length += 1

        return length

    def __iter__(self) -> typing.Generator[IFD, None, None]:
        """The __iter__() method provides a generator that iterates through the IFDs in
        the current TIFF file, including any sub or nested IFDs, yielding each one."""

        for index, ifd in enumerate(self._ifds, start=1):
            ifd.index = index

            yield ifd

            for tag in ifd:
                if tag.tag.isIFD is True and len(tag.subs) > 0:
                    for subindex, subifd in enumerate(tag.subs, start=(index + 1)):
                        subifd.index = subindex
                        yield subifd

            if len(ifd.subs) > 0:
                for subindex, subifd in enumerate(ifd.subs, start=(index + 1)):
                    subifd.index = subindex
                    yield subifd

    def __getattr__(self, name: str) -> object | None:
        """Support for obtaining TIFF tag values as class attributes."""

        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")

        for ifd in self:
            for tag in ifd:
                if tag.name.lower() == name.lower():
                    if isinstance(tag.values, list) and len(tag.values) == 1:
                        return tag.values[0]
                    else:
                        return tag.values

    def __setattr__(self, name: str, value: object):
        if name.startswith("_"):
            return super().__setattr__(name, value)
        else:
            return self.set(key=name, value=value)

    @classmethod
    def _parse_header(cls, filepath: str, new: bool = False) -> Information:
        """Parse the header of the file to determine if it is a valid TIFF image."""

        if not isinstance(filepath, str):
            raise TypeError("The 'filepath' argument must have a string value!")
        elif not os.path.exists(filepath):
            raise ValueError(
                "The 'filepath' argument must reference a file that exists!"
            )

        info = Information()

        with open(filepath, "rb") as handle:
            # Store the file path for reference
            info.filepath = filepath

            # Determine the size of the file
            handle.seek(0, os.SEEK_END)  # Seek to last byte (0) from the end
            info.filesize = handle.tell()  # Record the current position – the file size
            handle.seek(0, os.SEEK_SET)  # Seek to the first byte (0) from the start

            # Determine the byte order from the first two bytes of the file
            if isinstance(
                order := cls._parse_byteorder(header=handle.read(2)),
                ByteOrder,
            ):
                info.order = order
            else:
                raise TIFFDataFileFormatError(
                    f"The specified file, '{filepath}', is not a valid TIFF file - invalid byte order marker!"
                )

            # Determine the format – Classic TIFF or Big TIFF from the next two bytes
            if isinstance(
                format := cls._parse_format(header=handle.read(2), order=order),
                Format,
            ):
                info.format = format
            else:
                raise TIFFDataFileFormatError(
                    f"The specified file, '{filepath}', is not a valid TIFF file – invalid format marker!"
                )

            # If parsing the header for a new instance, return gathered information as
            # we have enough information (path, size, byte order and format) to proceed
            if new is True:
                return info

            # Determine the offset of the first (0th) Image File Directory (IFD)
            if format is Format.ClassicTIFF:
                # For Classic TIFF files, the IFD0 offset must be the stored in the
                # following four bytes, encoded as a 4-byte, 32-bit unsigned integer:
                if (
                    isinstance(
                        offset := UInt32.decode(
                            value=handle.read(4),
                            order=info.order,
                        ),
                        UInt32,
                    )
                    and offset >= 8
                ):  # The first IFD offset must begin after the header
                    info.offset = offset
                else:
                    raise TIFFDataFileFormatError(
                        "The specified file, '{self.filepath}', is not a valid Classic TIFF file; invalid IFD0 offset!"
                    )
            elif format is Format.BigTIFF:
                # All Big TIFF files must contain an unsigned 16 bit integer noting the
                # size of the first IFD offset field, which for Big TIFF, must be 8
                if not UInt16.decode(value=handle.read(2), order=info.order) == 8:
                    raise TIFFDataFileFormatError(
                        "The specified file, '{self.filepath}', is not a valid Big TIFF file; invalid offset byte size!"
                    )

                # All Big TIFF files must contain an unsigned 16 bit integer, reserved
                # for future use; for Big TIFF, the decoded value must be zero (0)
                if not UInt16.decode(value=handle.read(2), order=info.order) == 0:
                    raise TIFFDataFileFormatError(
                        "The specified file, '{self.filepath}', is not a valid Big TIFF file; invalid reserved value!"
                    )

                # The IFD0 offset should then be present as a 8-byte, 64-bit unsigned integer
                if (
                    isinstance(
                        offset := UInt64.decode(
                            value=handle.read(8),
                            order=info.order,
                        ),
                        UInt64,
                    )
                    and offset >= 16
                ):  # The first IFD offset must begin after the header
                    info.offset = offset
                else:
                    raise TIFFDataFileFormatError(
                        "The specified file, '{self.filepath}', is not a valid TIFF file; invalid IFD0 offset!"
                    )

        return info

    @classmethod
    def _parse_byteorder(cls, header: bytes) -> ByteOrder | None:
        """Parse the file's byte order from the first two bytes of the header."""

        if not isinstance(header, bytes):
            raise TypeError("The 'header' argument must have a bytes value!")
        elif not len(header) == 2:
            raise TypeError("The 'header' argument must have a length of two bytes!")

        if header == b"MM":
            return ByteOrder.MSB  # Motorolla (most-significant bit first)
        elif header == b"II":
            return ByteOrder.LSB  # Intel (least-significant bit first)

        raise TIFFDataParseError(
            f"The TIFF file header byte order mark, {hexbytes(header)}, is invalid!!"
        )

    @classmethod
    def _parse_format(cls, header: bytes, order: ByteOrder) -> Format | None:
        """Parse the file's format marker to determine if the specified file is a valid
        TIFF file, and if so, the file format (Classic or Big), and its endianness."""

        if not isinstance(header, bytes):
            raise TypeError("The 'header' argument must have a bytes value!")
        elif not len(header) == 2:
            raise TypeError("The 'header' argument must have a length of two bytes!")

        if not isinstance(order, ByteOrder):
            raise TypeError(
                "The 'order' argument must reference a ByteOrder enumeration option!"
            )

        if order is ByteOrder.MSB:
            if header == b"\x00\x2a":  # 42
                return Format.ClassicTIFF
            elif header == b"\x00\x2b":  # 43
                return Format.BigTIFF
        elif order is ByteOrder.LSB:
            if header == b"\x2a\x00":  # 42
                return Format.ClassicTIFF
            elif header == b"\x2b\x00":  # 43
                return Format.BigTIFF

        raise TIFFDataParseError(
            f"The TIFF file header format marker, {hexbytes(header)}, is invalid!!"
        )

    def _open(self) -> io.BufferedReader:
        """Open the TIFF file handle."""

        logger.debug(
            "%s._open() filepath => %s",
            self.__class__.__name__,
            self.filepath,
        )

        if not self._filehandle is None:
            return self._filehandle

        self._filehandle = open(self.filepath, "rb")

        return self._filehandle

    def _handle(self) -> io.BufferedReader:
        """Return the TIFF file handle."""

        if self._filehandle is None:
            self._open()

        return self._filehandle

    def _close(self):
        """Close the TIFF file handle."""

        logger.debug(
            "%s._close() filepath => %s" % (self.__class__.__name__, self.filepath),
        )

        if not self._filehandle is None:
            self._filehandle.close()
            self._filehandle = None

    def _parse(self):
        """Parse the TIFF file's metadata starting from the offset of the first (0th)
        Image File Directory (IFD). We then follow the offsets within the IFD and its
        Tags to access other data in the file, which may include additional IFDs and
        their Tags, as well as the image bitmap data itself which will be held either
        in "strips" or "tiles" as per the TIFF file format specification. The offsets
        and lengths of the image bitmap strips and tiles are recorded in IFD Tags and
        the just like the data for an IFD or Tag, the image data can be held anywhere
        within the file, reached via its absolute offset.

        All IFDs comprise the following components:
        +-------------+---------------------------------------------------------------+
        | Tag Count   | Two or eight bytes holding the count of tags that follow;     |
        |             | Classic TIFF uses 2 bytes, Big TIFF uses 8 bytes for counts   |
        +-------------+---------------------------------------------------------------+
        | Tags        | One or more byte-encoded IFD Tag values, the length of        |
        |             | which can be determined by multiplying the tag count by 12    |
        |             | for Classic TIFF files and by 20 for Big TIFF files           |
        +-------------+---------------------------------------------------------------+
        | Next Offset | Four or eight bytes for offset to the next IFD; offsets are   |
        |             | always absolute, never relative, and can point to a location  |
        |             | anywhere in the file; the last IFD must have an offset of 0;  |
        |             | Classic TIFF uses 4 bytes, Big TIFF uses 8 bytes for offsets  |
        +-------------+---------------------------------------------------------------+
        """

        logger.debug(
            "%s._parse() byte order => %s; file format => %s; offset => %d",
            self.__class__.__name__,
            self.info.order,
            self.info.format,
            self.info.offset,
        )

        handle = self._handle()  # Obtain the file handle

        # Prolog captures the magic header bytes of the file, and is made available for
        # reference via the TIFF class' 'prolog' (bytes) property
        self._prolog: bytes = handle.read(16 if self.format is Format.BigTIFF else 8)

        logger.debug(
            "> prolog (length: %d) => %s", len(self._prolog), hexbytes(self._prolog)
        )

        # Create the root TIFF container once the byte order and file format are known
        self._container = Container(
            order=self.info.order,
            format=self.info.format,
            first=Offset(
                source=self.info.offset,
                # The target offset for the first IFD is immediately after the header
                # which is 16 bytes in Big TIFF files and 8 bytes in Classic TIFF files
                target=(16 if self.format is Format.BigTIFF else 8),
            ),
        )

        # Seek to the offset of the first Image File Directory (IFD)
        handle.seek(self.info.offset)

        # Ensure that the handle's current position matches the expected IFD0 offset
        if not (handle.tell() == self.info.offset):
            raise TIFFDataParseError(
                f"Unable to seek to the offset, {self.info.offset}, for the IFD!"
            )

        # Placeholder for a reference to an IFD instance as it is parsed
        ifd: IFD = None

        # Starting with the offset of the first IFD, parse the first IFD and follow any
        # offsets it provides to possible additional IFDs held within the file, which
        # may include IFDs that are nested within the current IFD under one of its Tags:
        while isinstance(
            ifd := self._parse_ifd(
                offset=(ifd.next if ifd and ifd.next >= 0 else self.info.first),
            ),
            IFD,
        ):
            # Append the IFD to the list of IFDs
            self._ifds.append(ifd)

            # Label the IFD
            ifd.label = f"#{(len(self._ifds) - 1)}"  # IFD labelling starts at 0

            logger.debug("@" * 100)
            logger.debug(
                "Found %s => next offset => %s (%s)",
                ifd,
                ifd.next,
                ifd.nextoffset,
            )
            logger.debug("@" * 100)

            # If there are no further IFDs, as indicated by a 'next' offset of zero (0),
            # then break out of the loop as there are no more IFDs to find:
            if ifd.next == 0:
                break

        logger.debug("Found %d IFDs", len(self._ifds))

        # Build the linked-list between the elements, chaining them together
        self._structure()

    def _parse_ifd(
        self,
        offset: UInt64,
        carrier: Element = None,
    ) -> IFD | None:
        logger.debug("%s._parse_ifd(offset: %s)", self.__class__.__name__, offset)

        if offset == 0:
            return

        handle = self._handle()  # Obtain the file handle

        # Seek to the IFD's starting offset and ensure that the seek was successful
        if not handle.seek(offset) == offset:
            raise TIFFDataParseError(
                f"Unable to seek to the offset, {offset}, for the IFD @ {offset}!"
            )

        # Obtain the count of the tags held in the IFD
        if self.format is Format.ClassicTIFF:
            # For Classic TIFF, the tag count is held in a 2-byte, 16-bit unsigned integer (UInt16)
            if not (
                isinstance(
                    count := UInt16.decode(value=handle.read(2), order=self.order),
                    UInt16,
                )
                and count >= 1
            ):
                raise TIFFDataParseError(
                    f"Unable to parse the tag count for the IFD @ {offset}!"
                )
        elif self.format is Format.BigTIFF:
            # For Big TIFF, the tag count is held in an 8-byte, 64-bit unsigned integer (UInt64)
            if not (
                isinstance(
                    count := UInt64.decode(value=handle.read(8), order=self.order),
                    UInt64,
                )
                and count >= 1
            ):
                raise TIFFDataParseError(
                    f"Unable to parse the tag count for the IFD @ {offset}!"
                )

        logger.debug(" > IFD Tag count => %d", count)

        tagoffset: int = handle.tell()

        taglength: int = 0

        if self.format is Format.ClassicTIFF:
            taglength = 12
        elif self.format is Format.BigTIFF:
            taglength = 20

        # Create the IFD class instance to represent the IFD
        ifd = IFD(offset=offset, count=count, carrier=carrier, tiff=self)

        # Iterate through the count of tags, attempting to parse each one, starting at
        # the current file offset, and incrementing the offset by the fixed length of
        # each tag (either 12 bytes for Classic TIFF or 20 bytes for Big TIFF) as the
        # loop iterates, and add each parsed tag to the IFD for later use:
        for index in range(count):
            logger.debug(
                (">" * 50) + " • %02d/%02d • " % (index + 1, count) + ("<" * 50)
            )

            if not isinstance(tag := self._parse_ifd_tag(offset=tagoffset), Tag):
                logger.warning(
                    "Could not parse Tag %d of %d; the Tag will be omitted!",
                    index,
                    count,
                )
                continue

            logger.debug(
                " > %02d/%02d => %05s => Tag(id: %s (%s), type: %s, count: %s, length: %s, data: %s, values: %s)"
                % (
                    (index + 1),
                    tag.count,
                    tag.offset,
                    tag.id,
                    (tag.tag.name if tag.tag else "?"),
                    tag.type,
                    tag.count,
                    tag.datasize,
                    hexbytes(tag.data, limit=20) if tag.data else "?",
                    tag.values,
                )
            )

            ifd.tag = tag

            tagoffset += taglength

        ifd.nextoffset = handle.tell()

        logger.debug(f" >>> {ifd}.next (handle offset) => {ifd.nextoffset}")

        if self.format is Format.ClassicTIFF:
            ifd.next: UInt32 = UInt32.decode(value=handle.read(4), order=self.order)
        elif self.format is Format.BigTIFF:
            ifd.next: UInt64 = UInt64.decode(value=handle.read(8), order=self.order)

        logger.debug(f" >>> {ifd}.next (offset) => {ifd.next}")

        self._parse_image_data(ifd=ifd)

        return ifd

    def _parse_ifd_tag(self, offset: int) -> Attributes | None:
        """Parse the raw bytes of an Tag into an Tag data structure."""

        logger.debug(
            "%s._parse_ifd_tag(offset: %d)"
            % (
                self.__class__.__name__,
                offset,
            )
        )

        handle = self._handle()  # Obtain the file handle

        # Seek to the Tag's starting offset and ensure that the seek was successful
        if not handle.seek(offset) == offset:
            raise TIFFDataParseError(
                f"Unable to seek to the offset, {offset}, for the IFD @ {offset}!"
            )

        # Create an Attributes instance to hold additional attributes about the tag
        attributes: Attributes = Attributes(raw=Attributes())

        attributes.offset = offset

        if self.format is Format.ClassicTIFF:
            countsize: int = 4
            datasize: int = 4
        elif self.format is Format.BigTIFF:
            countsize: int = 8
            datasize: int = 8

        logger.debug(
            " > count size => %s (bytes reserved for count in a tag)" % (countsize)
        )

        logger.debug(
            " > data size => %s (bytes reserved for data in a tag)" % (datasize)
        )

        logger.debug(" > tell => %s" % (handle.tell()))

        # The IFD Tag ID always occupies 2 bytes in both Classic and Big TIFF formats
        attributes.raw.id = rawid = handle.read(2)

        logger.debug(" > id (raw) => %s (%d)" % (hexbytes(rawid), len(rawid)))
        logger.debug(" > tell => %s" % (handle.tell()))

        # Decode the raw Tag ID into an unsigned 16-bit integer
        attributes.id = id = UInt16.decode(value=rawid, order=self.order)

        # Attempt to reconcile the Tag ID to a TIFFTag enumeration option
        if not (tifftag := TIFFTag.reconcile(id)):
            logger.warning(
                f"Unable to reconcile Tag ID, '{id}', to a TIFFTag enumeration option!"
            )

            # TODO: Should this always raise an exception, or be configurable?
            raise TIFFDataParseError(
                f"Unable to reconcile Tag ID, '{id}', to a TIFFTag enumeration option!"
            )

        attributes.tag = tifftag

        attributes.name = tifftag.name

        logger.debug(" > id => %s (%s)" % (id, tifftag.name if tifftag else None))
        logger.debug(" > tell => %s" % (handle.tell()))

        attributes.raw.type = rawtype = handle.read(2)

        logger.debug(" > type (raw) => %s (%d)" % (hexbytes(rawtype), len(rawtype)))

        # The data type ID always occupies 2 bytes in both Classic and Big TIFF formats
        type: UInt16 = UInt16.decode(value=rawtype, order=self.order)

        logger.debug(" > type (decoded) => %s" % (type))

        # Attempt to reconcile the data type ID to a DataType enumeration option
        if not isinstance(datatype := DataType.reconcile(type), DataType):
            logger.warning(
                f"Unable to reconcile Tag data type ID, '{type}', to a DataType enumeration option!"
            )

            # TODO: Should this always raise an exception, or be configurable?
            raise TIFFDataParseError(
                f"Unable to reconcile Tag data type ID, '{type}', to a DataType enumeration option!"
            )

        # logger.debug(" > tag: %s (%s), type: %s" % (tifftag, builtins.type(tifftag.type), tifftag.type))
        logger.debug(
            " > type (reconciled) => %s, %s, %s, %s"
            % (datatype, datatype.size, datatype.type, datatype.description)
        )
        logger.debug(" > tag: %s", tifftag)

        # Check that the data type reported by the tag matches an expected data type (if any have been specified)
        if len(tifftag.types) >= 1 and not datatype in tifftag.types:
            logger.info(
                "The '%s' tag reports that its data is encoded as '%s' which does not match the expected '%s' datatype(s)!",
                tifftag.name,
                datatype,
                tifftag.types,
            )

            # TODO: Determine if it is appropriate to override the data type for a tag
            # if the tag's data type does not match any of the expected data types?
            # datatype = tifftag.types[0]

        attributes.type: DataType = datatype

        logger.debug(
            " > type => %s (%s, %s bytes, %s bits)",
            type,
            datatype.name,
            int(datatype.size / 8),
            datatype.size,
        )

        logger.debug(" > tell => %s", handle.tell())

        attributes.raw.count = rawcount = handle.read(countsize)

        logger.debug(" > read => %s", hexbytes(rawcount))
        logger.debug(" > tell => %s", handle.tell())

        count: int = 0

        # Decode the tag value count; stored as a 4 byte, 32 bit unsigned integer for
        # Classic TIFF files, and as an 8 byte, 64 bit unsigned integer for Big TIFF
        if self.format is Format.ClassicTIFF:
            attributes.count = count = UInt32.decode(value=rawcount, order=self.order)
        elif self.format is Format.BigTIFF:
            attributes.count = count = UInt64.decode(value=rawcount, order=self.order)

        logger.debug(" > count  => %s" % (count))
        logger.debug(" > %02d/8 => %s" % (datatype.size, int(datatype.size / 8)))

        # Calculate the data size based on the tag count and tag data type byte size
        attributes.datasize = count * int(datatype.size / 8)

        logger.debug(" > datasize => %s bytes" % (attributes.datasize))

        # Read the raw data bytes from the tag; the data is stored in 4 bytes within
        # Classic TIFF files and 8 bytes for Big TIFF files
        attributes.raw.data = rawdata = handle.read(datasize)

        logger.debug(" > data (tag, order) => %s", self.order)
        logger.debug(" > data (tag, raw) => %s", hexbytes(rawdata))

        # Hold the raw data within a Bytes class instance
        data: Bytes = Bytes.decode(value=rawdata, order=None)

        logger.debug(" > data (tag) => %s", hexbytes(data))

        dataoffset: int = 0
        dataextern: bool = False

        # If the calculated data size is greater than the data size supported by the tag
        # this means that the data is not held in the tag, but rather elsewhere in the
        # image with the offset being held in the tag's data; that is if data is small
        # enough to be stored directly in the tag it will be, otherwise, its stored in
        # the image elsewhere, with the tag's data value being used to hold the offset:
        if attributes.datasize > datasize:
            dataextern = True

            if self.format is Format.ClassicTIFF:
                dataoffset: UInt32 = UInt32.decode(value=data, order=self.order)
            elif self.format is Format.BigTIFF:
                dataoffset: UInt64 = UInt64.decode(value=data, order=self.order)

            logger.debug(" > offset (len>ds) (tag) => %s", dataoffset)

            currentoffset: int = handle.tell()
            handle.seek(dataoffset)
            rawdata: bytes = handle.read(attributes.datasize)
            data: Bytes = Bytes.decode(value=rawdata, order=None)
            handle.seek(currentoffset)

            logger.debug(" > data (new) => %s", hexbytes(data, limit=80))

        attributes.raw.data = rawdata  # data will be in the file's endianness when read
        attributes.data = data  # data will always be in msb order after Bytes.decode()
        attributes.dataoffset = dataoffset  # offset of tag's data (0 for internal data)

        tag = Tag(
            tiff=self,
            # offset=attributes.offset,
            # id=id,
            # type=datatype,
            # count=count,
            # data=data,
            **attributes,
        )

        if dataextern is True:
            tag.datum = Data(
                offset=Offset(source=dataoffset),
                length=len(data),
                data=rawdata,
            )

        logger.debug(" > offset => %s", offset)
        logger.debug(" > tell   => %s", handle.tell())

        attributes.subs: list[IFD] = []

        if datatype and isinstance(klass := datatype.type, builtins.type):
            # number of bytes that should have been encoded for the type
            typesize: int = int(datatype.size / 8)

            values: list[object] = []

            if datatype in (DataType.ASCII, DataType.Byte, DataType.Undefined):
                typesize = len(data)

            view: BytesView = BytesView(
                data=data,
                order=self.order,
                split=typesize,
            )

            for index, valdata in enumerate(view, start=1):
                logger.debug(
                    " > view[%d]  => %s / %s / %s / %s",
                    index,
                    builtins.type(valdata),
                    klass,
                    self.order,
                    hexbytes(valdata),
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
                    logger.debug(
                        " > klass => %s, value => %s, order => %s",
                        klass,
                        hexbytes(bytes(valdata)),
                        self.order,
                    )
                    decoded = klass.decode(value=bytes(valdata), order=self.order)

                # logger.debug(">" * 100)

                logger.debug(" > value[%d] => %s", index, hexbytes(valdata))
                logger.debug(" > decoded   => %s", decoded)

                values.append(decoded)

                # As an Tag can hold either 4 or 8 bytes of data, there could be padding, which we skip if we
                # have already read and decoded (noted by index) the expected number of values (noted by count)
                if len(values) == count:
                    break

            logger.debug(
                " > values => %s %s",
                values if len(values) <= 20 else values[0:20],
                tifftag.get("unit", "") if tifftag else "",
            )

            tag.values = values

            if tag.tag.isIFD is True:
                logger.debug("*" * 100)
                logger.debug(" >>> Found sub IFD: %s => %s", tifftag, values)

                # Record the current file handle position to return to after parsing the
                # sub IFD which could be anywhere in the file
                position: int = handle.tell()

                for suboffset in values:
                    if not isinstance(suboffset, int):
                        raise TypeError("The 'suboffset' value must be an integer!")

                    logger.debug(f" >>> offset (sub IFD offset) >>> {suboffset}")

                    while suboffset > 0:
                        logger.debug(f" >>> offset (current) >>> {suboffset}")

                        if isinstance(
                            ifd := self._parse_ifd(offset=suboffset, carrier=tag),
                            IFD,
                        ):
                            tag.sub = ifd

                            for t in ifd:
                                logger.debug(
                                    " >>> Found Tag: %s, %s, %s",
                                    t.id,
                                    t.name,
                                    t.values,
                                )

                            if (suboffset := ifd.next) == 0:
                                break
                        else:
                            break

                # Restore the previous position after parsing the sub IFD
                handle.seek(position)

        return tag

    def _parse_image_data(self, ifd: IFD):
        if not isinstance(ifd, IFD):
            raise TypeError("The 'ifd' argument must reference an IFD class instance!")

        logger.debug(f" >>>> Parsing IFD, {ifd}, for image data")

        strip_offsets: Tag = None
        strip_byte_counts: Tag = None

        tile_width: Tag = None
        tile_height: Tag = None
        tile_offsets: Tag = None
        tile_byte_counts: Tag = None

        for tag in ifd:
            # logger.debug(f" >>>> Parsing Tag, {tag}({tag.id}), {tag.name}, {builtins.type(tag.id)}, for image data")

            if tag.id == 273:  # StripOffsets
                strip_offsets = tag

                logger.debug(
                    f" >>>> Found StripOffsets, {tag}, truthy: {'yes' if tag else 'no'}"
                )
            elif tag.id == 279:  # StripByteCounts
                logger.debug(
                    f" >>>> Found StripByteCounts, {tag}, truthy: {'yes' if tag else 'no'}"
                )

                strip_byte_counts = tag
            elif tag.id == 322:  # TileWidth
                logger.debug(" >>>> Found TileWidth")

                tile_width = tag
            elif tag.id == 323:  # TileLength (TileHeight)
                logger.debug(" >>>> Found TileLength")

                tile_height = tag
            elif tag.id == 324:  # TileOffsets
                logger.debug(" >>>> Found TileOffsets")

                tile_offsets = tag
            elif tag.id == 325:  # TileByteCounts
                logger.debug(" >>>> Found TileByteCounts")

                tile_byte_counts = tag

        logger.debug(f"strip_offsets: {strip_offsets}")
        logger.debug(f"strip_byte_counts: {strip_byte_counts}")
        logger.debug(f"tile_width: {tile_width}")
        logger.debug(f"tile_height: {tile_height}")
        logger.debug(f"tile_offsets: {tile_offsets}")
        logger.debug(f"tile_byte_counts: {tile_byte_counts}")

        if tile_width and tile_height and tile_offsets and tile_byte_counts:
            if not len(tile_offsets.values) == len(tile_byte_counts.values):
                raise TIFFDataParseError(
                    "The TileOffsets and TileByteCounts tags do not have the same number of elements!"
                )

            # logger.debug(tile_offsets)
            # logger.debug(tile_byte_counts)

            for index, offset in enumerate(tile_offsets.values):
                if not (isinstance(offset, int) and offset >= 0):
                    raise TIFFDataError(
                        "The TileOffsets values must all be positive integers!"
                    )

                if not (
                    isinstance(count := tile_byte_counts.values[index], int)
                    and count >= 0
                ):
                    raise TIFFDataError(
                        "The TileByteCounts values must all be positive integers!"
                    )

                logger.debug(
                    "Tile %03d: Offset: %08d; Length: %08d" % (index, offset, count)
                )

                ifd.tile = Tile(index=index, offset=offset, length=count, carrier=ifd)
        elif strip_offsets and strip_byte_counts:
            if not len(strip_offsets.values) == len(strip_byte_counts.values):
                raise TIFFDataParseError(
                    "The StripOffsets and StripByteCounts tags do not have the same number of elements!"
                )

            # logger.debug(strip_offsets)
            # logger.debug(strip_byte_counts)

            for index, offset in enumerate(strip_offsets.values):
                if not (isinstance(offset, int) and offset >= 0):
                    raise TIFFDataError(
                        "The StripOffsets values must all be positive integers!"
                    )

                if not (
                    isinstance(count := strip_byte_counts.values[index], int)
                    and count >= 0
                ):
                    raise TIFFDataError(
                        "The StripByteCounts values must all be positive integers!"
                    )

                logger.debug(
                    "Strip %03d: Offset: %08d; Length: %07d",
                    index,
                    offset,
                    count,
                )

                ifd.strip = Strip(index=index, offset=offset, length=count, carrier=ifd)
        else:
            logger.warning(
                "Unable to find the expected tags for a tiled or strip-based TIFF in IFD: %s!",
                ifd,
            )

    def _structure(self, order: ByteOrder = None, format: Format = None):
        """Build or rebuild the linked-list between the TIFF's data elements and adjust
        the target offsets of each element as needed to represent the layout of the data
        as it would be written to into a new TIFF file."""

        logger.debug(f"TIFF._structure(order: {order}, format: {format})")

        if order is None:
            order = self.order

        if format is None:
            format = self.format

        ####################### Build the Linked-List of Elements ######################

        # Obtain a reference to the top-level container, and reset the linked list
        element: Element = self.container.reset()

        # Iterate through the IFDs chaining each element into the linked-list
        for ifd in self:
            logger.debug(">" * 50 + " IFDs " + "<" * 50)

            # Chain the IFD and any of its nested IFD Tags into the linked-list
            element = ifd.chain(element)

            logger.debug(">" * 50 + " Tags with external data " + "<" * 50)

            # Iterate over the IFD's tags, and for any that have external data, create
            # a Data element instance to represent the external data and its offset:
            for tag in ifd.tags:
                logger.debug(f" > {ifd}.{tag}")

                if tag.external(format=format) is True:
                    logger.debug(" > data is external")

                    if not isinstance(datum := tag.datum, Data):
                        tag.datum = datum = Data(
                            offset=Offset(source=tag.dataoffset),
                            length=tag.datasize,
                            parent=tag,
                        )

                    # For tags that have been newly created or updated with data after
                    # being parsed from the TIFF file, carry the data to the datum Data
                    # class instance, so that it will be written out to the file; data
                    # held by other tags cannot be copied here as it could be offsets
                    # and other intrinsic data, that could affect the file if included:
                    if isinstance(data := tag.data, bytes) and tag.updated is True:
                        datum.data = data
                        datum.length = len(data)
                        tag.count = len(data)

                    element = datum.chain(element)
                else:
                    logger.debug(" > data is internal")
                    tag.datum = None

            logger.debug(">" * 50 + " IFDs with Strips " + "<" * 50)

            # Iterate over the IFD's image data strips, if any, chaining them to the list
            for strip in ifd.strips:
                element = strip.chain(element)

            logger.debug(">" * 50 + " IFDs with Tiles " + "<" * 50)

            # Iterate over the IFD's image data tiles, if any, chaining them to the list
            for tile in ifd.tiles:
                element = tile.chain(element)

            logger.debug(">" * 100)

        ######################### Compute Target File Offsets ##########################

        # Compute the target file's offsets for each TIFF data element:
        element: Element = self.container
        offset: int = 0
        while True:
            # Ensure that all offsets begin on (even) word boundaries
            if offset % 2 == 0:  # Even offset
                element.offset.target = offset
                element.offset.padded = False  # Note that the offset is not padded
            else:  # Odd offset
                offset += 1  # Increment the offset to an even offset
                element.offset.target = offset
                element.offset.padded = True  # Note that the offset is padded

            # Add the current element's length to the offset, for the next element
            offset += element.length

            # Break if the end of the linked-list has been reached
            if not (element := element.carries):
                break

        ############### Recompute Tag External Data (Datum) Offsets ####################

        logger.debug(">" * 50 + " Recompute Tag Datum Offsets " + "<" * 50)

        # Update offsets for any Tags that have external held data for Tags that have
        # data that is too large to be held within the Tag's data field itself, thus for
        # Classic TIFF this will be data larger than 4 bytes, and for Big TIFF, any data
        # larger than 8 bytes; in these cases, the data is written elsewhere in the file
        # and in the linked-list is represented by a Data class instance; for externally
        # held data, the Tag records the offset to the externally held data, rather than
        # the data itself, so here we update the Tag's data attribute to hold the offset
        for ifd in self:
            for tag in ifd:
                logger.debug(f" > {ifd}.{tag}")

                if tag.external(format=format) is True:
                    logger.debug(f" > {ifd}.{tag} offset {tag.datum.offset.target}")

                    if tag.datum is None:
                        raise RuntimeError(
                            f"The {tag} has no datum, yet is an external data tag!"
                        )
                    elif format is Format.ClassicTIFF:
                        tag.data = UInt32(tag.datum.offset.target).encode(order=order)
                    elif format is Format.BigTIFF:
                        tag.data = UInt64(tag.datum.offset.target).encode(order=order)
                elif tag.hasIFDs is True:
                    logger.debug(f" > {ifd}.{tag} offset {tag.sub.offset.target}")

                    if tag.sub is None:
                        logger.debug(
                            "The %s tag has no sub IFD, yet is a sub-IFD data tag!",
                            tag,
                        )
                    elif format is Format.ClassicTIFF:
                        tag.data = UInt32(tag.sub.offset.target).encode(order=order)
                    elif format is Format.BigTIFF:
                        tag.data = UInt64(tag.sub.offset.target).encode(order=order)

        ########################## Recompute IFD Next Offsets ##########################

        logger.debug(">" * 50 + " Recompute IFD Offsets " + "<" * 50)

        # Gather a list of IFD offsets and update the IFD next offsets to point to the
        # updated location of each IFD within the target file; the last four or eight
        # bytes of an IFD (four bytes for Classic TIFF and eight bytes for Big TIFF) are
        # used to hold the offset for the next IFD, if any; if there are no further IFDs
        # to follow, the next offset value will be zero (0), indicating its the last one
        ifd_offsets: list[int] = []

        for ifd in self.ifds:
            ifd_offsets.append(ifd.offset.target)

        logger.debug(" >>> IFD Offsets >>> %s", ifd_offsets)

        # Iterate over the IFDs, and update the next offset of each IFD
        for index, ifd in enumerate(self.ifds):
            logger.debug(f" >>> Looking for IFD#{index} datum:")

            if isinstance(datum := ifd.datum, IFDNext) and (datum.parent is ifd):
                logger.debug(f" >>> Found IFD#{index} datum: {datum}")

                if (index + 1) < len(ifd_offsets):
                    offset = ifd_offsets[(index + 1)]
                else:
                    offset = 0

                logger.debug(
                    f" >>> IFD#{index} Next Offset (Before): {hexbytes(datum.data) if datum.data else 'N/A'}"
                )

                # The IFDNext.encode() method encodes and returns the value of .next, not .data
                datum.next = offset

                if format is Format.ClassicTIFF:
                    datum.data = UInt32(offset).encode(order=order)
                elif format is Format.BigTIFF:
                    datum.data = UInt64(offset).encode(order=order)

                logger.debug(
                    f" >>> IFD#{index} Next Offset (After):  {hexbytes(datum.data)} ({offset})"
                )

        logger.debug(">" * 50 + " Recompute Strip/Tile Offsets " + "<" * 50)

        ######################## Recompute Strip/Tile Offsets ##########################

        # Iterate over the IFDs, and update any Strip/Tile Offsets
        for ifd in self:
            # Attempt to find the StripOffsets and StripByteCounts tags
            strip_offsets = ifd.tagfilter(id=273, first=True)
            strip_byte_counts = ifd.tagfilter(id=279, first=True)

            # Attempt to find the TileOffsets and TileByteCounts tags
            tile_offsets = ifd.tagfilter(id=324, first=True)
            tile_byte_counts = ifd.tagfilter(id=325, first=True)

            logger.debug("&" * 100)
            logger.debug("StripOffsets:    %s", strip_offsets)
            logger.debug("StripByteCounts: %s", strip_byte_counts)
            logger.debug("TileOffsets:     %s", tile_offsets)
            logger.debug("TileByteCounts:  %s", tile_byte_counts)

            # If StripOffsets and StripByteCounts tags were found, adjust the offsets
            if strip_offsets and strip_byte_counts:
                data: bytearray = bytearray()

                offsets: list[int] = []

                for strip in ifd.strips:
                    offsets.append(strip.offset.target)

                    if format is Format.ClassicTIFF:
                        data += UInt32(strip.offset.target).encode(order=order)
                    elif format is Format.BigTIFF:
                        data += UInt64(strip.offset.target).encode(order=order)

                logger.debug(
                    " >>>> strip offsets => %s => %s (%s)",
                    offsets,
                    hexbytes(data),
                    len(data),
                )

                if format is Format.ClassicTIFF and len(data) > 4:
                    strip_offsets.datum = datum = Data(
                        data=bytes(data),
                        length=len(data),
                        parent=strip_offsets,
                    )

                    element: Element = self.container
                    while True:
                        if isinstance(element, Data) and element.parent:
                            if element.parent is strip_offsets:
                                element.replace(datum)

                        # Break if the end of the linked-list has been reached
                        if not (element := element.carries):
                            break
                elif format is Format.BigTIFF and len(data) > 8:
                    strip_offsets.datum = datum = Data(
                        data=bytes(data),
                        length=len(data),
                        parent=strip_offsets,
                    )

                    element: Element = self.container
                    while True:
                        if isinstance(element, Data) and element.parent:
                            if element.parent is strip_offsets:
                                element.replace(datum)

                        # Break if the end of the linked-list has been reached
                        if not (element := element.carries):
                            break
                else:
                    strip_offsets.datum = None
                    strip_offsets.data = bytes(data)
                    strip_offsets.length = len(data)

            # If TileOffsets and TileByteCounts tags were found, adjust the offsets
            elif tile_offsets and tile_byte_counts:
                data: bytearray = bytearray()

                offsets: list[int] = []

                for tile in ifd.tiles:
                    offsets.append(tile.offset.target)

                    if format is Format.ClassicTIFF:
                        data += UInt32(tile.offset.target).encode(order=order)
                    elif format is Format.BigTIFF:
                        data += UInt64(tile.offset.target).encode(order=order)

                logger.debug(
                    " >>>> tile offsets => %s (%s)",
                    offsets,
                    hexbytes(data),
                )

                if format is Format.ClassicTIFF and len(data) > 4:
                    tile_offsets.datum = datum = Data(
                        data=bytes(data),
                        length=len(data),
                        parent=tile_offsets,
                    )

                    element: Element = self.container
                    while True:
                        if isinstance(element, Data) and element.parent:
                            if element.parent is tile_offsets:
                                element.replace(datum)

                        # Break if the end of the linked-list has been reached
                        if not (element := element.carries):
                            break

                elif format is Format.BigTIFF and len(data) > 8:
                    tile_offsets.datum = datum = Data(
                        data=bytes(data),
                        length=len(data),
                        parent=tile_offsets,
                    )

                    element: Element = self.container
                    while True:
                        if isinstance(element, Data) and element.parent:
                            if element.parent is tile_offsets:
                                element.replace(datum)

                        # Break if the end of the linked-list has been reached
                        if not (element := element.carries):
                            break
                else:
                    tile_offsets.datum = None
                    tile_offsets.data = bytes(data)
                    tile_offsets.length = len(data)

            # If neither Strip nor Tile Offsets were found, the IFD has no image data
            else:
                logger.debug("The %s does not contain any image data...", ifd)

            logger.debug("&" * 100)

    @property
    def info(self) -> Information:
        """Return the byte order of the current TIFF file: Big or Little Endian."""

        return self._info

    @property
    def filepath(self) -> str:
        """Return filepath for the current TIFF file."""

        return self.info.filepath

    @property
    def filesize(self) -> int:
        """Return the file size for the current TIFF file."""

        return self.info.filesize

    @property
    def order(self) -> ByteOrder:
        """Return the byte order of the current TIFF file: Big or Little Endian."""

        return self.info.order

    @property
    def format(self) -> Format:
        """Return the format of the current TIFF file: ClassicTIFF or BigTIFF."""

        return self.info.format

    @property
    def prolog(self) -> bytes:
        """Return the prolog of the current TIFF file, which is the data prior to the
        first (0th) IFD, containing the byte order mark, format specifier and offset."""

        return bytes(self._prolog)

    @property
    def container(self) -> Container:
        """Return the reference to the top-level container which is the parent of all
        TIFF file elements, such as the IFDs, Tags, Strips and Tiles."""

        return self._container

    @property
    def ifds(self) -> list[IFD]:
        """Return the list of IFDs found within the TIFF."""

        return list(self._ifds)

    @property
    def elements(self) -> list[Element]:
        """Return the list of file elements found within the TIFF, including the top
        level container, the IFDs, Tags, Strips, Tiles and Data elements."""

        elements: list[Element] = []

        carrier: Element = self.container

        elements.append(carrier)

        while carries := carrier.carries:
            carrier = carries

            elements.append(carrier)

        return elements

    @property
    def tags(self) -> list[Tag]:
        """Return the list of IFD Tags parsed from the current TIFF file."""

        return self._tags

    def get(
        self,
        key: int | str | TIFFTag,
        default: object = None,
        ifd: int | IFD | bool = 0,
        first: bool = False,
    ) -> list[object] | None:
        """Support for getting a named tag from the TIFF."""

        if isinstance(key, TIFFTag):
            key = key.id
        elif isinstance(key, int) and key >= 1:
            pass
        elif isinstance(key, str):
            if tag := TIFFTag.reconcile(key, caselessly=True):
                key = tag.value
            else:
                raise TypeError(
                    f"The 'key' argument must have a valid Tag ID value, expressed either as a TIFFTag enumeration option, a Tag ID integer value, or Tag ID name; the provided value, '{key}', cannot be reconciled against a known Tag ID!"
                )
        else:
            raise TypeError(
                "The 'key' argument must have a string or an integer value!"
            )

        if isinstance(ifd, bool):
            # True = get tag value from any IFD; return first matching tag's value
            # False = get tag from first IFD, ignore all others

            for index, _ifd in enumerate(self.ifds):
                if ifd is True:
                    if value := self.get(key=key, ifd=_ifd, first=first):
                        return value
                elif ifd is False:
                    if index == 0:
                        if value := self.get(key=key, ifd=_ifd, first=first):
                            return value

            return default

        if isinstance(ifd, int):
            if not ifd >= 0:
                raise ValueError(
                    "If an IFD index is supplied, it must be a positive number!"
                )

            index: int = ifd

            ifd: IFD = None

            for _index, _ifd in enumerate(self):
                if index == _index:
                    ifd = _ifd
                    break
            else:
                raise ValueError(
                    f"The provided IFD index, {index}, is invalid, and does not match against an IFD!"
                )

        if not isinstance(ifd, IFD):
            raise TypeError(
                "The 'ifd' argument must reference an IFD class instance or an IFD index!"
            )

        tag: Tag = None

        for _tag in ifd:
            if isinstance(key, int) and _tag.id == key:
                tag = _tag
                break
            elif isinstance(key, str) and _tag.name == key:
                tag = _tag
                break
        else:
            return default

        if isinstance(tag, Tag):
            # if tag.external(format=self.format) is True and isinstance(tag.datum, Data):
            # if tag.datum.data is None:
            #     return tag.values
            # return bytes(tag.datum.data)
            # elif isinstance(tag.data, (bytes, bytearray)):
            # return bytes(tag.data)

            if first is True:
                if len(tag.values) > 0:
                    return tag.values[0]
            else:
                return tag.values

        return default

    def set(
        self,
        key: int | str | TIFFTag,
        value: bytes | bytearray | object,
        ifd: int | IFD | bool = 0,
    ) -> TIFF:
        """Support for setting the value of the named tag on the TIFF."""

        if isinstance(key, TIFFTag):
            key = key.id
        elif isinstance(key, int) and key >= 1:
            pass
        elif isinstance(key, str):
            if tag := TIFFTag.reconcile(key, caselessly=True):
                key = tag.value
            else:
                raise TypeError(
                    f"The 'key' argument must have a valid Tag ID value, expressed either as a TIFFTag enumeration option, a Tag ID integer value, or Tag ID name; the provided value, '{key}', cannot be reconciled against a known Tag ID!"
                )
        else:
            raise TypeError(
                "The 'key' argument must have a string or an integer value!"
            )

        if isinstance(ifd, bool):
            # True = set tag on all IFDs
            # False = set tag on first IFD, remove (if set) on all others

            for index, _ifd in enumerate(self.ifds):
                if ifd is True:
                    self.set(key=key, value=value, ifd=_ifd)
                elif ifd is False:
                    if index == 0:
                        self.set(key=key, value=value, ifd=_ifd)
                    else:
                        self.remove(key=key, ifd=_ifd)

        if isinstance(value, (bytes, bytearray)):
            value = Bytes(value)
        else:
            raise TypeError(
                "The 'value' argument must have a bytes or bytearray value!"
            )

        if isinstance(ifd, int):
            if not ifd >= 0:
                raise ValueError("An IFD index must have a positive integer value!")

            index: int = ifd

            ifd: IFD = None

            for _index, _ifd in enumerate(self):
                if index == _index:
                    ifd = _ifd
                    break
            else:
                raise ValueError(
                    f"The provided IFD index, {index}, is invalid, and does not match against an IFD!"
                )

        if not isinstance(ifd, IFD):
            raise TypeError(
                "The 'ifd' argument must reference an IFD class instance or an IFD index!"
            )

        tag: Tag = None

        for _tag in ifd:
            if isinstance(key, int) and _tag.id == key:
                tag = _tag
                break
            elif isinstance(key, str) and _tag.name == key:
                tag = _tag
                break
        else:
            if tifftag := TIFFTag.reconcile(key, caselessly=True):
                logger.debug(f" > reconciled TIFF tag for {key} => {tifftag}")

                tag = Tag(
                    id=tifftag.value,
                    name=tifftag.name,
                    type=(
                        (
                            tifftag.type[0]
                            if isinstance(tifftag.type, tuple)
                            else tifftag.type
                        )
                        if hasattr(tifftag, "type")
                        else DataType.Undefined
                    ),
                    count=1,
                    data=None,
                    tag=tifftag,
                    tiff=self,
                    new=True,
                )
            else:
                raise KeyError(
                    f"The TIFFData library does not recognise a match between the specified key, '{key}', and a IFD Tag!"
                )

        logger.debug(
            "TIFF.set(key: %s, value: %s, ifd: %s)"
            % (
                key,
                hexbytes(value, limit=20),
                ifd,
            )
        )

        logger.debug(f" > tag being updated => {tag}")
        logger.debug(f" > value length => {len(value)}")

        if isinstance(tag, Tag):
            tag.updated = True
            tag.data = bytes(value)
            tag.count = len(value)

            if tag.new is True:
                ifd.tag = tag
                # We must clear the new flag after the Tag has been added to the IFD to
                # prevent it being added again on possible future calls to this method:
                tag.new = False

        return self

    def remove(
        self,
        key: int | str | TIFFTag,
        ifd: int | IFD | bool = 0,
    ) -> bool:
        """Support for removing named tags from the TIFF."""

        logger.debug(
            "%s.remove(key: %s, ifd: %s)",
            self.__class__.__name__,
            key,
            ifd,
        )

        if isinstance(ifd, bool):
            # True = remove tag on all IFDs
            # False = remove tag on first IFD, ignore any others

            for index, _ifd in enumerate(self.ifds):
                if ifd is True:
                    self.remove(key=key, ifd=_ifd)
                elif ifd is False:
                    if index == 0:
                        self.remove(key=key, ifd=_ifd)

        if isinstance(ifd, int):
            if not ifd >= 0:
                raise ValueError("An IFD index must have a positive integer value!")

            index: int = ifd

            ifd: IFD = None

            for _index, _ifd in enumerate(self):
                if index == _index:
                    ifd = _ifd
                    break
            else:
                raise ValueError(
                    f"The provided IFD index, {index}, is invalid, and does not match against an IFD!"
                )

        if not isinstance(ifd, IFD):
            raise TypeError(
                "The 'ifd' argument must reference an IFD class instance or an IFD index!"
            )

        return ifd.untag(key)

    def restructure(self) -> TIFF:
        """Support for recomputing the internal linked-list structure after changes."""

        self._structure()

        return self

    def save(
        self,
        filepath: str = None,
        overwrite: bool = False,
        order: ByteOrder = None,
        format: Format = None,
        status: bool = False,
        buffer: int = 16384,  # default 16KB read buffer
    ):
        """Support for saving the TIFF file to storage."""

        logger.debug(
            "%s.save(filepath: %s, overwrite: %s, order: %s, format: %s, status: %s)",
            self.__class__.__name__,
            filepath,
            overwrite,
            order,
            format,
            status,
        )

        if filepath is None:
            filepath = self.info.filepath
        elif isinstance(filepath, str):
            pass
        else:
            raise TypeError(
                "The 'filepath' argument, if specified, must have a string value!"
            )

        if not isinstance(overwrite, bool):
            raise TypeError("The 'overwrite' argument must have a boolean value!")

        if order is None:
            order = self.order
        elif not isinstance(order, ByteOrder):
            raise TypeError(
                "The 'order' argument, if specified, must reference a ByteOrder enumeration option!"
            )

        if format is None:
            format = self.format
        elif isinstance(format, Format):
            # TODO: Allow conversion from Big TIFF to Classic TIFF if the Big TIFF file
            # is small enough (<= 4 GiB) to support mapping the data at 32-bit offsets
            if format is Format.ClassicTIFF and self.format is Format.BigTIFF:
                raise RuntimeError(
                    "The TIFFData library only supports transcoding Classic TIFF to Big TIFF, not the other way around!"
                )
        else:
            raise TypeError(
                "The 'format' argument, if specified, must reference a Format enumeration option!"
            )

        if not isinstance(status, bool):
            raise TypeError(
                "The 'status' argument, if specified, must have a boolean value!"
            )

        if not (isinstance(buffer, int) and not isinstance(buffer, bool)):
            raise TypeError(
                "The 'buffer' argument, if specified, must have an integer value!"
            )
        elif buffer == 0:
            pass  # turns off buffered read/write, so that all data is read before write
        elif not (1024 <= buffer <= 65536):
            raise ValueError(
                "The 'buffer' argument, if specified, must have a positive integer value between 1024 - 65,536!"
            )

        time_start: float = None

        if status is True:
            time_start = time.time()
            print()
            print(f" > Saving TIFF file to {filepath}")

        # Rebuild structure immediately prior to saving to ensure offsets are up-to-date
        self._structure(order=order, format=format)

        if os.path.exists(filepath) and overwrite is False:
            raise RuntimeError(
                "Cannot overwrite the file at '%s' unless the 'overwrite' argument is set to True; alternatively, specify a different path to save to using the optional 'filepath' argument!"
                % (filepath)
            )

        with tempfile.NamedTemporaryFile(
            mode="wb+",
            dir=os.path.dirname(filepath),
            delete=False,
        ) as handle:
            logger.debug(f" > A temporary file, {handle.name}, was created")
            logger.debug(f" > {order} / {format}")

            # Determine the number of elements to be saved
            count: int = len(self.elements)

            # Determine the length (size) of the target file, computed from the starting
            # offset of the last element plus the length of the last element:
            length: int = self.elements[-1].offset.target + self.elements[-1].length

            # Determine the length of the string representation of the length integer so
            # that the the length values can be padded for readability in the status log
            lenpad: int = len(str(length))

            def update_status(index: int):
                """Helper method to display and update save status."""

                offset: int = handle.tell()

                print(
                    f" > Saving element %04d/%04d • %06.2f%% • %0{lenpad}d/%0{lenpad}d bytes • %.3f seconds"
                    % (
                        index,
                        count,
                        ((offset / length) * 100),
                        offset,
                        length,
                        (time.time() - time_start),
                    ),
                    end="\r",
                )

            # Iterate through the elements, saving each to the target file
            for index, element in enumerate(self.elements, start=1):
                # If a padding byte is needed to start the element on a word boundary...
                if element.offset.padded is True:
                    handle.write(b"\x00")  # ...add it here

                dataoffset: int = handle.tell()
                datalength: int = 0

                logger.debug(" > writing data for %s at %d" % (element, dataoffset))

                if isinstance(element, Data) and not (
                    isinstance(element.parent, IFD) or isinstance(element.data, bytes)
                ):
                    position: int = self._filehandle.tell()

                    logger.debug(
                        " > seeking to % 8d for % 8d bytes to obtain %s"
                        % (element.offset.source, element.length, element)
                    )

                    self._filehandle.seek(element.offset.source)

                    # If buffered reading and writing is enabled copy the data in blocks
                    # from the source file to the target file, streamlining the save
                    if buffer > 0:
                        datalength: int = element.length
                        datacopied: int = 0

                        # Copy the data in segments of the defined size (readlength)
                        # until the full amount of data has been copied and written
                        # between the source file to the target file:
                        while datacopied < datalength:
                            if (
                                readlength := min(
                                    buffer,
                                    datalength - datacopied,
                                )
                            ) == 0:
                                break

                            if not (data := self._filehandle.read(readlength)):
                                break

                            datacopied += handle.write(data)

                            if status is True:
                                update_status(index=index)
                    else:
                        data: bytes = self._filehandle.read(element.length)
                        datalength += handle.write(data)

                        if status is True:
                            update_status(index=index)

                    self._filehandle.seek(position)

                    logger.debug(
                        f" > writing copied element data: {hexbytes(data, limit=20)} ({len(data)})"
                    )
                else:
                    data = element.encode(order=order, format=format)
                    datalength += handle.write(data)

                    logger.debug(
                        f" > writing encoded element data: {hexbytes(data)} ({len(data)})"
                    )

                    if status is True:
                        update_status(index=index)

            # Close the file, ensuring data is flushed and written to storage
            handle.close()

            if status is True:
                print()
                print(" > Saving complete • %3.3f seconds" % (time.time() - time_start))
                print()

            # Remove the existing file, if present, and if overwriting is enabled
            if os.path.exists(filepath) and overwrite is True:
                os.remove(filepath)

            # Rename the temporary file to its destination name
            os.rename(handle.name, filepath)

    def dump(self, **filters: dict[str, object]):
        """Generates and prints a plaintext formatted tabular informational dump for the
        structure of the file, listing its elements, their offsets, lengths and data."""

        self._structure()

        from tiffdata.types import ASCII, UTF8, Short, Long, Rational
        from tabulicious import tabulate

        def valueform(values: list | object, limit: int = 0, strlimit: int = 0):
            limited: bool = False

            if isinstance(values, bytes):
                return hexbytes(values, limit=limit)
            elif isinstance(values, list):
                if limit > 0 and len(values) > limit:
                    values = values[0:limit]
                    limited = True

            types: list[type] = []

            for value in values:
                types.append(type(value))

            if len(types) > 0:
                if issubclass(types[0], (ASCII, UTF8)):
                    return (
                        "".join(
                            [
                                str(
                                    v[0:strlimit] + "..."
                                    if strlimit > 0 and len(v) > strlimit
                                    else v
                                )
                                for v in values
                            ]
                        )
                    ) + ("..." if limited else "")
                elif issubclass(types[0], (Short, Long, Rational, int)):
                    val = ", ".join([str(v) for v in values])
                    if limit > 0 and len(val) > (limit * 3):
                        val = val[0 : (limit * 3)] + "..."
                    return val
                else:
                    return str(types[0])

            return "-"

        headers: list[str] = [
            "#",
            "Element",
            "Source Offset",
            "Target Offset",
            "Length",
            "Data (Raw)",
            "Data (Values)",
        ]

        rows: list[list[object]] = []

        for index, element in enumerate(self.elements, start=1):
            include: bool = False

            if len(filters) == 0:
                include = True
            elif filter := filters.get(element.__class__.__name__.lower()):
                for key, value in filter.items():
                    if hasattr(element, key):
                        if getattr(element, key) == value:
                            include = True
            elif hasattr(element, "parent") and isinstance(
                parent := element.parent, Element
            ):
                if filter := filters.get(parent.__class__.__name__.lower()):
                    for key, value in filter.items():
                        if hasattr(parent, key):
                            if getattr(parent, key) == value:
                                include = True

            if include is False:
                continue

            rows.append(
                [
                    index,
                    element,
                    element.offset.source,
                    element.offset.target,
                    element.length,
                    hexbytes(
                        element.encode(order=self.order, format=self.format), limit=20
                    ),
                    (
                        valueform(element.values, limit=10)
                        if hasattr(element, "values")
                        else "–"
                    ),
                ]
            )

        print("\n" + str(tabulate(rows, headers, style="curved")))


class ClassicTIFF(TIFF):
    """The ClassicTIFF class represents classic TIFF files which use 32-bit offsets."""

    _type: UInt = UInt32


class BigTIFF(TIFF):
    """The BigTIFF class represents big TIFF files which use 64-bit offsets."""

    _type: UInt = UInt64
