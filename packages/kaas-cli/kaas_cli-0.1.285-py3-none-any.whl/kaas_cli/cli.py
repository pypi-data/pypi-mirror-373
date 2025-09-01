from __future__ import annotations

import json
import sys
from dataclasses import asdict
from typing import TYPE_CHECKING

import click
import click.exceptions

from kaas_cli import __version__

from .client import KaasClient
from .config import DEFAULT_DIRECTORY, DEFAULT_TOKEN, SERVER_URL, CustomHelpOption
from .run_forge import RunForge
from .run_kontrol import RunKontrol
from .types import KontrolVersion
from .utils import get_foundry_out_dir

if TYPE_CHECKING:
    from click.core import Context


@click.group()
@click.version_option(version=__version__, prog_name='kaas-cli')
@click.pass_context
def cli(
    ctx: Context,
) -> None:
    """KaaS Command Line Interface"""
    ctx.ensure_object(dict)
    ctx.obj["client"] = KaasClient(
        url=SERVER_URL,
    )


@cli.command(
    cls=CustomHelpOption,
    help="Upload proofs to the remote server. VAULT_SPEC should be in the format <ORG_NAME>/<VAULT_NAME>:<TAG>",
)
@click.argument('vault_spec', required=True)
@click.option(
    "-d",
    "--directory",
    default='',
    show_default=True,
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    help="Directory containing proofs to upload",
)
@click.option("--url", "-u", required=False, default=SERVER_URL, show_default=True, help="Server URL")
@click.option("--token", "-t", required=False, default=DEFAULT_TOKEN, help="Personal access key for vault")
@click.option("--tag", required=False, help="Tag of the version to upload")
@click.option("--verbose", "-v", is_flag=True, default=False, help="Show verbose output")
@click.option("--job-id", required=False, help="The id of job that is uploading this", default=None)
@click.pass_context
def upload(
    ctx: Context,
    vault_spec: str,
    directory: str,
    url: str,
    token: str | None,
    tag: str | None,
    verbose: bool,
    job_id: str | None,
) -> None:
    try:
        org_name, vault_and_tag = vault_spec.split('/')
        if not ':' in vault_and_tag:
            if tag is None:
                raise ValueError("No tag defined with --tag or in Vault Specification")
            vault_name = vault_and_tag
            tag_name = tag
        else:
            vault_name, tag_name = vault_and_tag.split(':')
    except ValueError:
        click.echo("Invalid vault specification. Use the format orgName/vaultName:tag or @orgName/vaultName:tag")
        return

    try:
        ctx.ensure_object(dict)
        client: KaasClient = KaasClient(url=url, token=token, vault=vault_name, org=org_name)
        ctx.obj["client"] = client
        if not directory:
            directory = get_foundry_out_dir()
        response_message = client.upload_files_s3(
            directory=directory, tag=tag_name or tag, verbose=verbose, job_id=job_id
        )
        if verbose:
            click.echo(response_message)
    except Exception as e:
        click.echo(e)
        sys.exit(1)


@cli.command(
    cls=CustomHelpOption,
    help="Download proofs from the remote server. VAULT_SPEC should be in the format <ORG_NAME>/<VAULT_NAME>:<TAG> or @<ORG_NAME>/<VAULT_NAME>:<TAG>",
)
@click.argument("vault_spec", required=True)
@click.option(
    "-d",
    "--directory",
    default='',
    show_default=True,
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    help="Directory to save downloaded proofs",
)
@click.option("--url", "-u", default=SERVER_URL, show_default=True, help="Server URL")
@click.option("--token", "-t", default=DEFAULT_TOKEN, help="Personal access key for vault")
@click.option("--verbose", "-v", is_flag=True, default=False, help="Show verbose output")
@click.pass_context
def download(
    ctx: Context,
    vault_spec: str,
    directory: str,
    url: str,
    token: str | None,
    verbose: bool,
) -> None:
    try:
        org_name, vault_and_tag = vault_spec.split('/')
        vault_name, tag_name_or_file_name = vault_and_tag.split(':')
    except ValueError:
        click.echo("Invalid vault specification. Use the format orgName/vaultName:tag or @orgName/vaultName:tag")
        return None

    if not org_name or not vault_name:
        click.echo(
            "Invalid vault specification. Use the format orgName/vaultName:tag or @orgName/vaultName:tag",
        )
        return None
    ctx.ensure_object(dict)
    client: KaasClient = KaasClient(url=url, token=token, vault=vault_name, org=org_name)
    ctx.obj["client"] = client
    if not directory:
        directory = get_foundry_out_dir()
    if not tag_name_or_file_name:
        message = client.download_latest_version(org_name, vault_name, target_directory=directory, verbose=verbose)
        if verbose:
            click.echo(message)
        return None

    try:
        message = client.download_version_or_tag(
            org_name, vault_name, tag_name_or_file_name, target_directory=directory, verbose=verbose
        )
        if verbose:
            click.echo(message)
        return None
    except ValueError:
        click.echo("Invalid vault specification. Use the format orgName/vaultName:tag")
        return None


