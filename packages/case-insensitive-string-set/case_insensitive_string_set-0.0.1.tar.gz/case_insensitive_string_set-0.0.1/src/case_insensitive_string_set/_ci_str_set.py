from __future__ import annotations

from typing import MutableSet, Iterator, Dict, Iterable


class CaseInsensitiveStringSet(MutableSet[str]):
    """
    A set class for case-insensitive strings.
    """

    _data: Dict[str, str]

    def __init__(self, iterable: Iterable[str] | None = None):
        self._data = {item.casefold(): item for item in (iterable or [])}

    def add(self, value: str) -> None:
        folded = value.casefold()
        if folded not in self._data:
            self._data[folded] = value

    def discard(self, value: str) -> None:
        self._data.pop(value.casefold(), None)

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[str]:
        return iter(self._data.values())

    def __contains__(self, item: object) -> bool:
        if not isinstance(item, str):
            return False
        return item.casefold() in self._data

    def copy(self) -> CaseInsensitiveStringSet:
        return CaseInsensitiveStringSet(self._data.values())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CaseInsensitiveStringSet):
            return NotImplemented
        return sorted(self._data.keys()) == sorted(other._data.keys())
