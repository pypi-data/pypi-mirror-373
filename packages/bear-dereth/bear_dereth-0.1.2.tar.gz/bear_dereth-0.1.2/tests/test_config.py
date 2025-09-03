from collections.abc import Callable, Generator
import os
from pathlib import Path
import tempfile
from typing import Any
from unittest.mock import patch

from pydantic import BaseModel
import pytest

from bear_dereth.config.config_manager import ConfigManager, Sources, nullable_string_validator
from bear_dereth.models.type_fields import PathModel


class MockDatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    username: str = "app"


class MockLoggingConfig(BaseModel):
    level: str = "INFO"
    file: PathModel = PathModel()
    _validate_file: Callable[..., str | None] = nullable_string_validator("file")


class MockAppConfig(BaseModel):
    database: MockDatabaseConfig = MockDatabaseConfig()
    logging: MockLoggingConfig = MockLoggingConfig()
    debug: bool = False


class TestConfigManager:
    @pytest.fixture
    def temp_config_dir(self) -> Generator[Path, Any]:
        """Create a temporary directory for config files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def config_manager(self, temp_config_dir: Path) -> ConfigManager[MockAppConfig]:
        """Create a ConfigManager with temporary paths."""
        config_paths: list[Path] = [temp_config_dir / "default.toml"]
        manager: ConfigManager[MockAppConfig] = ConfigManager[MockAppConfig](
            config_model=MockAppConfig, program_name="TEST_APP", config_paths=config_paths, env="test"
        )

        if hasattr(manager, "load"):
            delattr(manager, "load")
        manager._config = None
        return manager

    def test_env_vars(self) -> None:
        """Debug environment variable processing."""
        with patch.dict(os.environ, {"TEST_APP_DATABASE_HOST": "env.db", "TEST_APP_DEBUG": "true"}):
            config_manager: ConfigManager[MockAppConfig] = ConfigManager[MockAppConfig](
                config_model=MockAppConfig, program_name="TEST_APP", config_paths=[], env="test"
            )
            config: MockAppConfig = config_manager.config
            assert config.database.host == "env.db"
            assert config.debug is True

    def test_loads_default_config_when_no_files_exist(self, config_manager: ConfigManager[MockAppConfig]):
        """Test that default values are used when no config files exist."""
        config: MockAppConfig = config_manager.config

        assert config.database.host == "localhost"
        assert config.database.port == 5432
        assert config.debug is False

    def test_loads_toml_file_config(self, temp_config_dir: Path):
        """Test loading configuration from TOML file."""
        config_file: Path = temp_config_dir / "default.toml"

        config_file.write_text("""
        debug = true

        [database]
        host = "production.db"
        port = 3306
        """)

        assert config_file.exists()

        config_manager: ConfigManager[MockAppConfig] = ConfigManager[MockAppConfig](
            config_model=MockAppConfig, program_name="TEST_APP", config_paths=[config_file], env="test"
        )

        config: MockAppConfig = config_manager.config
        assert config.database.host == "production.db"
        assert config.debug is True

    def test_environment_variable_overrides(self, temp_config_dir: Path) -> None:  # noqa: ARG002
        """Test that environment variables override file and default settings."""
        with patch.dict(os.environ, {"TEST_APP_DATABASE_HOST": "env.db", "TEST_APP_DEBUG": "true"}):
            config_manager: ConfigManager[MockAppConfig] = ConfigManager[MockAppConfig](
                config_model=MockAppConfig,
                program_name="test_app",
                config_paths=[],
                env="test",
            )
            config: MockAppConfig = config_manager.config
            assert config.database.host == "env.db"

    def test_env_value_conversion(self, config_manager: ConfigManager[MockAppConfig]):
        """Test environment variable type conversion."""
        with patch.dict(os.environ, {"TEST_APP_DATABASE_PORT": "9999", "TEST_APP_DEBUG": "false"}):
            config: MockAppConfig = config_manager.config

            assert config.database.port == 9999
            assert isinstance(config.database.port, int)
            assert config.debug is False
            assert isinstance(config.debug, bool)

    def test_has_config_method(self, config_manager: ConfigManager[MockAppConfig]):
        """Test the has_config method."""
        assert config_manager.has_config(MockDatabaseConfig) is True
        assert config_manager.has_config(MockLoggingConfig) is True

        class NonExistentConfig(BaseModel):
            pass

        assert config_manager.has_config(NonExistentConfig) is False

    def test_get_config_method(self, config_manager: ConfigManager[MockAppConfig]):
        """Test the get_config method returns correct types."""
        db_config: MockDatabaseConfig | None = config_manager.get_config(MockDatabaseConfig)
        assert isinstance(db_config, MockDatabaseConfig)
        assert db_config.host == "localhost"

        logging_config: MockLoggingConfig | None = config_manager.get_config(MockLoggingConfig)
        assert isinstance(logging_config, MockLoggingConfig)
        assert logging_config.level == "INFO"

    def test_config_reload(self, temp_config_dir: Path):
        """Test that reload picks up config changes."""
        config_file: Path = temp_config_dir / "default.toml"
        config_file.write_text("debug = false")

        config_manager: ConfigManager[MockAppConfig] = ConfigManager[MockAppConfig](
            config_model=MockAppConfig, program_name="test_app", config_paths=[config_file], env="test"
        )
        initial_config: MockAppConfig = config_manager.config
        assert initial_config.debug is False
        config_file.write_text("debug = true")
        reloaded_config: MockAppConfig = config_manager.reload()
        assert reloaded_config.debug is True

    def test_nullable_string_validator(self) -> None:
        """Test the nullable string validator."""

        class TestModel(BaseModel):
            optional_field: str | None = None
            _validate_field: Callable[..., str | None] = nullable_string_validator("optional_field")

        # Test null conversion
        model1 = TestModel(optional_field="null")
        assert model1.optional_field is None

        model2 = TestModel(optional_field="none")
        assert model2.optional_field is None

        model3 = TestModel(optional_field="")
        assert model3.optional_field is None

        # Test regular string
        model4 = TestModel(optional_field="actual_value")
        assert model4.optional_field == "actual_value"

    def test_deep_merge_functionality(self, config_manager: ConfigManager[MockAppConfig]):
        """Test that deep merge works correctly."""
        base: dict[str, Any] = {"a": {"b": 1, "c": 2}, "d": 3}
        override: dict[str, Any] = {"a": {"b": 99}, "e": 4}

        result: dict[str, Any] = config_manager._deep_merge(base, override)

        assert result["a"]["b"] == 99  # Overridden
        assert result["a"]["c"] == 2  # Preserved
        assert result["d"] == 3  # Preserved
        assert result["e"] == 4  # Added

    def test_config_sources_tracking(self, temp_config_dir: Path, config_manager: ConfigManager[MockAppConfig]):
        """Test that config sources are properly tracked."""
        config_file: Path = temp_config_dir / "default.toml"
        config_file.write_text('[database]\nhost = "test"')
        config_manager.reload()
        sources: Sources = config_manager.config_sources()

        assert len(sources.files_loaded) == 1
        assert "default.toml" in sources.files_loaded[0]["path"]
        assert "database" in sources.files_loaded[0]["keys"]

    def test_default_config_generation(self, tmp_path: Path, config_manager: ConfigManager[MockAppConfig]):
        """Test that default config generation works, this outputs a file"""
        default_file: Path = tmp_path / "default.toml"
        config_manager.create_default_config(default_file)
        assert default_file.exists()
        content: str = default_file.read_text()
        assert 'host = "localhost"' in content
        assert 'level = "INFO"' in content
        assert "debug = false" in content
        assert "port = 5432" in content
        assert 'file = "null"' in content
