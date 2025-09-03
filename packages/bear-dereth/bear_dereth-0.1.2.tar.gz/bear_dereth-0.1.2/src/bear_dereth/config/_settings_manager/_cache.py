from collections import OrderedDict
from collections.abc import Iterator, MutableMapping
from math import inf
from typing import Any


class LRUCache[K, V](MutableMapping):
    """A least-recently used (LRU) cache with a fixed cache size."""

    def __init__(self, capacity: int | None = None) -> None:
        self.capacity: int | float = capacity or inf
        self.cache: OrderedDict[K, V] = OrderedDict()

    @property
    def lru(self) -> list[K]:
        return list(self.cache.keys())

    @property
    def length(self) -> int:
        return len(self.cache)

    def clear(self) -> None:
        self.cache.clear()

    def __len__(self) -> int:
        return self.length

    def __contains__(self, key: object) -> bool:
        return key in self.cache

    def __setitem__(self, key: K, value: V) -> None:
        self.set(key, value)

    def __delitem__(self, key: K) -> None:
        del self.cache[key]

    def __getitem__(self, key: Any) -> V:
        value: V | None = self.get(key)
        if value is None:
            raise KeyError(key)

        return value

    def __iter__(self) -> Iterator[K]:
        return iter(self.cache)

    def get[D](self, key: K, default: D | None = None) -> V | D | None:
        value: V | None = self.cache.get(key)

        if value is not None:
            self.cache.move_to_end(key, last=True)

            return value

        return default

    def set(self, key: K, value: V) -> None:
        if self.cache.get(key):  # key in this case in a Query object and cannot be a falsy value
            self.cache[key] = value
            self.cache.move_to_end(key, last=True)
        else:
            self.cache[key] = value

            # Evict least-recently used item if over capacity
            # If capacity is inf, this will never happen
            if self.length > self.capacity:
                self.cache.popitem(last=False)
