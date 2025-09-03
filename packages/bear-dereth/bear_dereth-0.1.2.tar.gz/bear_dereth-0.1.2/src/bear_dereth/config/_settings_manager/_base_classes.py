from __future__ import annotations

from collections.abc import Mapping  # noqa: TC003
from typing import TYPE_CHECKING, Any, NoReturn, Protocol, Self

from bear_dereth.config._settings_manager._common import OpType  # noqa: TC001
from bear_dereth.tools.freezing import BaseNotCacheable, FrozenModel

if TYPE_CHECKING:
    from bear_dereth.config._settings_manager._common import Document, QueryCheck


class HashValue(FrozenModel):
    """A simple frozen model to hold a hash value for query caching."""

    op: OpType | None
    value: list[Any] | None = None

    def combine(self, op: OpType, other: HashValue) -> HashValue:
        """Combine multiple hash values into one."""
        return HashValue(op=op, value=[self, other])

    def __hash__(self) -> int:
        if not self.cacheable:
            raise TypeError("This HashValue is not cacheable")
        return super().__hash__()


class NotCacheable(HashValue, BaseNotCacheable):
    """A singleton representing a non-cacheable hash value, contains a frozen cacheable=False flag."""

    def __init__(self) -> None: ...

    def __hash__(self) -> int:
        raise TypeError("This HashValue is not cacheable")

    def combine(self, op: OpType, other: HashValue) -> NoReturn:  # noqa: ARG002
        raise TypeError("This object is not cacheable")


class QueryInstance:
    """A manifestation of a query operation."""

    def __init__(self, test: QueryCheck, hash_val: HashValue | None) -> None:
        self._test = test
        self._hash: HashValue = hash_val if hash_val is not None else NotCacheable()

    def is_cacheable(self) -> bool:
        """Check if this object is cacheable."""
        return self._hash.cacheable

    def combine(self, op: OpType, other: QueryInstance) -> HashValue:
        """Combine multiple hash values into one."""
        if not other.is_cacheable() or not self.is_cacheable():
            return NotCacheable()
        return self._hash.combine(op, other._hash)

    def __call__(self, value: Mapping) -> bool:
        return self._test(value)

    def __hash__(self) -> int:
        return hash(self._hash)

    def __repr__(self) -> str:
        return f"QueryImpl{self._hash}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, QueryInstance):
            return self._hash == other._hash

        return False

    def __and__(self, other: QueryInstance) -> QueryInstance:
        return QueryInstance(lambda value: self(value) and other(value), self.combine("and", other))

    def __or__(self, other: QueryInstance) -> QueryInstance:
        return QueryInstance(lambda value: self(value) or other(value), self.combine("or", other))

    def __invert__(self) -> QueryInstance:
        return QueryInstance(lambda value: not self(value), HashValue(op="not", value=[self._hash]))


class QueryLike(Protocol):
    def __call__(self, value: Mapping) -> bool: ...
    def __getattr__(self, key: str) -> Self: ...
    def __getitem__(self, key: str) -> Self: ...
    def __eq__(self, value: object) -> QueryInstance: ...  # type: ignore[override]
    def __ne__(self, value: object) -> QueryInstance: ...  # type: ignore[override]
    def __hash__(self) -> int: ...
    def __gt__(self, value: Any) -> QueryInstance: ...
    def __lt__(self, value: Any) -> QueryInstance: ...
    def __and__(self, other: Self) -> QueryInstance: ...
    def __or__(self, other: Self) -> QueryInstance: ...
    def matches(self, regex: str, flags: int = 0) -> QueryInstance: ...
    def search(self, regex: str, flags: int = 0) -> QueryInstance: ...
    def exists(self) -> QueryInstance: ...


class StorageBackend(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Self: ...
    def get(self, key: str) -> Any: ...
    def set(self, key: str, value: Any) -> None: ...
    def search(self, query: Any) -> list[Document]: ...
    def all(self) -> list[Document]: ...
    def upsert(self, record: dict[str, Any], query: Any) -> None: ...
    def contains(self, query: Any) -> bool: ...
    def close(self) -> None: ...
