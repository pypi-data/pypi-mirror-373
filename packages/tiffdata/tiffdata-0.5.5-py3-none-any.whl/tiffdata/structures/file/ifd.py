from __future__ import annotations

from tiffdata.logging import logger

from tiffdata.structures.offset import Offset

from tiffdata.structures.file.base import Element
from tiffdata.structures.file.tag import Tag
from tiffdata.structures.file.strip import Strip
from tiffdata.structures.file.tile import Tile
from tiffdata.structures.file.data import Data

from tiffdata.enumerations import (
    Format,
    TIFFTag,
)

from tiffdata.exceptions import (
    TIFFDataError,
)

from deliciousbytes import (
    ByteOrder,
    UInt16,
    UInt32,
    UInt64,
)

import typing
import io

logger = logger.getChild(__name__)


class IFD(Element):
    """The IFD class represents an Image File Directory used within EXIF compatible
    image file formats such as TIFF and JPEG to hold image and metadata information.

    IFD0 is the first IFD in an EXIF file and contains the main image data, including
    resolution, color space, and other essential image attributes. It can also store
    EXIF metadata like camera settings, date, and time, via its associated EXIF IFD.

    IFD1 is often used to store information about a thumbnail image, which is a smaller
    version of the main image, and is included to support faster previews. All tags from
    IFD0 may also be present in IFD1.

    IFD2, while less common, can exist to store additional image data or information
    about related images, such as linked images or other image formats.

    All IFDs comprise the following components:
    +---------------+-----------------------------------------------------------------+
    | Tag Count     | Two bytes holding the count of tags that follow                 |
    +---------------+-----------------------------------------------------------------+
    | Tags          | One or more byte-encoded IFD Tag values, the length of which    |
    |               | can be determined by multiplying the tag count by 12            |
    +---------------+-----------------------------------------------------------------+
    | Next Offset   | Four or eight bytes holding the pointer to the next IFD or zero |
    +---------------+-----------------------------------------------------------------+

    The tag count is stored as a short integer (UInt16) comprised of 2 bytes or 16 bits.
    The tags are encoded according to the format specified for IFD Tag below.
    The next offset is stored as a long integer (UInt32) comprised of 4 bytes or 32 bits
        or as a long long integer (UInt64) comprised of 8 bytes for Big TIFF files.
    """

    _tiff: TIFF = None
    _index: int = 0
    _count: int = None
    _tags: list[Tag] = None
    _next: int = None
    _nextoffset: int = None
    _subs: list[IFD] = None
    _parent: Element = None
    _strips: list[Strip] = None
    _tiles: list[Tile] = None

    def __init__(
        self,
        tiff: TIFF,
        count: int = 0,
        tags: list[Tag] = None,
        next: int = 0,
        subs: list[IFD] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self._tiff: TIFF = tiff

        if not isinstance(count, int):
            raise TypeError("The 'count' argument must have an integer value!")
        elif not count >= 0:
            raise TypeError("The 'count' argument must have an positive integer value!")

        self._count: int = count

        if tags is None:
            self._tags: list[Tag] = []
        elif not isinstance(tags, list):
            raise TypeError("The 'tags' argument must have a list value!")
        else:
            carrier = self

            for tag in tags:
                if not isinstance(tag, Tag):
                    raise TypeError(
                        "Each entry in the 'tags' list must be an Tag class instance!"
                    )

                carrier.carries = tag
                tag.carrier = carrier

                carrier = tag

            self._tags: list[Tag] = sorted(tags, key=lambda tag: int(tag.id))

        if not isinstance(next, int):
            raise TypeError("The 'next' argument must have an integer value!")
        elif not next >= 0:
            raise TypeError("The 'next' argument must have an positive integer value!")

        self._next: int = next

        if subs is None:
            self._subs: list[IFD] = []
        elif not isinstance(subs, list):
            raise TypeError("The 'subs' argument must have a list value!")
        else:
            for sub in subs:
                if not isinstance(sub, IFD):
                    raise TypeError(
                        "Each entry in the 'subs' list must be an IFD class instance!"
                    )

                sub.carrier = self

            self._subs: list[IFD] = subs

        self._strips: list[Strip] = []

        self._tiles: list[Tile] = []

    def __iter__(self) -> typing.Generator[Tag, None, None]:
        """The __iter__ method provides a generator that iterates through the IFD Tags
        in the current IFD."""

        for tag in self._tags:
            yield tag

    @Element.label.getter
    def label(self) -> str:
        return (
            self._label
            if self._label
            else (
                self.parent.label
                if self.parent
                else self.carrier.label if self.carrier else "?"
            )
        )

    @property
    def tiff(self) -> TIFF:
        """The 'name' property returns the IFD's parent TIFF instance."""

        return self._tiff

    @property
    def index(self) -> int:
        """Two bytes representing the number of tags that follow the IFD"""

        return self._index

    @index.setter
    def index(self, index: int):
        if not isinstance(index, int):
            raise TypeError("The 'index' argument must have an integer value!")
        elif not index >= 0:
            raise TypeError("The 'index' argument must have a positive integer value!")

        self._index = index

    @property
    def count(self) -> int:
        """The number of tags that follow the IFD."""

        return len(self._tags)

    @property
    def tags(self) -> list[Tag]:
        """Variable number of bytes holding the tag data, where the number can be found
        by multiplying the number of tags by twelve."""

        return self._tags

    @tags.setter
    def tags(self, tags: list[Tag]):
        if not isinstance(tags, list):
            raise TypeError("The 'tags' argument must have a list value!")
        else:
            temp: list[Tag] = []  # Create a temporary list to ensure we don't see dupes

            for tag in tags:
                if not isinstance(tag, Tag):
                    raise TypeError(
                        "The 'tags' argument must reference a list of Tag class instances!"
                    )
                elif tag in temp:
                    raise ValueError(
                        "The 'tags' argument contains a duplicate entry for %s; tag references must be unique and cannot be repeated!"
                        % (tag)
                    )
                else:
                    temp.append(tag)

            temp.clear()  # Empty the temp list

        self._tags = sorted(tags, key=lambda tag: int(tag.id))

    @property
    def tag(self):
        raise NotImplementedError

    @tag.setter
    def tag(self, tag: Tag) -> IFD:
        """Variable number of bytes holding the tag data, where the number can be found
        by multiplying the number of tags by twelve."""

        if not isinstance(tag, Tag):
            raise TypeError("The 'tag' argument must reference a Tag class instance!")
        elif tag in self._tags:
            raise ValueError(
                "The 'tag' value, %s, has already been added to %s!" % (tag, self)
            )

        tag.ifd = self

        self._tags.append(tag)

        self._tags = sorted(self._tags, key=lambda tag: int(tag.id))

        self._count += 1

        return self

    def untag(self, tag: str | int | Tag | TIFFTag) -> bool:
        """Support for removing the specified tag from the IFD."""

        logger.debug("%s.untag(tag: %s)" % (self, tag))

        tags: list[Tag] = []

        found: bool = False

        for _tag in self._tags:
            if isinstance(tag, str):
                if _tag.name.lower() == tag.lower():
                    found = True
                    continue
            elif isinstance(tag, int):
                if _tag.id == tag:
                    found = True
                    continue
            elif isinstance(tag, Tag):
                if _tag.id == tag.id:
                    found = True
                    continue
            elif isinstance(tag, TIFFTag):
                if _tag.id == tag.id:
                    found = True
                    continue

            tags.append(_tag)

        self._tags = sorted(tags, key=lambda tag: int(tag.id))
        self._count = len(tags)

        return found

    def tagfilter(self, first: bool = False, **filters: dict[str, object]):
        filtered: list[Tag] = []

        matched: bool = False

        for tag in self.tags:
            for key, value in filters.items():
                if not hasattr(tag, key):
                    matched = False
                    break
                elif getattr(tag, key) == value:
                    matched = True
                else:
                    matched = False
                    break

            if matched is True:
                filtered.append(tag)

        return filtered[0] if (len(filtered) > 0 and first is True) else filtered

    @property
    def next(self) -> int:
        """The offset in bytes to the next IFD, if an IFD follows, or zero otherwise."""

        return self._next

    @next.setter
    def next(self, next: int):
        if not isinstance(next, int):
            raise TypeError("The 'next' argument must have an integer value!")
        elif not next >= 0:
            raise ValueError("The 'next' argument must have a positive integer value!")
        self._next = next

    @property
    def nextoffset(self) -> int:
        """The offset of the next IFD value in the source image."""

        return self._nextoffset

    @nextoffset.setter
    def nextoffset(self, nextoffset: int):
        if not isinstance(nextoffset, int):
            raise TypeError("The 'nextoffset' argument must have an integer value!")
        elif not nextoffset >= 0:
            raise ValueError(
                "The 'nextoffset' argument must have a positive integer value!"
            )
        self._nextoffset = nextoffset

    @property
    def subs(self) -> list[IFD]:
        """The 'subs' property returns the list of sub-IFDs associated with the IFD."""

        return self._subs

    @property
    def sub(self):
        raise NotImplementedError

    @sub.setter
    def sub(self, sub: IFD):
        """The 'sub' property setter allows a sub-IFD to be associated with the IFD."""

        if not isinstance(sub, IFD):
            raise TypeError("The 'sub' argument must reference an IFD class instance!")

        self._subs.append(sub)

    @property
    def strips(self) -> list[Strip]:
        """The 'strips' property returns the list of Strip instances associated with the IFD."""

        return self._strips

    @property
    def strip(self):
        raise NotImplementedError

    @strip.setter
    def strip(self, strip: Strip):
        """The 'strip' property setter allows a Strip to be associated with the IFD."""

        if not isinstance(strip, Strip):
            raise TypeError(
                "The 'strip' argument must reference a Strip class instance!"
            )

        self._strips.append(strip)

    @property
    def tiles(self) -> list[Tile]:
        """The 'tiles' property returns the list of Tile instances associated with the IFD."""

        return self._tiles

    @property
    def tile(self):
        raise NotImplementedError

    @tile.setter
    def tile(self, tile: Tile):
        """The 'tile' property setter allows a Strip to be associated with the IFD."""

        if not isinstance(tile, Tile):
            raise TypeError("The 'tile' argument must reference a Tile class instance!")

        self._tiles.append(tile)

    @Element.length.getter
    def length(self) -> int:
        if self.tiff.info.format is Format.ClassicTIFF:
            return (
                2  # 2 bytes; size of tag count field
                # As .encode() only writes the tag count we don't include tags or next
                # size of tags (12 bytes x tag count)
                # + 4  # 4 bytes; size of next ifd offset field
            )
        elif self.tiff.info.format is Format.BigTIFF:
            return (
                8  # 8 bytes; size of tag count field
                # As .encode() only writes the tag count we don't include tags or next
                # size of tags (20 bytes x tag count)
                # + 8  # 8 bytes; size of next ifd offset field
            )
        else:
            raise TIFFDataError(
                "Unsupported TIFF format; must be Classic of Big TIFF only!"
            )

    @property
    def after(self) -> Element:
        element: Element = self

        while True:
            if isinstance(element := element.carries, Element):
                if isinstance(element, IFDNext) and element.parent is self:
                    break
            else:
                break

        return element

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

    def size(self, format: Format) -> int:
        """Compute the size in bytes of the IFD, its Tags, and any externally stored
        data associated with those tags. The size is computed with reference to the TIFF
        format as this determines whether offsets are stored as 4 byte unsigned longs or
        as 8 byte unsigned long longs, as well as affecting the lengths of other fields.

        All IFDs comprise the following components:
        +-------------+----------------------------------------------------------------+
        | Tag Count   | Two bytes holding the count of tags that follow                |
        +-------------+----------------------------------------------------------------+
        | Tags        | One or more byte-encoded IFD Tag values, the length of which   |
        |             | can be determined by multiplying the tag count by 12           |
        +-------------+----------------------------------------------------------------+
        | Next Offset | Four or eight bytes holding the offset to the next IFD or zero |
        +-------------+----------------------------------------------------------------+
        """

        if not isinstance(format, Format):
            raise TypeError(
                "The 'format' argument must reference a Format enumeration class option!"
            )

        size: int = 0

        if format is Format.ClassicTIFF:
            size += 2  # 2 bytes for the UInt16 encoded tag count

            for tag in self:
                size += tag.size(format=format)

            size += 4  # 4 bytes for the UInt32 encoded next IFD offset
        elif format is Format.BigTIFF:
            size += 2  # 2 bytes for the UInt16 encoded tag count

            for tag in self:
                size += tag.size(format=format)

            size += 8  # 8 bytes for the UInt64 encoded next IFD offset

        return size

    def chain(self, carrier: Element) -> Element:
        """Support chaining the current element to the specifed (carrier) element."""

        logger.debug(
            "%s[%s].chain(carrier: %s[%s])"
            % (
                self.klass,
                self.label,
                carrier.klass,
                carrier.label,
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

        carrier = super().chain(carrier)

        for tag in self.tags:
            carrier = tag.chain(carrier)

        # Add a Data element to hold the IFD next offset
        self.datum = datum = IFDNext(
            length=(8 if self.tiff.info.format is Format.BigTIFF else 4),
            offset=Offset(source=self.nextoffset),
            parent=self,
            next=self.next,
        )

        carrier = datum.chain(carrier)

        return carrier

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

        # Assemble the bytes that represent the IFD metadata and data
        if format is Format.ClassicTIFF:
            encoded.append(UInt16(self.count).encode(order=order))
        elif format is Format.BigTIFF:
            encoded.append(UInt64(self.count).encode(order=order))

        # for tag in self._tags: encoded.append(tag.encode(order=order))

        # encoded.append(self.next.encode(order=order))

        return b"".join(encoded)

    @classmethod
    def decode(
        cls,
        # value: bytes,
        tiff: TIFF,
        handle: io.BufferedReader,
        offset: UInt64,
    ) -> IFD | None:
        raise NotImplementedError


class IFDNext(Data):
    _next: int = None

    def __init__(self, next: int, **kwargs):
        super().__init__(**kwargs)

        if not isinstance(next, int):
            raise TypeError("The 'next' argument must have an integer value!")
        elif not next >= 0:
            raise ValueError("The 'next' argument must have a positive integer value!")

        self._next: int = next

    def __str__(self):
        return f"<IFDNext(offset: {self.offset}, length: {self.length}, parent: {self.parent})>"

    @property
    def next(self) -> int:
        return self._next

    @next.setter
    def next(self, next: int):
        if not isinstance(next, int):
            raise TypeError("The 'next' argument must have an integer value!")
        elif not next >= 0:
            raise ValueError("The 'next' argument must have a positive integer value!")
        self._next = next

    @property
    def values(self) -> list[object]:
        return [self.next]

    def encode(self, order: ByteOrder = ByteOrder.MSB, format: Format = None) -> bytes:
        # raise NotImplementedError

        encoded: list[bytes] = []

        # # Assemble the bytes that represent the IFD metadata and data
        if format is Format.ClassicTIFF:
            encoded.append(UInt32(self.next).encode(order=order))
        elif format is Format.BigTIFF:
            encoded.append(UInt64(self.next).encode(order=order))

        return b"".join(encoded)
