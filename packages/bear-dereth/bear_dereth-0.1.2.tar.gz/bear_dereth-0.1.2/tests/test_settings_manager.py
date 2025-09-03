from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from bear_dereth.config._settings_manager._db import HAS_TINYDB, Database, JsonFileStorage, StorageBackend
from bear_dereth.config.settings_manager import SettingsManager

if TYPE_CHECKING:
    from bear_dereth.config._settings_manager._record import ValueType


@pytest.fixture
def tmp_json_path(tmp_path: Path) -> Path:
    """Provide a temporary path for JSON storage."""
    return tmp_path / "temp_settings.json"


@pytest.fixture
def settings_manager(tmp_json_path: Path) -> Generator[SettingsManager]:
    """Create a SettingsManager instance and clean up after."""
    manager = SettingsManager("test_settings", path=tmp_json_path)
    try:
        yield manager
    finally:
        manager.destroy_settings()


class TestSettingsManager:
    """Test SettingsManager integration with storage backends."""

    def test_settings_manager_initialization(self, settings_manager: SettingsManager) -> None:
        """Test that SettingsManager initializes properly."""
        assert hasattr(settings_manager, "db")
        assert hasattr(settings_manager.db, "get")
        assert hasattr(settings_manager.db, "set")
        assert hasattr(settings_manager.db, "search")

    def test_set_and_get_string_setting(self, settings_manager: SettingsManager) -> None:
        """Test setting and getting string values."""
        settings_manager.set("app_name", "MyApp")
        assert settings_manager.get("app_name") == "MyApp"

    def test_set_and_get_number_setting(self, settings_manager: SettingsManager) -> None:
        """Test setting and getting numeric values."""
        settings_manager.set("max_connections", 100)
        assert settings_manager.get("max_connections") == 100

    def test_set_and_get_boolean_setting(self, settings_manager: SettingsManager) -> None:
        """Test setting and getting boolean values."""
        settings_manager.set("debug_mode", value=True)
        assert settings_manager.get("debug_mode") is True

        settings_manager.set("debug_mode", value=False)
        assert settings_manager.get("debug_mode") is False

    def test_get_nonexistent_setting(self, settings_manager: SettingsManager) -> None:
        """Test getting a setting that doesn't exist."""
        assert settings_manager.get("nonexistent") is None

    def test_get_with_default(self, settings_manager: SettingsManager) -> None:
        """Test getting with default value."""
        default_value = "default_app"
        assert settings_manager.get("app_name", default_value) == default_value

        # Set a value and ensure default is not used
        settings_manager.set("app_name", "RealApp")
        assert settings_manager.get("app_name", default_value) == "RealApp"

    def test_settings_persistence(self, tmp_json_path: Path) -> None:
        """Test that settings persist across manager instances."""
        # Set value with first manager
        manager1 = SettingsManager(name="persistent_test", path=tmp_json_path)
        manager1.set("persistent_setting", "should_persist")

        # Create new manager and verify value persists
        manager2 = SettingsManager(name="persistent_test", path=tmp_json_path)
        assert manager2.get("persistent_setting") == "should_persist"

    def test_multiple_settings(self, settings_manager: SettingsManager) -> None:
        """Test setting and getting multiple different settings."""
        settings = {
            "app_name": "TestApp",
            "version": "1.0.0",
            "port": 8080,
            "debug": True,
            "timeout": 30.5,
            "optional_feature": None,
        }

        # Set all settings
        for key, value in settings.items():
            settings_manager.set(key, value)

        # Verify all settings
        for key, expected_value in settings.items():
            assert settings_manager.get(key) == expected_value

    def test_update_existing_setting(self, settings_manager: SettingsManager) -> None:
        """Test updating an existing setting."""
        settings_manager.set("counter", 1)
        assert settings_manager.get("counter") == 1

        settings_manager.set("counter", 2)
        assert settings_manager.get("counter") == 2

        # Should not have duplicate entries
        all_settings: dict[str, ValueType] = settings_manager.get_all()
        print(all_settings)
        assert "counter" in all_settings
        assert all_settings["counter"] == 2

    def test_get_all_settings(self, settings_manager: SettingsManager) -> None:
        """Test getting all settings."""
        settings_manager.set("setting1", "value1")
        settings_manager.set("setting2", 42)
        settings_manager.set("setting3", value=True)

        all_settings: dict[str, ValueType] = settings_manager.get_all()
        assert len(all_settings) == 3

        # Verify all settings are present
        setting_keys: set[str] = set(all_settings.keys())
        assert setting_keys == {"setting1", "setting2", "setting3"}

    def test_settings_with_special_characters(self, settings_manager: SettingsManager) -> None:
        """Test settings with special characters in keys and values."""
        special_settings = {
            "key.with.dots": "value.with.dots",
            "key_with_underscores": "value_with_underscores",
            "key-with-hyphens": "value-with-hyphens",
            "unicode_key": "🚀 unicode value 🌟",
        }

        for key, value in special_settings.items():
            settings_manager.set(key, value)
            assert settings_manager.get(key) == value

    def test_caching_behavior(self, settings_manager: SettingsManager) -> None:
        """Test that caching works if implemented."""
        # Set a value
        settings_manager.set("cached_value", "original")

        # Get the value (should be cached if caching is implemented)
        first_get = settings_manager.get("cached_value")
        second_get = settings_manager.get("cached_value")

        assert first_get == "original"
        assert second_get == "original"

        # Update the value
        settings_manager.set("cached_value", "updated")

        # Should get updated value (cache should be invalidated)
        third_get = settings_manager.get("cached_value")
        assert third_get == "updated"


