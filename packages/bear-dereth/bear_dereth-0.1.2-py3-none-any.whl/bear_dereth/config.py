"""Configuration management for Bear Dereth."""

from bear_dereth._internal._info import _ProjectMetadata
from bear_dereth._internal.debug import _METADATA
from bear_dereth.config.config_manager import ConfigManager
from bear_dereth.tools.freezing import FrozenModel


class Metadata(FrozenModel):
    """Metadata about the application."""

    info_: _ProjectMetadata = _METADATA

    def __getattr__(self, name: str) -> str:
        """Delegate attribute access to the internal _ProjectMetadata instance."""
        return getattr(self.info_, name)


class AppConfig(FrozenModel):
    """Application configuration model."""

    env: str = "prod"
    debug: bool = False
    metadata: Metadata = Metadata()


def get_config_manager(env: str = "prod") -> ConfigManager[AppConfig]:
    """Get the configuration manager for the application."""
    return ConfigManager[AppConfig](config_model=AppConfig, program_name=_METADATA.name, env=env)


__all__ = ["AppConfig", "Metadata", "get_config_manager"]
