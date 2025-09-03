from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Self

from bear_dereth.config._settings_manager._base_classes import HashValue, NotCacheable, QueryInstance, QueryLike
from bear_dereth.config._settings_manager._common import QueryCheck  # noqa: TC001

if TYPE_CHECKING:
    from collections.abc import Callable

Queryish: QueryLike


class BackupQuery(QueryInstance):
    """Lightweight Query class that mimics TinyDB's Query interface.

    Now with frozen data structure support for better hashing and immutability.
    """

    def __init__(self) -> None:
        self._path: tuple[str | Callable, ...] = ()

        def notest(*args, **kwargs) -> bool:  # noqa: ARG001
            raise RuntimeError("Empty query was evaluated")

        super().__init__(test=notest, hash_val=HashValue(op=None, value=[None]))

    def __hash__(self) -> int:
        return super().__hash__()

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"

    def __getattr__(self, key: str) -> Self:
        """Build nested path for attribute access like Query().user.name"""
        query: Self = type(self)()
        query._path = (*self._path, key)
        query._hash = HashValue(op="path", value=[*self._path, key]) if self.is_cacheable() else NotCacheable()
        return query

    def __getitem__(self, key: str) -> Self:
        """Build nested path for item access like Query()["user"]["name"]"""
        return self.__getattr__(key)

    def _get_test(self, test: QueryCheck, hash_val: HashValue, allow_empty_path: bool = False) -> QueryInstance:
        """Generate a query based on a test function that first resolves the query path.

        Args:
            test (QueryCheck): A callable that takes a single argument and returns a boolean.
            hash_val (tuple): A tuple representing the hash value for caching.
            allow_empty_path (bool): Whether to allow an empty path. Defaults to False.

        Returns:
            QueryInstance: A query instance that applies the test to the resolved path value.
        """
        if not self._path and not allow_empty_path:
            raise ValueError("Query has no path")

        def runner(value) -> bool:  # noqa: ANN001
            try:
                for part in self._path:
                    value = value[part] if isinstance(part, str) else part(value)
            except (KeyError, TypeError):
                return False
            else:
                return test(value)

        hash_val = hash_val if self.is_cacheable() else HashValue.not_cacheable()
        return QueryInstance(lambda value: runner(value), hash_val)

    def __eq__(self, value: Any) -> QueryInstance:  # type: ignore[override] # noqa: PYI032
        """Create equality test callable."""
        return self._get_test(lambda record: record == value, hash_val=HashValue(op="==", value=[*self._path, value]))

    def __ne__(self, value: Any) -> QueryInstance:  # type: ignore[override] # noqa: PYI032
        """Create not-equal test callable."""
        return self._get_test(lambda record: record != value, hash_val=HashValue(op="!=", value=[*self._path, value]))

    def __gt__(self, value: Any) -> QueryInstance:
        """Create greater-than test callable."""
        return self._get_test(
            lambda record: record is not None and record > value, hash_val=HashValue(op=">", value=[*self._path, value])
        )

    def __lt__(self, value: Any) -> QueryInstance:
        """Create less-than test callable."""
        return self._get_test(
            lambda record: record is not None and record < value, hash_val=HashValue(op="<", value=[*self._path, value])
        )

    def __ge__(self, value: Any) -> QueryInstance:
        """Create greater-than-or-equal test callable."""
        return self._get_test(
            lambda record: record is not None and record >= value,
            hash_val=HashValue(op=">=", value=[*self._path, value]),
        )

    def __le__(self, value: Any) -> QueryInstance:
        """Create less-than-or-equal test callable."""
        return self._get_test(
            lambda record: record is not None and record <= value,
            hash_val=HashValue(op="<=", value=[*self._path, value]),
        )

    def exists(self) -> QueryInstance:
        """Create exists test callable."""
        return self._get_test(
            lambda _: True,
            hash_val=HashValue(op="exists", value=[*self._path]),
            allow_empty_path=True,
        )

    def matches(self, regex: str, flags: int = 0) -> QueryInstance:
        """Create a regex match test callable."""

        def regex_test(record: Any) -> bool:
            if not isinstance(record, str):
                return False
            return re.match(regex, record, flags) is not None

        return self._get_test(regex_test, hash_val=HashValue(op="matches", value=[*self._path, regex, flags]))

    def search(self, regex: str, flags: int = 0) -> QueryInstance:
        """Create a regex search test callable."""

        def regex_test(record: Any) -> bool:
            if not isinstance(record, str):
                return False
            return re.search(regex, record, flags) is not None

        return self._get_test(regex_test, hash_val=HashValue(op="search", value=[*self._path, regex, flags]))

    def all(self, condition: QueryInstance | list[Any]) -> QueryInstance:
        """Create a test callable that checks if all elements in a list satisfy a condition.

        Args:
            condition (QueryInstance | list[Any]): A callable condition or a list of values to check
                for membership.

        Returns:
            QueryInstance: A query instance that checks if all elements satisfy the condition.
        """
        if callable(condition):

            def test(value) -> bool:  # noqa: ANN001
                return hasattr(value, "__iter__") and all(condition(e) for e in value)

        else:

            def test(value) -> bool:  # noqa: ANN001
                return hasattr(value, "__iter__") and all(e in value for e in condition)

        return self._get_test(lambda record: test(record), hash_val=HashValue(op="all", value=[*self._path, condition]))


try:
    from tinydb import Query as Queryish  # type: ignore[import]

except ImportError:  # pragma: no cover
    Queryish = BackupQuery  # type: ignore[assignment]


def Query() -> QueryLike:  # noqa: N802 # pragma: no cover
    """Get a Query instance depending on availability."""
    return Queryish()  # type: ignore[call-arg]


def where(key: str) -> QueryLike:
    """A shorthand for ``Query()[key]``

    Args:
        key (str): The key to query.

    Returns:
        QueryLike: A Query instance with the specified key.
    """
    return Query()[key]
