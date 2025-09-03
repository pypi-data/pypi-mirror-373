"""A storage backend using TinyDB or a stdlib JSON storage handler."""

from collections.abc import Generator
from contextlib import contextmanager, suppress
import json
from pathlib import Path
from threading import RLock
from typing import Any, ClassVar

from bear_dereth.config._settings_manager._base_classes import QueryLike, StorageBackend
from bear_dereth.config._settings_manager._cache import LRUCache
from bear_dereth.config._settings_manager._common import Document, FileWatcher, QueryCheck, ValueType
from bear_dereth.config._settings_manager._record import SettingsRecord
from bear_dereth.tools.freezing import FrozenDict, freeze

StorageDatabase: StorageBackend


class JsonFileStorage:
    """Stdlib-only storage backend using JSON files."""

    _lock: ClassVar[RLock] = RLock()

    def __init__(self, file_path: str | Path, cache_size: int = 10, **kwargs) -> None:
        self.path = Path(file_path)
        self.save_settings: dict[str, Any] = kwargs
        self._data: list[Document] = []
        self._query_cache = LRUCache[QueryLike, list[Document]](capacity=cache_size)
        self._load()
        self._file = FileWatcher(self.path)

    def _load(self) -> None:
        """Load data from JSON file."""

        def _json_get(path: Path) -> list:
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()
                path.write_text("[]", encoding="utf-8")
                return []
            try:
                with path.open("r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return []

        frozen_data: tuple[Document, ...] = self.immutable_data

        for record in _json_get(self.path):
            if isinstance(record, dict) and "key" in record and "value" in record:
                output: SettingsRecord[ValueType] = SettingsRecord.model_validate(record)
                doc: Document = output.get_document()
                frozen: FrozenDict = freeze(doc)
                if frozen not in frozen_data:
                    self._data.append(doc)

    @property
    def immutable_data(self) -> tuple[Document, ...]:
        """Get an immutable copy of the data."""
        with self._lock:
            return freeze(self._data)

    @contextmanager
    def _cache_check(self) -> Generator[None, Any]:
        """Context manager to check for external file changes."""
        if self._file.has_changed:
            self._load()
        yield

    def _save(self) -> None:
        """Save data to JSON file."""

        def save_to_file() -> None:
            with self.path.open("w") as f:
                json.dump(self._data, f, **self.save_settings)

        with self._lock, suppress(OSError):
            save_to_file()

    def get(self, key: str) -> Any:
        """Get a value by key."""
        with self._lock, self._cache_check():
            for record in self._data:
                if record.get("key") == key:
                    return record.get("value")
            return None

    def all(self) -> list[Document]:
        """Return all records."""
        with self._lock, self._cache_check():
            return self._data.copy()

    def upsert(self, record: dict[str, ValueType], query: QueryCheck) -> None:
        """Update existing record or insert new one."""
        with self._lock, self._cache_check():
            rec: SettingsRecord[ValueType] = SettingsRecord.model_validate(record)
            doc: Document = rec.get_document()

            for index, existing_record in enumerate(self._data):
                if query(existing_record):
                    self._data.pop(index)
                    self._add(doc)
                    return
            self._add(doc)

    def _add(self, record: Document) -> None:
        """Add a new record without checking for existing keys."""
        self._data.append(record)
        self._save()

    def set(self, key: str, value: ValueType) -> None:
        """Set a key-value pair using SettingsRecord."""
        with self._lock, self._cache_check():
            record: SettingsRecord[ValueType] = SettingsRecord(key=key, value=value)
            doc: Document = record.get_document()
            for existing_record in self._data:
                if existing_record.get("key") == key:
                    self._data.remove(existing_record)
                    self._add(doc)
                    return
            self._add(doc)

    def search(self, query: QueryLike) -> list[Document]:
        """Search records using a callable query function."""
        cached_results: list[Document] | None = self._query_cache.get(query)
        if cached_results is not None:
            return cached_results[:]
        with self._lock, self._cache_check():
            # FIXME: This could be optimized further by caching individual records.
            return [record for record in self._data if query(record)]

    def contains(self, query: QueryCheck) -> bool:
        """Check if any record matches the query."""
        with self._lock, self._cache_check():
            return any(query(record) for record in self._data)

    def close(self) -> None:
        """Close the storage (save any pending changes)."""
        self._save()


HAS_TINYDB = False
try:
    from tinydb import TinyDB as StorageDatabase  # type: ignore[import]

    HAS_TINYDB = True
except ImportError:
    StorageDatabase = JsonFileStorage  # type: ignore[assignment]


def Database(file_path: Path, **kwargs: Any) -> StorageBackend:  # noqa: N802
    """Get a TinyDB database instance or fallback to JSON file storage.

    Args:
        file_path (Path): Path to the database file.
        **kwargs: Additional keyword arguments to pass to the database constructor.

    Returns:
        StorageBackend: An instance of the database backend, either TinyDB or JsonFileStorage.
    """
    return StorageDatabase(file_path, **kwargs)


__all__ = ["HAS_TINYDB", "Database"]
