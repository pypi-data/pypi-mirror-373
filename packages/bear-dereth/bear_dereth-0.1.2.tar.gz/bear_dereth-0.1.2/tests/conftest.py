"""Configuration for the pytest test suite."""

from os import environ

from bear_dereth import _METADATA

environ[f"{_METADATA.env_variable}"] = "test"
