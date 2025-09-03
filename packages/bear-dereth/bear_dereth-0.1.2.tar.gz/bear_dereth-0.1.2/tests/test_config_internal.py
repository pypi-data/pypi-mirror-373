from os import getenv

from bear_dereth import _METADATA


def test_config_works() -> None:
    """Test to ensure the env was set"""
    assert getenv(_METADATA.env_variable) == "test", "Environment variable not set correctly"


def test_metadata() -> None:
    """Test to ensure metadata is correctly set."""
    assert _METADATA.name == "bear-dereth", "Metadata name does not match"
    assert _METADATA.version != "0.0.0", "Metadata version should not be '0.0.0'"
    assert _METADATA.description != "No description available.", "Metadata description should not be empty"
    assert _METADATA.project_name == "bear_dereth", "Project name does not match"
