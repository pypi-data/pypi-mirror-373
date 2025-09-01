"""Configuration management for Zapper."""

from collections.abc import Callable

from pydantic import BaseModel, ConfigDict

from bear_utils.config import ConfigManager
from zapper._common import SORTING_CHOICES
from zapper._internal._info import _ProjectMetadata
from zapper._internal.debug import _METADATA


class FrozenModel(BaseModel):
    """A Pydantic model that is immutable (frozen)."""

    model_config = ConfigDict(frozen=True)


class ZapConfig[Target_Type](BaseModel):
    source_input: str | tuple[str, ...]
    src: str
    split_count: int = 0
    replace: str = ""
    sep: str | None = None
    func: Callable[[str], Target_Type] = str  # type: ignore[type-arg]
    strict: bool = True
    regex: bool = False
    filter_start: bool = False
    filter_end: bool = False
    atomic: bool = False
    sorting: SORTING_CHOICES = "length"

    def update_from_args(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class Environment(FrozenModel):
    """Environment configuration for the application."""

    name: str = "test"
    debug: bool = False

    @property
    def is_prod(self) -> bool:
        """Check if the environment is production."""
        return self.name == "prod"

    @property
    def is_dev(self) -> bool:
        """Check if the environment is development."""
        return self.name == "dev"

    @property
    def is_test(self) -> bool:
        """Check if the environment is testing."""
        return self.name == "test"


class Metadata(FrozenModel):
    """Metadata about the application."""

    info_: _ProjectMetadata = _METADATA

    def __getattr__(self, name: str) -> str:
        """Delegate attribute access to the internal _ProjectMetadata instance."""
        return getattr(self.info_, name)


class AppConfig(FrozenModel):
    """Application configuration model."""

    environment: Environment = Environment()
    metadata: Metadata = Metadata()


def get_config_manager(env: str = "prod") -> ConfigManager[AppConfig]:
    """Get the configuration manager for the application."""
    return ConfigManager[AppConfig](config_model=AppConfig, program_name=_METADATA.name, env=env)


__all__ = [
    "AppConfig",
    "Environment",
    "get_config_manager",
]
