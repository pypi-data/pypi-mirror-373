from __future__ import annotations

from typing import TYPE_CHECKING, Any

import click

from .cli import cli  # Import the Click group you've defined
from .config import CustomHelpOption

if TYPE_CHECKING:
    from collections.abc import Callable


def register_command_aliases() -> None:
    # Collect aliases and their corresponding commands in a list
    aliases_to_register = []
    for _command_name, command in cli.commands.items():
        if isinstance(command, CustomHelpOption):
            # Ensure command.callback is not None before proceeding
            if command.callback is not None:
                for alias in command.aliases:
                    # Avoid adding an alias if it's already a command
                    if alias not in cli.commands:
                        # Add type assertion to ensure command.callback is not None
                        callback: Callable[..., Any] = command.callback
                        aliases_to_register.append((alias, callback))

    # Register collected aliases as commands
    for alias, callback in aliases_to_register:
        cli.command(name=alias, cls=click.Command)(callback)


def main() -> None:
    register_command_aliases()
    cli()


if __name__ == "__main__":
    main()
