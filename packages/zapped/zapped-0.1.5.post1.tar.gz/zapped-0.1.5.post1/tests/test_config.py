from os import getenv

from zapper import _METADATA


def test_config_works() -> None:
    """Test to ensure the env was set"""
    assert getenv(_METADATA.env_variable) == "test", "Environment variable not set correctly"


def test_metadata() -> None:
    """Test to ensure metadata is correctly set."""
    assert _METADATA.name == "zapper", "Metadata name does not match"
    assert _METADATA.version != "0.0.0", "Metadata version should not be '0.0.0'"
    assert _METADATA.description != "No description available.", "Metadata description should not be empty"
    assert _METADATA.project_name == "zapper", "Project name does not match"
