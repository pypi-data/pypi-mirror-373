from __future__ import annotations

from tiffdata.logging import logger
from tiffdata.enumerations.format import Format
from tiffdata.structures.offset import Offset

from enumerific import Enumeration, auto

import typing

logger = logger.getChild(__name__)


class Element(object):
    """The Element class provides base functionality for the TIFF structure subclasses."""

    _label: str = None
    _length: int = None
    _offset: Offset = None
    _carrier: Element = None
    _carries: Element = None
    _datum: Data = None

    def __init__(
        self,
        label: str = None,
        offset: Offset | int = 0,
        length: int = 0,
        carrier: Element = None,
    ):
        """Support initialising the Element class' state."""

        self.label = label
        self.offset = offset
        self.length = length
        self.carrier = carrier

    def __str__(self) -> str:
        """Support getting a string representation of the element."""

        return f"<{self.__class__.__name__}({self.label})>"

    def __iter__(self) -> typing.Generator[Element, None, None]:
        """Supports iteration through the elements available from the current element
        onwards through the linked-list, until no more carried elements are found."""

        if isinstance(element := self.root, Element):
            while True:
                yield element

                if isinstance(carries := element.carries, Element):
                    element = carries
                else:
                    break

    @property
    def klass(self) -> str:
        """Support getting the element's class name."""

        return self.__class__.__name__

    @property
    def label(self) -> str:
        """Support getting the element's label."""

        return self._label or "?"

    @label.setter
    def label(self, label: str):
        """Support setting the element's label."""

        if label is None:
            self._label = None
        elif isinstance(label, str):
            self._label = label
        else:
            raise TypeError(
                "The 'label' argument, if specified, must have a string value!"
            )

    @property
    def length(self) -> int:
        """Support getting the element's data length."""

        return self._length

    @length.setter
    def length(self, length: int):
        """Support setting the element's data length."""

        if not isinstance(length, int):
            raise TypeError("The 'length' argument must have an integer value!")
        elif not length >= 0:
            raise ValueError(
                "The 'length' argument must have a positive integer value!"
            )
        else:
            self._length = length

    @property
    def offset(self) -> Offset:
        """Support getting the node's source and later target offsets within the file"""

        return self._offset

    @offset.setter
    def offset(self, offset: Offset | int):
        """Support setting the node's source and later target offsets within the file"""

        if isinstance(offset, Offset):
            self._offset = offset
        elif isinstance(offset, int):
            if not offset >= 0:
                raise ValueError(
                    "The 'offset' argument must have a positive integer value!"
                )
            self._offset = Offset(source=offset)
        else:
            raise TypeError(
                "The 'offset' argument must have a positive integer value or reference an Offset class instance!"
            )

    @property
    def carrier(self) -> Element | None:
        """Support getting the carrier node if any."""

        return self._carrier

    @carrier.setter
    def carrier(self, carrier: Element):
        """Support setting the carrier node."""

        if carrier is None:
            self._carrier = None
        elif isinstance(carrier, Element):
            if carrier is self:
                raise ValueError(
                    "The 'carrier' argument for %s cannot be a circular reference to itself!"
                    % (self)
                )
            self._carrier = carrier
        else:
            raise TypeError(
                "The 'carrier' argument must reference a Element class instance!"
            )

    @property
    def carries(self) -> Element | None:
        """Support getting the carries node if any."""

        return self._carries

    @carries.setter
    def carries(self, carries: Element):
        """Support setting the carries node."""

        if carries is None:
            self._carries = None
        elif isinstance(carries, Element):
            if carries is self:
                raise ValueError(
                    "The 'carries' argument for %s cannot be a circular reference to itself!"
                    % (self)
                )
            self._carries = carries
        else:
            raise TypeError(
                "The 'carries' argument must reference a Element class instance!"
            )

    @property
    def root(self) -> Element:
        """Support getting the linked-list root (first) node."""

        node: Element = self

        while isinstance(carrier := node.carrier, Element):
            node = carrier

        return node

    @property
    def tip(self) -> Element:
        """Support getting the linked-list tip (last) node."""

        node: Element = self

        while isinstance(carries := node.carries, Element):
            node = carries

        return node

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

        self.carrier = carrier

        carrier.carries = self

        return self

    def insert(self, other: Element, position: Position = None):
        """Support inserting the provided element into the chain at the current element."""

        if not isinstance(other, Element):
            raise TypeError(
                "The 'other' argument must reference a Element class instance!"
            )

        if position is None:
            position = Position.AFTER
        elif not isinstance(position, Position):
            raise TypeError(
                "The 'position' argument must reference a Position enumeration option!"
            )

        logger.debug(
            "%s[%s].insert(other: %s[%s], position: %s)"
            % (
                self.klass,
                self.label,
                other.klass,
                other.label,
                position,
            )
        )

        logger.debug("Carrier => %s" % (self.carrier))
        logger.debug("Carries => %s" % (self.carries))

        # The default behaviour is to insert the other element after the current element
        if position is Position.AFTER:
            other.carrier = self
            other.carries = self.carries

            if self.carries:
                self.carries.carrier = other
            self.carries = other

        # Alternatively insert the other element before the current element
        elif position is Position.BEFORE:
            other.carrier = self.carrier
            other.carries = self

            if self.carrier:
                self.carrier.carries = other
            self.carrier = other

        logger.debug("Carrier => %s" % (self.carrier))
        logger.debug("Carries => %s" % (self.carries))

        return self

    def replace(self, other: Element):
        """Support replacing the current element in the chain with the provided element."""

        if not isinstance(other, Element):
            raise TypeError(
                "The 'other' argument must reference a Element class instance!"
            )

        logger.debug(
            "%s[%s].replace(other: %s[%s])"
            % (
                self.klass,
                self.label,
                other.klass,
                other.label,
            )
        )

        if isinstance(self.offset, Offset) and not (
            isinstance(other.offset, Offset) and other.offset.source > 0
        ):
            other.offset = self.offset.copy()
        else:
            logger.debug(" >>> did not copy self.offset to other.offset <<<")
            logger.debug(" >>> self.offset:  %s" % (isinstance(self.offset, Offset)))
            logger.debug(" >>> other.offset: %s" % (isinstance(other.offset, Offset)))

        carrier = self.carrier
        carries = self.carries

        if carrier:
            carrier.carries = other
            other.carrier = carrier

        if carries:
            carries.carrier = other
            other.carries = carries

        self.carrier = None
        self.carries = None

        return self

    def remove(self):
        """Support removing the current element from the chain."""

        logger.debug(
            "%s[%s].remove()"
            % (
                self.klass,
                self.label,
            )
        )

        # Determine the current element's carrier and carries
        carrier: Element = self.carrier
        carries: Element = self.carries

        logger.debug("Carrier => %s" % (carrier))
        logger.debug("Carries => %s" % (carries))

        # Adjust its carries reference of the carrier to skip the current element
        if carrier:
            carrier.carries = carries if carries else None

        # Adjust its carrier reference of the carries to skip the current element
        if carries:
            carries.carrier = carrier if carrier else None

        # If the element has associated datum, remove that as well
        if isinstance(datum := self.datum, Element):
            datum.remove()

        # Clear the references on the current element, removing it from the chain
        self.carrier = None
        self.carries = None

        logger.debug("Carrier => %s" % (carrier))
        logger.debug("Carries => %s" % (carries))

        return self

    def unchain(self):
        """Support unchaining the current element's carried element, if any."""

        self.carries = None
        self.carrier = None

    def reset(self) -> Element:
        """Support resetting the linked-list between the elements."""

        logger.debug("%s.reset()" % (self))

        element: Element = self.tip  # Find the tip (last) element

        while True:
            element.unchain()  # Unlink the carried element (if any)

            # Find its carrier, working up to the root (first) element
            if carrier := element.carrier:
                element = carrier
            else:
                break

        return self

    @property
    def datum(self) -> Data | None:
        """The data value itself, if it fits in the four bytes available, or a pointer
        to the data if it won't fit, which could be to the beginning of another IFD."""

        return self._datum

    @datum.setter
    def datum(self, datum: Data):
        from tiffdata.structures.file.data import Data

        if datum is None:
            self._datum = None
        elif isinstance(datum, Data):
            datum.parent = self
            self._datum = datum
        else:
            raise TypeError(
                "The 'datum' argument, if specified, must reference a Data class instance!"
            )

    def external(self, format: Format) -> bool:
        """Determine if the element has needs to store any data externally or not, given
        the target file format, which affects how many bytes are available within some
        elements such as Tags to store data (32 bytes for Classic, 64 bytes for Big)."""

        return False


class Position(Enumeration):
    """The Positions enumeration defines the supported linked-list insertion options."""

    BEFORE = auto(description="Insert the element before the current element")
    AFTER = auto(description="Insert the element after the current element")