@cli.command(cls=CustomHelpOption, help="Say hello.")
@click.option("-n", "--name", default="World", show_default=True, help="Name to say hello to")
@click.pass_context
def hello(ctx: Context, name: str) -> None:
    client: KaasClient = ctx.obj["client"]
    client.hello(name=name)


@cli.command(cls=CustomHelpOption, help="Login to the system.")
@click.pass_context
def login(ctx: Context) -> None:
    client: KaasClient = ctx.obj["client"]
    data = client.login()
    click.echo(f"Your user code: {data.user_code}")
    click.echo(f"Open the link and type your code {data.verification_uri}")
    click.echo("Then hit 'enter'")
    input_value = click.prompt("Press Enter to continue or type 'q' to quit", default="", show_default=False)
    if input_value.lower() == 'q':
        click.echo("You left authentication")
        sys.exit(1)
        return
    click.echo("You pressed Enter. The application continues...")
    confirm_success = client.confirm_login(data.device_code).success
    if not confirm_success:
        click.echo("Authentication failed")
        sys.exit(1)
        return
    click.echo("Access token received. We store it in cache folder")


@cli.command(cls=CustomHelpOption, help="List local proofs.", aliases=['l', 'ls'])
@click.option(
    "-d",
    "--directory",
    default=DEFAULT_DIRECTORY,
    show_default=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Directory to list local proofs",
)
@click.option("--remote", is_flag=True, help="List remote proofs instead of local proofs", default=False)
@click.pass_context
def list(ctx: Context, directory: str = DEFAULT_DIRECTORY, remote: bool = False) -> None:
    client: KaasClient = ctx.obj["client"]
    if remote:
        proofs = client.list_remote()
    else:
        proofs = client.list_local_proofs(directory=directory)
    if not proofs:
        click.echo('No proofs found')
    for proof in proofs:
        click.echo(proof)


@cli.command(cls=CustomHelpOption, help="List remote vaults.")
@click.option("--url", "-u", default=SERVER_URL, show_default=True, help="Server URL")
@click.option("--token", "-t", default=DEFAULT_TOKEN, help="Personal access key for vault")
@click.pass_context
def list_vaults(ctx: Context, token: str, url: str) -> None:
    client: KaasClient = KaasClient(url=url, token=token)
    vaults = client.list_vaults()
    for vault in vaults:
        if isinstance(vault, dict):
            org_name = vault.get('organization', {}).get('name', 'Unknown')
            vault_name = vault.get('name', 'Unknown')
            click.echo(f"{org_name}/{vault_name}")
        else:
            click.echo("Invalid vault structure received.")


@cli.command(cls=CustomHelpOption, help="List you organizations.")
@click.option("--url", "-u", default=SERVER_URL, show_default=True, help="Server URL")
@click.option("--token", "-t", default=DEFAULT_TOKEN, help="Personal access key for vault")
@click.pass_context
def list_orgs(ctx: Context, token: str, url: str) -> None:
    client: KaasClient = KaasClient(url=url, token=token)
    orgs = client.list_orgs()
    for org in orgs:
        if isinstance(org, dict):
            org_name = org.get('name', 'Unknown')
            click.echo(f"{org_name}")
        else:
            click.echo("Invalid vault structure received.")


