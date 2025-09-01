"""The dependency injection container for the application."""

from __future__ import annotations

from contextlib import contextmanager
from os import getenv
from typing import TYPE_CHECKING, Any

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Resource
from typer import Typer

from bear_utils.cli.typer_bridge import TyperBridge
from bear_utils.logger_manager import ConsoleLogger as Console, LogLevel
from zapper._internal._info import _METADATA

if TYPE_CHECKING:
    from collections.abc import Generator

    from bear_utils.config.config_manager import ConfigManager
    from zapper.config import AppConfig


@contextmanager
def get_config(env_override: str | None = None) -> Generator[AppConfig, Any]:
    """Context manager to get the application configuration."""
    from zapper.config import get_config_manager  # noqa: PLC0415

    env: str = getenv(_METADATA.env_variable, "prod")
    if env_override is not None:
        env = env_override
    config_manager: ConfigManager[AppConfig] = get_config_manager(env=env)
    yield config_manager.config


@contextmanager
def get_console(config: AppConfig) -> Generator[Console, Any]:
    """Context manager to get a console instance."""
    console = Console(name=_METADATA.name, level=LogLevel.INFO if not config.environment.debug else LogLevel.VERBOSE)
    try:
        yield console
    finally:
        console.exit()


@contextmanager
def get_typer_app(name: str, help_text: str) -> Generator[Typer, Any]:
    """Context manager to get a Typer application instance."""
    typer_app = Typer(
        name=name,
        help=help_text,
        rich_markup_mode="rich",
        no_args_is_help=True,
    )
    yield typer_app


@contextmanager
def get_typer_bridge(typer_app: Typer, console: Console) -> Generator[TyperBridge, Any]:
    """Context manager to get a TyperBridge instance."""
    bridge = TyperBridge(typer_app=typer_app, console=console, is_primary=True)
    yield bridge


class Container(DeclarativeContainer):
    """Dependency Injection container for the application."""

    typer_app = Resource(
        get_typer_app,
        name=_METADATA.name,
        help_text=f"[bold bright_green]{_METADATA.name}[/bold bright_green] - Command-line interface",
    )
    config = Resource(get_config)
    console = Resource(get_console, config=config)
    typer_bridge = Resource(get_typer_bridge, typer_app=typer_app, console=console)


container = Container()
