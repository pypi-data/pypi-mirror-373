from __future__ import annotations

from pathlib import Path
import shlex
import sys
from typing import TYPE_CHECKING, NoReturn

from dependency_injector.wiring import Provide, inject
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from rich.panel import Panel
from rich.table import Table

from bear_utils import SettingsManager
from bear_utils.cli.typer_bridge import CommandMeta, TyperBridge
from bear_utils.constants import ExitCode
from singleton_base import SingletonBase
from zapper._internal.debug import _METADATA
from zapper.di import Container

if TYPE_CHECKING:
    from bear_utils.cli.typer_bridge import CommandMeta, TyperBridge
    from bear_utils.logger_manager import BaseLogger as Console


class _InteractiveCLI(SingletonBase):
    """Interactive CLI with colorful interface using rich and prompt_toolkit."""

    @inject
    def __init__(
        self,
        console: Console = Provide[Container.console],
        typer_bridge: TyperBridge = Provide[Container.typer_bridge],
    ) -> None:
        """Initialize the InteractiveCLI with settings and command mappings."""
        self.console: Console = console
        self.bridge: TyperBridge = typer_bridge
        self.settings = SettingsManager(_METADATA.name, _METADATA.name, Path.home() / ".config" / _METADATA.name)
        self.command_history = FileHistory(f".{_METADATA.name}_cli_history")
        self.commands: dict[str, CommandMeta] = self.bridge.get_all_command_info(show_hidden=False)
        self.command_completer = WordCompleter(words=list(self.commands.keys()))

    def show_welcome(self) -> None:
        """Display welcome message."""
        welcome_panel: Panel = Panel.fit(
            renderable=f"[bold bright_green]{_METADATA.name.title()} Interactive Console[/]\n\n"
            "[dim cyan]>> Command-line interface activated <<[/]\n"
            "Enter 'help' to see available commands or 'quit' to exit",
            border_style="bright_green",
            title="INTERACTIVE CLI",
        )
        self.console.print(welcome_panel)

    def show_help(self, command_name: str | None = None) -> None:
        """Show available commands using Typer's registered commands.

        Args:
            command_name (str | None): Specific command name to show help for. If None, shows all commands.
        """
        if not self.bridge:
            self.console.error("TyperBridge not initialized!")
            return

        help_table = Table(title="Available Commands", border_style="bright_cyan", header_style="bold bright_cyan")
        help_table.add_column(header="Command", style="bold bright_green", width=15)
        help_table.add_column(header="Description", style="dim bright_white")

        commands = {}
        if command_name:
            match_command: CommandMeta | None = self.bridge.get_command_info(command_name)
            if match_command is not None:
                commands: dict[str, CommandMeta] = {command_name: match_command}
            else:
                self.console.error(f"Command '{command_name}' not found!")
                return
        else:
            commands: dict[str, CommandMeta] = self.bridge.get_all_command_info(show_hidden=False)

        for cmd_name, cmd_info in commands.items():
            help_table.add_row(cmd_name, cmd_info.help)
        self.console.print(help_table)

    def run(self) -> ExitCode:
        """Main CLI loop."""
        if self.bridge is None:
            self.console.print("[bright_red]TyperBridge not initialized! Cannot start interactive mode.[/]")
            return ExitCode.FAILURE

        self.show_welcome()

        while True:
            try:
                full_command: str = prompt(message="> ", completer=self.command_completer, history=self.command_history)

                if not full_command.strip():
                    continue

                command: str = shlex.split(full_command.strip())[0]

                if command.strip() == "help":
                    self.show_help()
                    continue

                if command.strip() in ("quit", "exit", "q", "exit()"):
                    self.quit()

                if command not in self.commands:
                    self.console.error(f"Command '{command}' not found! Type 'help' for available commands.")
                    continue

                if not self.bridge.execute_command(command_string=full_command):
                    self.console.error(f"Command failed: {command}")
            except KeyboardInterrupt:
                self.console.warning("Input 'exit' to leave interactive mode")
            except EOFError:
                break
        return self.quit()

    def quit(self) -> NoReturn:
        """Exit the application."""
        self.console.info(f"Exiting {_METADATA.name.title()}...")
        sys.exit(ExitCode.SUCCESS)