@cli.command(
    cls=CustomHelpOption,
    name="list-caches",
    help="""List remote caches.\n
    $ kaas-cli list-caches <ORG_NAME>/<VAULT_NAME>""",
)
@click.argument("org_vault", required=True)
@click.option("--url", "-u", default=SERVER_URL, show_default=True, help="Server URL")
@click.option("--token", "-t", default=DEFAULT_TOKEN, help="Personal access key for vault")
@click.pass_context
def list_caches(ctx: Context, org_vault: str, token: str, url: str) -> None:
    click.echo(f"Default Token: {DEFAULT_TOKEN}")
    client: KaasClient = KaasClient(url=url, token=token)
    org_name, vault_name = org_vault.split('/')
    caches = client.list_caches(org_name, vault_name)
    click.echo(json.dumps([asdict(cache) for cache in caches], indent=2))


@cli.command(cls=CustomHelpOption, name="check-auth", help="Check authentication status.")
@click.option("--url", "-u", default=SERVER_URL, show_default=True, help="Server URL")
@click.option("--token", "-t", default=DEFAULT_TOKEN, help="Personal access key for vault")
@click.pass_context
def check_auth(ctx: Context, token: str, url: str) -> None:
    client: KaasClient = KaasClient(url=url, token=token)
    error_message = f"Authentication failed, please use {click.style('--token', fg='red')} flag or {click.style('kaas-cli login', fg='red')} to authenticate."
    try:
        is_authenticated = client.check()
        if is_authenticated:
            click.echo("You are currently authenticated.")
        else:
            click.echo(error_message)
            sys.exit(1)
    except Exception:
        click.echo(error_message)
        sys.exit(1)


@cli.command(cls=CustomHelpOption, name="logout", help="Log out from the system.")
@click.pass_context
def logout(ctx: Context) -> None:
    client: KaasClient = ctx.obj["client"]
    logout_success = client.logout()
    if logout_success:
        click.echo("You have been logged out successfully.")
    else:
        click.echo("Logout failed. You may not be logged in.")


