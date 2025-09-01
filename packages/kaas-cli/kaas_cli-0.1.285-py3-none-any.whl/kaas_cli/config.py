import os
from typing import Any

import click
from dotenv import load_dotenv

from .constants import DEFAULT_K_OUT_FOLDER, DEFAULT_PROD_SERVER_URL

load_dotenv()

# Load environment variables from .flaskenv file
load_dotenv('.flaskenv')

DEFAULT_DIRECTORY = os.getenv('KAAS_DIRECTORY') or DEFAULT_K_OUT_FOLDER
SERVER_URL = os.getenv('KAAS_SERVER_URL') or DEFAULT_PROD_SERVER_URL
DEFAULT_PROJECT_ID = os.getenv('KAAS_ORG_VAULT')
DEFAULT_TOKEN = os.getenv('KAAS_TOKEN')


class CustomHelpOption(click.Command):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.aliases = kwargs.pop('aliases', [])
        super().__init__(*args, **kwargs)

    def format_aliases(self) -> str:
        return f"Aliases: {', '.join(repr(alias) for alias in self.aliases)}" if self.aliases else ""

    def get_short_help_str(self, limit: int = 45) -> str:
        short_help = super().get_short_help_str(limit)
        aliases_text = self.format_aliases()
        return f"{short_help}. {aliases_text}" if aliases_text else short_help

    def get_help(self, ctx: Any) -> str:
        return super().get_help(ctx)
