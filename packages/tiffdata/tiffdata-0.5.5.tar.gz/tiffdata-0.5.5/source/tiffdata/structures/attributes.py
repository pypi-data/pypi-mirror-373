from tiffdata.logging import logger

import collections
import typing

logger = logger.getChild(__name__)


class Attributes(collections.abc.Mapping):
    """The Attributes class holds arbitrary key-values accessible via attribute and item
    access patterns on behalf of other data types."""

    _data: dict[str, object] = None

    def __init__(self, **attributes: dict[str, object]):
        self._data: dict[str, object] = {}

        for key, value in attributes.items():
            self._data[key] = value

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> typing.Generator[str, None, None]:
        for key in self._data.keys():
            yield key

    def __getattr__(self, name: str) -> object | None:
        if name.startswith("_"):
            return super().__getattr__(name)
        elif name in self._data:
            return self._data[name]
        else:
            raise AttributeError(f"The Attributes class has no '{name}' attribute!")

    def __setattr__(self, name: str, value: object):
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            self._data[name] = value

    def __delattr__(self, name: str):
        if name.startswith("_"):
            super().__delattr__(name)
        elif name in self._data:
            del self._data[name]

    def __getitem__(self, name: str) -> object | None:
        if name in self._data:
            return self._data[name]
        else:
            raise KeyError(f"The Attributes class has no '{name}' item!")

    def __setitem__(self, name: str, value: object):
        if name.startswith("_"):
            raise NotImplementedError
        else:
            self._data[name] = value

    def __delitem__(self, name: str):
        if name.startswith("_"):
            raise NotImplementedError
        elif name in self._data:
            del self._data[name]
