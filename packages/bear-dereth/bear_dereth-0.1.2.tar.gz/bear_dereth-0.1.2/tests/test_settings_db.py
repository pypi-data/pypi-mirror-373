"""Comprehensive tests for the settings database functionality."""

from collections.abc import Generator
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Any

import pytest

from bear_dereth.config._settings_manager._db import Database, JsonFileStorage
from bear_dereth.config._settings_manager._record import Document, SettingsRecord

if TYPE_CHECKING:
    from bear_dereth.config._settings_manager._base_classes import StorageBackend


class TestSettingsRecord:
    """Test SettingsRecord model validation and type detection."""

    def test_string_type_detection(self) -> None:
        """Test automatic string type detection."""
        record = SettingsRecord(key="name", value="test")
        assert record.type == "string"
        assert record.key == "name"
        assert record.value == "test"

    def test_number_type_detection(self) -> None:
        """Test automatic integer type detection."""
        record = SettingsRecord(key="age", value=25)
        assert record.type == "number"
        assert record.value == 25

    def test_float_type_detection(self) -> None:
        """Test automatic float type detection."""
        record = SettingsRecord(key="ratio", value=3.14)
        assert record.type == "float"
        assert record.value == 3.14

    def test_boolean_type_detection(self) -> None:
        """Test automatic boolean type detection."""
        record = SettingsRecord(key="enabled", value=True)
        assert record.type == "boolean"
        assert record.value is True

        record_false = SettingsRecord(key="disabled", value=False)
        assert record_false.type == "boolean"
        assert record_false.value is False

    def test_null_type_detection(self) -> None:
        """Test automatic null type detection."""
        record = SettingsRecord(key="optional", value=None)
        assert record.type == "null"
        assert record.value is None

    def test_model_dump(self) -> None:
        """Test model serialization."""
        record: SettingsRecord[int] = SettingsRecord(key="test", value=42)
        dumped: dict[str, Any] = record.model_dump()

        expected: dict[str, str | int] = {"key": "test", "value": 42, "type": "number"}
        assert dumped == expected

    def test_boolean_precedence_over_int(self) -> None:
        """Test that boolean detection happens before int (since bool is subclass of int)."""
        record: SettingsRecord[bool] = SettingsRecord(key="flag", value=True)
        assert record.type == "boolean"  # Not "number"


