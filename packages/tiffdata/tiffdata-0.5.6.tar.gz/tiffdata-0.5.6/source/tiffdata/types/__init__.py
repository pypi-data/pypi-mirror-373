from __future__ import annotations

from deliciousbytes import (
    ByteOrder,
    UInt8,
    Int8,
    Short,
    UnsignedShort,
    Long,
    UnsignedLong,
    LongLong,
    UnsignedLongLong,
    Bytes,
    Float,
    Double,
    String,
    ASCII,
    UTF8,
    Encoding,
)

import fractions


# TODO: Simplify types, use deliciousbytes types directly, can we manage without Value?


class Value(object):
    _value: object = None

    def __init__(self, value: object):
        self._value = value

    @property
    def value(self) -> object:
        return self._value

    @value.setter
    def value(self, value: object):
        self._value = value


class UInt8(Value, UInt8):
    pass


class Int8(Value, Int8):
    pass


class Rational(Value):
    """Two unsigned long integers used to hold a rational number. The first long is the
    numerator and the second long expresses the denominator."""

    _tagid: int = 5
    _signed: bool = False

    def __init__(
        self,
        value: float | str = None,
        numerator: int = None,
        denominator: int = None,
        **kwargs,
    ):
        if value is None:
            if not isinstance(numerator, int):
                raise ValueError(
                    "If no 'value' argument has been specified, both the 'numerator' and 'denominator' arguments must be specified!"
                )
            if not isinstance(denominator, int):
                raise ValueError(
                    "If no 'value' argument has been specified, both the 'numerator' and 'denominator' arguments must be specified as integers!"
                )
        elif isinstance(value, (int, float, str)):
            if isinstance(value, int):
                numerator = value
                denominator = 1
            elif fraction := fractions.Fraction(value):
                numerator = int(fraction.numerator)
                denominator = int(fraction.denominator)
            else:
                raise ValueError("The 'value' could not be parsed into a fraction!")
        else:
            raise ValueError(
                "Either the 'value' or 'numerator' and 'denominator' arguments must be specified!"
            )

        self.numerator: Long = numerator
        self.denominator: Long = denominator

        super().__init__(value=f"{numerator}/{denominator}", **kwargs)

    def __str__(self) -> str:
        return f"{self.numerator}/{self.denominator}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.numerator}/{self.denominator}) @ {hex(id(self))}>"

    def __int__(self) -> int:
        return int(int(self.numerator) // int(self.denominator))

    def __float__(self) -> int:
        return float(int(self.numerator) / int(self.denominator))

    @property
    def numerator(self) -> Long:
        return self._numerator

    @numerator.setter
    def numerator(self, numerator: int):
        if not isinstance(numerator, int):
            raise TypeError("The 'numerator' argument must have an integer value!")

        if self._signed is True:
            self._numerator = SignedLong(numerator)
        elif self._signed is False:
            self._numerator = UnsignedLong(numerator)

    @property
    def denominator(self) -> Long:
        return self._denominator

    @denominator.setter
    def denominator(self, denominator: int):
        if not isinstance(denominator, int):
            raise TypeError("The 'denominator' argument must have an integer value!")

        if self._signed is True:
            self._denominator = SignedLong(denominator)
        elif self._signed is False:
            self._denominator = UnsignedLong(denominator)

    def encode(self, order: ByteOrder = ByteOrder.MSB) -> bytes:
        encoded: list[bytes] = []

        encoded.append(self.numerator.encode(order=order))

        encoded.append(self.denominator.encode(order=order))

        return b"".join(encoded)

    @classmethod
    def decode(cls, value: bytes, order: ByteOrder = ByteOrder.MSB) -> Rational:
        if not isinstance(value, bytes):
            raise TypeError("The 'value' argument must have a bytes value!")

        # Expect value to be 8 bytes, 64 bits in length for two long (32-bit) integers
        if not (length := len(value)) == 8:
            raise ValueError(
                "The provided bytes 'value' does not have the expected length of 8 bytes (64 bits), but rather: %d!"
                % (length)
            )

        if cls._signed is True:
            numerator: SignedLong = SignedLong.decode(value[0:4], order=order)
            denominator: SignedLong = SignedLong.decode(value[4:8], order=order)
        else:
            numerator: UnsignedLong = UnsignedLong.decode(value[0:4], order=order)
            denominator: UnsignedLong = UnsignedLong.decode(value[4:8], order=order)

        return cls(numerator=numerator, denominator=denominator)


class UnsignedRational(Rational):
    def __str__(self) -> str:
        return f"{self.numerator}/{self.denominator}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.numerator}/{self.denominator}) @ {hex(id(self))}>"


class SignedRational(Rational):
    """Two signed long integers used to hold a rational number. The first long is the
    numerator and the second long expresses the denominator."""

    _signed: bool = True


class Short(Short, Value):
    pass


class SignedShort(Short):
    pass


class UnsignedShort(UnsignedShort, Value):
    pass


class Long(Long, Value):
    pass


class SignedLong(Long):
    pass


class UnsignedLong(UnsignedLong, Value):
    pass


class LongLong(LongLong, Value):
    pass


class SignedLongLong(LongLong):
    pass


class UnsignedLongLong(UnsignedLongLong, Value):
    pass


class Float(Value, Float):
    pass


class Double(Value, Double):
    pass


class Bytes(Bytes, Value):
    pass


class String(String, Value):
    pass


class ASCII(ASCII, Value):
    @classmethod
    def decode(
        cls,
        value: bytes,
        order: ByteOrder = ByteOrder.MSB,
        encoding: Encoding = None,
    ) -> String:
        if not isinstance(value, bytes):
            raise TypeError("The 'value' argument must have a 'bytes' value!")

        if not isinstance(order, ByteOrder):
            raise TypeError(
                "The 'order' argument must reference a ByteOrder enumeration option!"
            )

        if encoding is None:
            encoding = cls.encoding
        elif not isinstance(encoding, Encoding):
            raise TypeError(
                "The 'encoding' argument, if specified, must reference an Encoding enumeration option!"
            )

        if order is ByteOrder.LSB:
            value = bytes(reversed(bytearray(value)))

        # Some embedded metadata values that should be constrained to ASCII, contain
        # characters from UTF-8, such as the © symbol, which will result in an exception
        # being raised by str.decode(string, "ascii") when it cannot reconcile the byte
        # value to an ASCII character as it is out of range; as such we catch the error
        # and attempt the decode again, but with the UTF-8 character set:
        try:
            return cls(value.decode(encoding.value))
        except UnicodeDecodeError:
            return cls(value.decode("UTF-8"))


class UTF8(UTF8, Value):
    pass
