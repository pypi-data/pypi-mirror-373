from __future__ import annotations

import os
import io


class File(object):
    """The 'File' class supports working with file data from a range of sources."""

    _path: str = None
    _mode: str = None
    _open: bool = False
    _size: int = None
    _encoding: str = None
    _newline: str = None
    _handle: io.BufferedReader | io.BufferedWriter = None

    @classmethod
    def from_path(cls, path: str) -> File:
        return cls(path=path)

    @classmethod
    def from_buffer(cls, buffer: object) -> File:
        pass

    @classmethod
    def from_data(cls, data: bytes | bytearray) -> File:
        pass

    def __init__(
        self,
        path: str = None,
        mode: str = "rb",
        encoding: str = None,
        newline: str = "\n",
    ) -> None:
        self._path: str = path
        self._mode: str = mode
        self._encoding: str = encoding
        self._newline: str = newline

    def __enter__(self):
        self.open()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    @property
    def path(self) -> str:
        return self._path

    @property
    def size(self) -> int:
        return self._size

    @property
    def offset(self) -> int:
        return self.tell()

    def open(self):
        if self._open is True:
            return

        # open the file
        self._handle: object = open(
            filename=self._path,
            mode=self._mode,
            encoding=self._encoding,
            newline=self._newline,
        )

        self._open: bool = True

        # determine the file size
        self._handle.seek(0, os.SEEK_END)  # seek to the end of the file
        self._size: int = self._handle.tell()  # obtain the position of the last byte
        self._handle.seek(0, os.SEEK_SET)  # seek back to the start of the file

    def tell(self) -> int:
        if self._open is False:
            raise RuntimeError(
                "Cannot tell the position from the file as it is closed!"
            )

        return self._handle.tell()

    def seek(self, position: int, direction: os.SEEK_SET):
        if self._open is False:
            raise RuntimeError("Cannot seek in the file as it is closed!")

        return self._handle.seek(position, direction)

    def read(self, size: int = None) -> bytes | str:
        if self._open is False:
            raise RuntimeError("Cannot read from the file as it is closed!")

        return self._handle.read(size)

    def saferead(self, size: int = None) -> bytes | str:
        if (self.offset + size) >= self.size:
            raise RuntimeError(
                "Cannot read %d bytes from the current offset %d as the read would pass the end of the file!"
                % (
                    size,
                    self.offset,
                )
            )

        return self._handle.read(size)

    def readline(self) -> bytes | str:
        if self._open is False:
            raise RuntimeError("Cannot read from the file as it is closed!")

        return self._handle.readline()

    def write(self, data: bytes | str):
        if self._open is False:
            raise RuntimeError("Cannot write to the file as it is closed!")

        return self._handle.write(data)

    def flush(self):
        if self._open is False:
            raise RuntimeError("Cannot flush to the file as it is closed!")

        if self._handle is None:
            return

        self._handle.flush()

    def close(self):
        if self._handle is None:
            return

        self._handle.close()

        self._open: bool = True
