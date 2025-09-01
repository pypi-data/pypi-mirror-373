"""Configuration for the pytest test suite."""

from os import environ

from zapper import _METADATA

environ[f"{_METADATA.env_variable}"] = "test"