@cli.command(
    cls=CustomHelpOption,
    name="run",
    help="Run Proofs locally, in a container or remotely on kaas provided compute machines",
)
@click.option(
    "--mode",
    "-m",
    required=False,
    default="local",
    show_default=True,
    help="Mode to run the command in: local, remote, or container",
    type=click.Choice(['local', 'remote', 'container'], case_sensitive=False),
)
@click.option(
    "--test-mode",
    "-tm",
    required=False,
    default="kontrol",
    show_default=True,
    type=click.Choice(['kontrol', 'forge'], case_sensitive=False),
    help="Tool to run tests with: kontrol or forge",
)
@click.option(
    "--foundry-version",
    "-fv",
    required=False,
    default="",
    show_default=True,
    help="Foundry version to use (only used with test-mode forge)",
)
@click.option(
    "--foundry-docker-image",
    "-fdi",
    required=False,
    default="",
    help="Docker image to use for running Foundry in container mode",
)
@click.option(
    "--watch",
    "-w",
    required=False,
    default=False,
    is_flag=True,
    help="Watch the job execution status. Wait until the job is completed",
)
@click.option(
    "--build-only",
    "-bo",
    required=False,
    default=False,
    is_flag=True,
    help="Only run 'kontrol build' but not 'kontrol prove'",
)
@click.option(
    "--prove-only-profile",
    "-pop",
    required=False,
    help="Only run 'kontrol prove' but not 'kontrol build'. Use this option to run 'kontrol prove' on a previously built proof. Provide the profile name to run the proof.",
    type=str,
    default="",
)
@click.option(
    "--kontrol-version",
    "-kv",
    required=False,
    default="v0.0.0",
    show_default=True,
    help="Version of Kontrol to run",
    type=KontrolVersion(),
)
@click.option(
    "--kontrol-docker-image",
    "-kdi",
    required=False,
    help="Docker image to use for running Kontrol in container mode",
    type=str,
    default="",
)
@click.option(
    "--url",
    "-u",
    required=False,
    default=SERVER_URL,
    show_default=True,
    help="API Server URL",
)
@click.option(
    "--vault-spec",
    "-vs",
    "vault",
    required=False,
    help="Organization and vault to use for remote mode. VAULT_SPEC should be in the format <ORG_NAME>/<VAULT_NAME>",
)
@click.option(
    "--token",
    "-t",
    required=False,
    help="Personal access key for vault. See https://kaas.runtimeverification.com/app/profile/keys",
)
@click.option(
    "--branch",
    "-b",
    required=False,
    help="Git repository branch to use for remote mode",
)
@click.option(
    "--test-root",
    "-tr",
    required=False,
    help="Test folder root path relative to the project root.",
    type=str,
    default="",
)
@click.option("--extra-build-args", "-eb", required=False, help="Extra arguments to build the proof")
@click.option("--extra-test-args", "-et", required=False, help="Extra arguments to 'forge test' command")
@click.option("--extra-prove-args", "-ep", required=False, help="Extra arguments to pass to Kontrol's prove command")
@click.pass_context
def run(
    ctx: Context,
    mode: str,
    test_mode: str,
    foundry_version: str,
    foundry_docker_image: str,
    watch: bool,
    build_only: bool,
    prove_only_profile: str,
    kontrol_version: KontrolVersion,
    kontrol_docker_image: str,
    url: str,
    vault: str,
    token: str,
    branch: str,
    test_root: str,
    extra_build_args: str,
    extra_test_args: str,
    extra_prove_args: str,
) -> None:
    """
    When change the code in this function, please update the gitbook documentation
    https://github.com/runtimeverification/gitbook-kaas
    """
    click.echo(f"Running {test_mode.capitalize()} in {mode} mode")
    if test_mode.lower() == "kontrol":
        if mode == "remote":
            if not all([vault, token, branch]):
                missing_args = []
                if not vault:
                    missing_args.append("--vault-spec VAULT_SPEC")
                if not token:
                    missing_args.append("--token PERSONAL_KEY")
                if not branch:
                    missing_args.append("--branch GIT_BRANCH")
                click.echo(f"You must provide all of the following options: {', '.join(missing_args)}")
                sys.exit(1)
            try:
                org_name, vault_name = vault.split('/')
            except ValueError:
                click.echo("Invalid vault specification. Use the format orgName/vaultName or @orgName/vaultName")
                sys.exit(1)
            ctx.ensure_object(dict)
            client: KaasClient = KaasClient(url=url, token=token, vault=vault_name, org=org_name)
            ctx.obj["client"] = client
            is_authenticated = client.check()
            if not is_authenticated:
                click.echo("You are not authenticated. Please use 'kaas-cli login' to authenticate.")
                click.echo(
                    "Check kaas token is enabled in your account. https://kaas.runtimeverification.com/app/profile/keys"
                )
                sys.exit(1)
            run_kontrol = RunKontrol(
                kontrol_version=kontrol_version,
                mode=mode,
                kontrol_docker_image=kontrol_docker_image,
                extra_build_args=extra_build_args,
                extra_prove_args=extra_prove_args,
                org_name=org_name,
                vault_name=vault_name,
                branch=branch,
                client=client,
                watch=watch,
                build_only=build_only,
                prove_only_profile=prove_only_profile,
                test_root=test_root,
            )
            if run_kontrol.run():
                click.echo("Kontrol ran successfully...")
                return None
            else:
                click.echo("An error occurred while running Kontrol")
                sys.exit(1)
        else:
            run_kontrol = RunKontrol(
                kontrol_version=kontrol_version,
                mode=mode,
                kontrol_docker_image=kontrol_docker_image,
                extra_build_args=extra_build_args,
                extra_prove_args=extra_prove_args,
                watch=watch,
                build_only=build_only,
                prove_only_profile=prove_only_profile,
                test_root=test_root,
            )
            if run_kontrol.run():
                click.echo("Kontrol ran successfully...")
                return None
            else:
                click.echo("An error occurred while running Kontrol")
                sys.exit(1)
    elif test_mode.lower() == "forge":
        if mode == "remote":
            click.echo("Remote mode for forge is not implemented yet")
            sys.exit(1)
        else:
            run_forge = RunForge(
                foundry_version=foundry_version,
                mode=mode,
                foundry_docker_image=foundry_docker_image,
                extra_build_args=extra_build_args,
                extra_test_args=extra_test_args,
                watch=watch,
                test_root=test_root,
            )
            if run_forge.run():
                click.echo("Forge ran successfully...")
                return None
            else:
                click.echo("An error occurred while running Forge")
                sys.exit(1)
    else:
        click.echo(f"Invalid test mode: {test_mode}")
        sys.exit(1)