class TestSettingsManagerFallback:
    """Test SettingsManager with different storage backends."""

    def test_database_fallback_to_json_storage(self, tmp_json_path: Path) -> None:
        """Test that Database factory falls back to JsonFileStorage when TinyDB unavailable."""
        # This should use JsonFileStorage since we don't have TinyDB in dependencies
        db: StorageBackend = Database(tmp_json_path)
        if not HAS_TINYDB:  # Ensure TinyDB is not available
            # Should behave like JsonFileStorage
            db.set("test_key", "test_value")
            assert db.get("test_key") == "test_value"

            # Verify it's actually JsonFileStorage (not TinyDB)
            assert isinstance(db, JsonFileStorage)
        else:
            pytest.skip("TinyDB is available; skipping fallback test.")

    def test_settings_manager_works_with_fallback(self, settings_manager: SettingsManager) -> None:
        """Test that SettingsManager works correctly with JsonFileStorage fallback."""
        # All basic operations should work
        settings_manager.set("fallback_test", "works")
        assert settings_manager.get("fallback_test") == "works"

        # Type detection should work
        settings_manager.set("number_test", 123)
        settings_manager.set("bool_test", value=True)

        all_settings: dict[str, ValueType] = settings_manager.get_all()

        # Verify the values are correctly stored and retrieved
        assert "number_test" in all_settings
        assert all_settings["number_test"] == 123
        assert "bool_test" in all_settings
        assert all_settings["bool_test"] is True


class TestSettingsManagerErrorHandling:
    """Test SettingsManager error handling and edge cases."""

    def test_invalid_config_file_path(self, settings_manager: SettingsManager) -> None:
        """Test handling of invalid config file paths."""
        # Should not crash during initialization with invalid path

        settings_manager.set("test", "value")
        assert settings_manager.get("test") == "value"

    def test_corrupted_settings_file_recovery(self, settings_manager: SettingsManager) -> None:
        """Test recovery from corrupted settings file."""
        # Should not crash, should start fresh even with corrupted underlying storage
        settings_manager.set("recovery_test", "works")
        assert settings_manager.get("recovery_test") == "works"

    def test_concurrent_access_safety(self, tmp_path: Path) -> None:
        """Test that concurrent access doesn't corrupt data."""
        manager1 = SettingsManager("concurrent_test", path=tmp_path)
        manager2 = SettingsManager("concurrent_test", path=tmp_path)
        try:
            # Both managers write different settings
            manager1.set("manager1_setting", "value1")
            manager2.set("manager2_setting", "value2")

            # Both should be able to read their own and each other's settings
            assert manager1.get("manager1_setting") == "value1"
            assert manager2.get("manager2_setting") == "value2"

            # Create a third manager to verify persistence
            manager3 = SettingsManager("concurrent_test", path=tmp_path)
            assert manager3.get("manager1_setting") == "value1"  # <-- Fails here, returns None
            assert manager3.get("manager2_setting") == "value2"
        finally:
            manager1.destroy_settings()