class TestJsonFileStorage:
    """Test JsonFileStorage CRUD operations."""

    @pytest.fixture
    def temp_db(self, tmp_path: Path) -> Generator[JsonFileStorage, Any]:
        """Create a temporary database for testing."""
        db_path: Path = tmp_path / "test_db.json"

        db = JsonFileStorage(db_path)
        yield db

        if db_path.exists():
            db_path.unlink()

    def test_set_and_get(self, temp_db: JsonFileStorage) -> None:
        """Test basic set and get operations."""
        temp_db.set("username", "testuser")
        assert temp_db.get("username") == "testuser"

    def test_get_nonexistent_key(self, temp_db: JsonFileStorage) -> None:
        """Test getting a key that doesn't exist."""
        assert temp_db.get("nonexistent") is None

    def test_set_updates_existing(self, temp_db: JsonFileStorage) -> None:
        """Test that set updates existing records."""
        temp_db.set("counter", 1)
        temp_db.set("counter", 2)
        assert temp_db.get("counter") == 2

        # Should only have one record
        all_records: list[Document] = temp_db.all()
        counter_records: list[dict[str, Any]] = [r for r in all_records if r.get("key") == "counter"]
        assert len(counter_records) == 1

    def test_multiple_data_types(self, temp_db: JsonFileStorage):
        """Test storing different data types."""
        temp_db.set("name", "test")
        temp_db.set("age", 25)
        temp_db.set("ratio", 3.14)
        temp_db.set("active", True)  # noqa: FBT003

        assert temp_db.get("name") == "test"
        assert temp_db.get("age") == 25
        assert temp_db.get("ratio") == 3.14
        assert temp_db.get("active") is True

    def test_persistence(self, temp_db: JsonFileStorage):
        """Test that data persists across database instances."""
        # Store data
        temp_db.set("persistent", "value")
        db_path = temp_db.path

        # Create new instance with same path
        new_db = JsonFileStorage(db_path)
        assert new_db.get("persistent") == "value"

    def test_upsert_new_record(self, temp_db: JsonFileStorage):
        """Test upserting a new record."""
        temp_db.upsert({"key": "new_key", "value": "new_value"}, lambda r: r.get("key") == "new_key")

        assert temp_db.get("new_key") == "new_value"

    def test_upsert_existing_record(self, temp_db):
        """Test upserting an existing record."""
        temp_db.set("existing", "old_value")
        temp_db.upsert({"key": "existing", "value": "new_value"}, lambda r: r.get("key") == "existing")

        assert temp_db.get("existing") == "new_value"

    def test_upsert_with_type_detection(self, temp_db: JsonFileStorage):
        """Test that upsert automatically detects types."""
        temp_db.upsert({"key": "typed", "value": 42}, lambda r: r.get("key") == "typed")

        records = temp_db.search(lambda r: r.get("key") == "typed")
        assert len(records) == 1
        assert isinstance(records[0]["value"], int) is True

    def test_search(self, temp_db: JsonFileStorage) -> None:
        """Test search functionality."""
        temp_db.set("user1", "alice")
        temp_db.set("user2", "bob")
        temp_db.set("count", 10)

        # Search for string values
        string_records: list[Document] = temp_db.search(lambda r: r.get("type") == "string")
        assert len(string_records) == 2

        # Search for specific key
        user1_records: list[Document] = temp_db.search(lambda r: r.get("key") == "user1")
        assert len(user1_records) == 1
        assert user1_records[0]["value"] == "alice"

    def test_contains(self, temp_db: JsonFileStorage):
        """Test contains functionality."""
        temp_db.set("exists", "value")

        assert temp_db.contains(lambda r: r.get("key") == "exists")
        assert not temp_db.contains(lambda r: r.get("key") == "missing")

    def test_all(self, temp_db: JsonFileStorage):
        """Test getting all records."""
        temp_db.set("key1", "value1")
        temp_db.set("key2", "value2")

        all_records = temp_db.all()
        assert len(all_records) == 2

        keys = {r["key"] for r in all_records}
        assert keys == {"key1", "key2"}

    def test_close(self, temp_db: JsonFileStorage):
        """Test close functionality (should save data)."""
        temp_db.set("test", "value")
        temp_db.close()

        # Verify data was saved
        new_db = JsonFileStorage(temp_db.path)
        assert new_db.get("test") == "value"


class TestFactoryFunctions:
    """Test factory functions and TinyDB fallback."""

    @pytest.fixture
    def temp_path(self) -> Generator[Path, Any]:
        """Create a temporary file path."""
        with NamedTemporaryFile(suffix=".json", delete=True) as f:
            yield Path(f.name)

    def test_get_db_returns_storage(self, temp_path: Path):
        """Test that get_db returns a StorageBackend."""
        db: StorageBackend = Database(temp_path)

        # Should have all StorageBackend methods
        assert hasattr(db, "get")
        assert hasattr(db, "set")
        assert hasattr(db, "search")
        assert hasattr(db, "all")
        assert hasattr(db, "upsert")
        assert hasattr(db, "contains")
        assert hasattr(db, "close")


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.fixture
    def temp_db(self) -> Generator[JsonFileStorage, Any]:
        """Create a temporary database for testing."""
        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            db_path = Path(f.name)

        db = JsonFileStorage(db_path)
        yield db

        # Cleanup
        if db_path.exists():
            db_path.unlink()

    def test_corrupted_json_file(self) -> None:
        """Test handling of corrupted JSON files."""
        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content {")
            db_path = Path(f.name)

        # Should not crash, should start with empty data
        db = JsonFileStorage(db_path)
        assert db.all() == []

        # Cleanup
        db_path.unlink()

    def test_empty_json_file(self) -> None:
        """Test handling of empty JSON files."""
        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("")
            db_path = Path(f.name)

        # Should not crash, should start with empty data
        db = JsonFileStorage(db_path)
        assert db.all() == []

        # Cleanup
        db_path.unlink()

    def test_upsert_without_key_value_structure(self, temp_db: JsonFileStorage) -> None:
        """Test upserting records that don't follow key-value pattern."""
        record = {"id": 1, "key": "test", "value": "active"}

        temp_db.upsert(record, lambda r: r.get("id") == 1)

        results: list[Document] = temp_db.search(lambda r: r.get("key") == "test")
        assert len(results) == 1
        assert results[0]["key"] == "test"
        assert results[0]["value"] == "active"
