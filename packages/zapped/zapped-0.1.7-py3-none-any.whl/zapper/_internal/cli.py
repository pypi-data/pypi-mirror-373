# - When you run `python -m zapper` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `zapper.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `zapper.__main__` in `sys.modules`.
from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Annotated

from dependency_injector.wiring import Provide, inject
from typer import Argument, Option, Typer, echo

from bear_utils.cli._args import args_parse
from bear_utils.cli._get_version import cli_bump
from bear_utils.constants import ExitCode
from zapper._internal._info import _METADATA
from zapper._internal.cli_interactive import _InteractiveCLI
from zapper._internal.debug import _print_debug_info
from zapper.di import Container, container

if TYPE_CHECKING:
    from bear_utils.cli.typer_bridge import TyperBridge


@inject
def _typer_app(typer_app: Typer = Provide[Container.typer_app]) -> Typer:
    """Get the Typer application instance."""
    return typer_app


@inject
def _get_bridge(typer_bridge: TyperBridge = Provide[Container.typer_bridge]) -> TyperBridge:
    """Get the TyperBridge instance."""
    return typer_bridge


container.wire(modules=[__name__])

_cli: TyperBridge = _get_bridge()


def _debug_info_callback(value: bool) -> None:
    """Print debug information and exit."""
    if value:
        _print_debug_info()
        raise SystemExit


def _version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        echo(_METADATA.full_version, color=False)


@_cli.callback()
def _app_callback(
    version: Annotated[
        bool,
        Option("-V", "--version", callback=_version_callback, help="Show version information."),
    ] = False,
) -> None:
    """Zapper command-line interface."""


@_cli.command("interactive", help="Start interactive mode.")
def _interactive() -> ExitCode:
    """Start interactive mode."""
    echo("Starting interactive mode...")
    interactive_cli: _InteractiveCLI = _InteractiveCLI()
    return interactive_cli.run()


@_cli.command("version", hidden=True, ignore=True)
def _get_version() -> ExitCode:
    """CLI command to get the version of the package."""
    echo(_METADATA.version, color=False)
    return ExitCode.SUCCESS


@_cli.command(
    "bump",
    help="Bump the version of the package.",
    usage_text="zapper bump [major|minor|patch]",
    ignore=True,
    hidden=True,
)
def _bump_version(bump_type: Annotated[str, Argument(help="◉ Bump type (major, minor, patch)")]) -> ExitCode:
    """CLI command to bump the version of the package."""
    return cli_bump([bump_type, _METADATA.name, _METADATA.version])


@_cli.command(
    "debug_info",
    help="Print debug information.",
    usage_text="zapper debug_info [--no-color]",
    ignore=True,
    hidden=True,
)
def _debug_info(
    no_color: Annotated[
        bool,
        Option("--no-color", "-n", help="Disable colored output."),
    ] = False,
) -> ExitCode:
    """CLI command to print debug information."""
    _print_debug_info(no_color=no_color)
    return ExitCode.SUCCESS


@args_parse()
def main(args: list[str]) -> ExitCode:
    """Entry point for the CLI application.

    This function is executed when you type `zapper` or `python -m zapper`.

    Parameters:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """
    arguments: list[str] = args
    if not args:
        arguments: list[str] = ["--help"]

    try:
        _typer_app()(arguments, prog_name=_METADATA.name)
        return ExitCode.SUCCESS
    except SystemExit as e:
        exit_code = e.code
        if isinstance(exit_code, int):
            raise SystemExit(exit_code) from e
        return ExitCode.SUCCESS
    except Exception:
        return ExitCode.FAILURE


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
