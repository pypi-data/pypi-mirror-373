from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

import click

if TYPE_CHECKING:
    import docker

import tomlkit

from kaas_cli.types import KaasCliException

from .config import DEFAULT_DIRECTORY


def get_foundry_out_dir() -> str:
    kontrol_toml_path, foundry_toml_path = find_kontrol_configs()
    profile = os.environ.get('FOUNDRY_PROFILE')
    click.echo(f"env FOUNDRY_PROFILE={profile}")
    if profile is None:
        profile = 'default'
    click.echo(f"Using Foundry profile: {profile}")
    try:
        with open(foundry_toml_path, 'r') as file:
            parsed_toml: dict[str, Any] = tomlkit.load(file)
        if 'profile' in parsed_toml and isinstance(parsed_toml['profile'], dict):
            profile_config = parsed_toml['profile'].get(profile)
            if isinstance(profile_config, dict) and 'out' in profile_config:
                click.echo(f"Using Foundry out directory: {profile_config['out']}")
                return profile_config['out']
        click.echo("Falling back to default 'out' value")
        return DEFAULT_DIRECTORY
    except Exception as e:
        click.echo(f"Error parsing Foundry profile: {e}")
        raise KaasCliException(f"Error reading foundry.toml: {e}") from e


def find_kontrol_configs() -> tuple[str, str]:
    """
    Check if kontrol.toml and foundry.toml or just 'foundry.toml' exist below the current directory.
    Use chdir to change to the directory containing the kontrol.toml and foundry.toml files
    then if they do exist, return the path, otherwise return None

    Returns:
        str: Path to the directory containing the kontrol.toml and foundry.toml files
    """
    # Check if kontrol.toml and foundry.toml or just 'foundry.toml' exist below the current directory
    kontrol_toml = find_file('kontrol.toml')
    foundry_toml = find_file('foundry.toml')
    kontrol_exists = os.path.exists(kontrol_toml)
    foundry_exists = os.path.exists(foundry_toml)

    if not foundry_exists:
        click.echo("No foundry.toml file found...")
        click.echo("  Warning: This is Advanced Kontrol usage. Running kontrol with default settings.")
        click.echo("    If you wish to modify runtime settings. Use kontrol --parameters.")
    else:
        click.echo("Found foundry.toml file.")
    return kontrol_toml if kontrol_exists else "", foundry_toml if foundry_exists else ""


def find_file(file_name: str) -> str:
    """
    Check if the file exists below the current directory
    if it does, return the path to the file, otherwise return None

    Returns:
        str: Path to the file
    """
    for root, _dirs, files in os.walk("."):
        if file_name in files:
            return os.path.relpath(root) + '/' + file_name
    return ""


def validate_config_location(test_root: str, kontrol_toml: str, foundry_toml: str) -> None:
    if test_root:
        if not os.path.isdir(test_root):
            raise KaasCliException("Provided --test-root/-tr directory does not exist.")
    if not os.path.isfile(foundry_toml):
        click.echo(
            click.style(
                """Warning: No foundry.toml file found in test root. \n
                    Refine Kontrol execution using 'foundry.toml'. \n
                    OR using `kontrol build/prove --parameters`""",
                fg='yellow',
            )
        )
    if not os.path.isfile(kontrol_toml):
        click.echo(
            click.style(
                """Warning: No kontrol.toml file found in the current directory or subdirectories. \n
                  Refine Kontrol execution using 'kontrol.toml'. \n
                  OR using kontrol --parameters""",
                fg='yellow',
            )
        )


def exec_docker_command(container: docker.models.containers.Container, command: str) -> tuple[int, list[bytes]]:
    exec_id_info = container.client.api.exec_create(  # type: ignore[union-attr]
        container.id,
        command,
        tty=True,
    )
    exec_id = exec_id_info['Id']
    output_stream = container.client.api.exec_start(exec_id, tty=True, stream=True)  # type: ignore[union-attr]

    for log in output_stream:
        click.echo(log.decode('utf-8'))

    exec_info = container.client.api.exec_inspect(exec_id)  # type: ignore[union-attr]
    return_code = exec_info['ExitCode']
    return return_code, [log.decode('utf-8') for log in output_stream]


def escape_shell_args(args: str) -> str:
    """
    Escape special characters in shell arguments to prevent syntax errors.
    """
    # Replace single quotes with double quotes
    escaped_args = args.replace("'", '"')
    return escaped_args
