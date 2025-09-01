from __future__ import annotations

import logging
import os
import platform
import random
import re
import shutil
import subprocess
import sys
import time
from typing import TYPE_CHECKING, Optional

import click
import docker
import requests

if TYPE_CHECKING:
    from .client import KaasClient
    from .types import KontrolVersion

from .constants import CONFIG_LOG_PATH, KONTROL_JOB_DETAILS_URL
from .types import KaasCliException
from .utils import find_kontrol_configs, get_foundry_out_dir, validate_config_location


class RunKontrol:
    def __init__(
        self,
        kontrol_version: KontrolVersion,
        mode: str,
        kontrol_docker_image: str = "",
        extra_build_args: str = "",
        extra_prove_args: str = "",
        org_name: str = "",
        vault_name: str = "",
        branch: str = "",
        client: Optional[KaasClient] = None,
        watch: bool = False,
        build_only: bool = False,
        prove_only_profile: str = "",
        test_root: str = "",
    ):
        self.kontrol_version = kontrol_version
        self.kontrol_docker_image = kontrol_docker_image
        self.mode = mode
        self.extra_build_args = extra_build_args
        self.extra_prove_args = extra_prove_args
        self.org_name = org_name
        self.vault_name = vault_name
        self.branch = branch
        self.client = client
        self._configure_logging()
        self.watch = watch
        self.build_only = build_only
        self.prove_only_profile = prove_only_profile
        self.test_root = test_root

    def _configure_logging(self) -> None:
        """Configure logging for the application."""
        if not CONFIG_LOG_PATH.exists():
            CONFIG_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_LOG_PATH.touch()
        logging.basicConfig(
            filename=CONFIG_LOG_PATH,
            filemode='a',
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.DEBUG,
        )

    def run(
        self,
    ) -> bool:
        """
        Run Kontrol with the given version and current source code within the current directory structure.
        Execution will start and results dumped to log/console.
        True if Kontrol ran at all PERIOD. If there are errors in the proofs these will be output but that is still a success to RUN kontrol.
        Returns:
            bool: True if Kontrol ran successfully, False otherwise
        """
        if self.mode == 'container':
            return self._run_in_container()
        elif self.mode == 'local':
            return self._run_locally()
        elif self.mode == 'remote':
            return self._run_remotely()
        else:
            click.echo(f"Invalid mode: {self.mode}")
            return False

    def _run_in_container(self) -> bool:
        if not self._is_docker_installed():
            click.echo("Docker is not installed. Please install Docker to run in a container.")
            return False
        self.kontrol_version = self._get_or_set_kontrol_version()
        if self.kontrol_version == "v0.0.0":
            click.echo("Error getting latest Kontrol release and No Version Specified. Exiting...")
            sys.exit(1)
        try:
            self._setup_docker_container()
            self._run_kontrol_in_container()
            return True
        except Exception as e:
            click.echo(f"Critical Container Error: {e}")
            sys.exit(1)

    def _get_or_set_kontrol_version(self) -> KontrolVersion:
        if self.kontrol_version == "v0.0.0":
            click.echo("No Version Specified... Using LATEST Kontrol Version")
            return self._get_latest_kontrol_release()
        return self.kontrol_version

    def _setup_docker_container(self) -> None:
        try:
            docker_client = docker.from_env()
        except Exception as e:
            raise KaasCliException(f"Error talking to Docker client: {e}") from e

        if self.kontrol_docker_image:
            click.echo(f"Using Kontrol Image: {self.kontrol_docker_image}")
            click.echo("Pulling Kontrol Image...")
            try:
                [repo, tag] = self.kontrol_docker_image.split(':')
                docker_client.images.pull(repo, tag=tag)
            except Exception as e:
                raise KaasCliException(f"Error pulling Kontrol Image: {e}") from e
            image = self.kontrol_docker_image
        else:  # use self.kontrol_version
            kv = self.kontrol_version.lstrip('v')
            click.echo(f"Using Kontrol Image: runtimeverificationinc/kontrol:ubuntu-jammy-{kv}")
            click.echo("Pulling Kontrol Image...")
            image_tag = "ubuntu-jammy-" + kv
            try:
                docker_client.images.pull("runtimeverificationinc/kontrol", tag=image_tag)
            except Exception as e:
                raise KaasCliException(f"Error pulling Kontrol Image: {e}") from e
            image = f"runtimeverificationinc/kontrol:ubuntu-jammy-{kv}"
        kontrol_toml, foundry_toml = find_kontrol_configs()
        validate_config_location(self.test_root, kontrol_toml, foundry_toml)
        container_name = f"kaas-proof-container-{random.randint(1000, 2000)}"
        click.echo(f"Spawning Kontrol container with name: {container_name}")

        try:
            self.container = docker_client.containers.run(
                image,
                name=container_name,
                command="/bin/bash",
                # volumes={os.getcwd(): {'bind': '/opt/kaas', 'mode': 'rw'}},
                user="user",
                remove=True,
                detach=True,
                tty=True,
                working_dir="/opt/kaas",
                environment={"FOUNDRY_PROFILE": os.environ.get("FOUNDRY_PROFILE", "default")},
            )
        except Exception as e:
            raise KaasCliException(f"Error running Kontrol Container: {e}") from e
        click.echo("Setting Permissions on Container Files...")
        self.container.exec_run("chown -R user:user /opt/kaas", stream=True, user='root')
        self._copy_files_to_container(
            self.container.name,
            '/opt/kaas',
            (
                '.'
                if os.path.dirname(self.test_root or kontrol_toml or foundry_toml) == ''
                else os.path.dirname(self.test_root or kontrol_toml or foundry_toml)
            ),
        )

    def _copy_files_to_container(self, container_name: str | None, container_path: str | None, host_path: str) -> None:
        if container_name is None:
            click.echo("Lost Context to Container... Exiting...")
            raise KaasCliException("Lost context to container")
        mac_release, mac_version, mac_machine = platform.mac_ver()
        user_id = 'user'
        group_id = 'user'

        if not host_path:
            host_path = os.getcwd()

        click.echo(f"Copying files from {host_path} to {container_path}")

        # Construct the tar command to archive the current directory
        if mac_release:
            tar_command = "COPYFILE_DISABLE=1 tar -cf - ./"
        else:
            tar_command = "tar -cf - ./"

        # Construct the docker exec command to extract the archive inside the container
        docker_command = (
            f"docker exec -i {container_name} bash -cl "
            f"'tar -xf - -C {container_path} --owner={user_id} --group={group_id}'"
        )

        # Combine the commands with a pipe
        full_command = f"{tar_command} | {docker_command}"

        try:
            click.echo("Copying files to container")
            os.chdir(host_path)
            subprocess.run(full_command, shell=True, check=True)
        except Exception as e:
            raise KaasCliException(f"Error copying files to container: {e}") from e

    def _copy_files_from_container(self, container_name: str | None, container_path: str) -> None:
        if container_name is None:
            click.echo("Lost Context to Container... Exiting...")
            raise KaasCliException("Lost context to container")
        # Create a tarball inside the container and stream it to the host
        copy_out_folder_command = f"docker exec -i {container_name} bash -cl 'tar -cf - -C {container_path} {get_foundry_out_dir()}/' | tar -xf - --overwrite"
        try:
            click.echo("Copying files from container")
            subprocess.run(copy_out_folder_command, shell=True, check=True)
        except Exception as e:
            raise KaasCliException(f"Error copying files from container: {e}") from e

        # Find the .xml file and pull it from the container to the current folder
        find_command = (
            f"docker exec -i {container_name} bash -cl 'find {container_path} -name \"kontrol_prove_report.xml\"'"
        )
        try:
            result = subprocess.run(
                find_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            kontrol_prove_report = result.stdout.decode('utf-8').strip()
            if not kontrol_prove_report:
                raise KaasCliException("kontrol_prove_report.xml not found in the container")
            copy_command = f"docker cp {container_name}:{kontrol_prove_report} ."
            subprocess.run(copy_command, shell=True, check=True)
            click.echo(f"Copied {kontrol_prove_report} from container to current folder")
        except Exception as e:
            if not self.build_only:
                raise KaasCliException(f"Error finding or copying kontrol_prove_report.xml from container: {e}") from e

    def _parse_run_args(self, args: str) -> tuple[list[str], str]:
        # Split the args string while preserving quoted strings
        prove_args_list = []
        current_arg: list[str] = []
        in_quotes = False

        if not args:
            return [], ''

        for char in self.extra_prove_args:
            if char == '"' or char == "'":
                in_quotes = not in_quotes
            elif char.isspace() and not in_quotes:
                if current_arg:
                    prove_args_list.append(''.join(current_arg))
                    current_arg = []
            else:
                current_arg.append(char)

        if current_arg:
            prove_args_list.append(''.join(current_arg))

        # Separate config profiles from other options
        config_profiles = []
        other_options = []
        i = 0
        while i < len(prove_args_list):
            if prove_args_list[i] == '--config-profile' and i + 1 < len(prove_args_list):
                config_profiles.append(f'--config-profile {prove_args_list[i + 1]}')
                i += 2
            else:
                other_options.append(prove_args_list[i])
                i += 1

        # Join the other options with spaces
        options_str = ' '.join(other_options)

        return config_profiles, options_str

    def _exec_docker_command(self, command: str) -> tuple[int, list[bytes]]:
        exec_id_info = self.container.client.api.exec_create(  # type: ignore[union-attr]
            self.container.id,
            command,
            tty=True,
        )
        exec_id = exec_id_info['Id']
        output_stream = self.container.client.api.exec_start(exec_id, tty=True, stream=True)  # type: ignore[union-attr]

        for log in output_stream:
            click.echo(log.decode('utf-8'))

        exec_info = self.container.client.api.exec_inspect(exec_id)  # type: ignore[union-attr]
        return_code = exec_info['ExitCode']
        return return_code

    def _escape_shell_args(self, args: str) -> str:
        """
        Escape special characters in shell arguments to prevent syntax errors.
        """
        # Replace single quotes with double quotes
        escaped_args = args.replace("'", '"')
        return escaped_args

    def _run_kontrol_in_container(self) -> None:
        click.echo(f"Container Status: {self.container.status}")
        click.echo(f"Container Name: {self.container.name}")
        click.echo(f"Container ID: {self.container.id}")

        original_exception: Optional[BaseException] = None
        keyboard_interrupt_occurred = False

        try:
            # This inner try-except handles exceptions from build/prove operations
            try:
                if self.prove_only_profile:
                    click.echo(f"Running Kontrol Prove with profile: {self.prove_only_profile}")
                else:
                    click.echo("Starting Kontrol Build...")
                    escaped_build_args = self._escape_shell_args(self.extra_build_args) if self.extra_build_args else ""
                    kontrol_command = (
                        "/bin/bash --login -c 'kontrol build "
                        + (f" {escaped_build_args}" if self.extra_build_args else " ")
                        + "'"
                    )
                    click.echo(f"$ {kontrol_command}")
                    return_code = self._exec_docker_command(kontrol_command)

                    click.echo(f"Kontrol Build exited with code: {return_code}")
                    if return_code != 0:
                        raise KaasCliException(f"Error running Kontrol Build in container: {return_code}")

                if self.build_only:
                    click.echo("Build Only Mode. Kontrol operations complete.")
                else:
                    # Run "kontrol prove"
                    if self.prove_only_profile:
                        self._execute_kontrol_prove_container(
                            f"--config-profile {self.prove_only_profile}"
                            + (f" {self.extra_prove_args}" if self.extra_prove_args else "")
                        )
                    else:
                        config_profiles, options_list = self._parse_run_args(self.extra_prove_args)
                        if config_profiles:
                            for profile in config_profiles:
                                click.echo(f"Running kontrol prove with profile: {profile}")
                                self._execute_kontrol_prove_container(profile + " " + options_list)
                        else:
                            click.echo("Running kontrol prove with profile: default")
                            self._execute_kontrol_prove_container(self.extra_prove_args)

            except KeyboardInterrupt:
                click.echo("SIGINT or CTRL-C detected during Kontrol operations.")
                keyboard_interrupt_occurred = True
            except Exception as e:  # Catches KaasCliException from build or other unexpected errors
                click.echo(f"An error occurred during Kontrol operations: {e}")
                original_exception = e

        finally:
            # This block ALWAYS executes, regardless of what happened in the main try block.
            click.echo("Attempting to copy files from container (post-operations)...")
            try:
                self._copy_files_from_container(self.container.name, "/opt/kaas")
            except Exception as copy_e:
                click.echo(f"ERROR: Failed to copy files from container: {copy_e}")
                logging.error(f"Failed to copy files from container: {copy_e}")
                # If there wasn't an earlier critical error, this copy error becomes the main one.
                if not original_exception and not keyboard_interrupt_occurred:
                    # Explicitly setting cause for KaasCliException
                    err_msg = "Failed to copy files from container post-operations"
                    kaas_ex = KaasCliException(err_msg)
                    kaas_ex.__cause__ = copy_e
                    original_exception = kaas_ex

            click.echo("Cleaning up container...")
            self._cleanup_container()

            # After cleanup, handle any exceptions or interrupts that occurred.
            if keyboard_interrupt_occurred:
                click.echo("Exiting due to KeyboardInterrupt after cleanup.")
                sys.exit(0)  # Exit code 0 for SIGINT as per original behavior

            if original_exception:
                click.echo(f"Re-raising error after cleanup: {original_exception}")
                if isinstance(original_exception, KaasCliException):
                    raise original_exception
                else:  # Wrap other Python exceptions in KaasCliException for consistent error handling
                    raise KaasCliException(
                        f"Unhandled error during Kontrol execution in container: {original_exception}"
                    ) from original_exception

        # If we reach this point, it means the main operations in the try block completed successfully
        # (or prove had non-critical errors), and the finally block (copy & cleanup) also completed
        # without an unhandled exception being set to original_exception or a KeyboardInterrupt.
        click.echo("Kontrol in container finished successfully, files copied, container cleaned up.")

    def _execute_kontrol_prove_container(self, args: str) -> bool:
        escaped_args = self._escape_shell_args(args)
        kontrol_command = (
            "/bin/bash --login -c 'kontrol prove --xml-test-report" + (f" {escaped_args}" if args else " ") + "'"
        )
        click.echo(f"$ {kontrol_command}")
        return_code = self._exec_docker_command(kontrol_command)

        click.echo(f"Prove Return Code: {return_code}")
        return return_code == 0

    def _cleanup_container(self) -> None:
        try:
            click.echo("Stopping Container...")
            self.container.stop()
            self.container.remove(force=True)
            click.echo("Container cleaned up successfully")
        except Exception as e:
            logging.error(f"Error stopping or removing container: {e}")

    def handle_user_interrupt(self) -> None:
        click.echo("SIGINT or CTRL-C detected. Exiting gracefully..")
        self._cleanup_container()
        sys.exit(0)

    def _run_locally(self) -> bool:
        if not self._is_kontrol_installed():
            click.echo("Kontrol is not installed. Please install Kontrol to run locally. Using kup.")
            click.echo(
                "  For installation instructions, visit: https://github.com/runtimeverification/kontrol#fast-installation"
            )
            return False

        self._check_local_kontrol_version()
        kontrol_toml, foundry_toml = find_kontrol_configs()
        validate_config_location(self.test_root, kontrol_toml, foundry_toml)
        click.echo(f"Changing directory to: {os.path.dirname(self.test_root or kontrol_toml or foundry_toml)}")
        dirname = (
            '.'
            if os.path.dirname(self.test_root or kontrol_toml or foundry_toml) == ''
            else os.path.dirname(self.test_root or kontrol_toml or foundry_toml)
        )
        os.chdir(dirname)
        if self.build_only:  # Skip "kontrol prove"
            click.echo("Skipping Kontrol Prove...")
            if not self._run_kontrol_build():
                return False
            else:
                return True
        else:
            if not self.prove_only_profile:
                if not self._run_kontrol_build():
                    return False
                else:
                    return self._run_kontrol_prove()
            else:
                click.echo("Skipping Kontrol Build...")
                return self._run_kontrol_prove()

    def _check_local_kontrol_version(self) -> None:
        os.system("kontrol version")
        click.echo("  is installed. Checking Kontrol Version...")
        if self.kontrol_version == "v0.0.0":
            click.echo('No Version Specified... Using currently installed version')
        else:
            self._verify_specific_kontrol_version()

    def _verify_specific_kontrol_version(self) -> None:
        click.echo(f"Requested Kontrol Version: {self.kontrol_version}")
        try:
            result = subprocess.run(["kontrol", "version"], check=True, capture_output=True, text=True)
            version = self.kontrol_version.lstrip('v')
            version_pattern = re.compile(rf"Kontrol version: {re.escape(version)}\b")
            if version_pattern.search(result.stdout):
                click.echo("Exact Version Installed. Proceeding...")
            else:
                click.echo(f"Requested Version: {version}, NOT FOUND")
                click.echo(
                    "  Visit https://github.com/runtimeverification/kontrol#fast-installation for installation instructions"
                )
                raise KaasCliException(version)
        except Exception as e:
            raise KaasCliException(f"Error checking Kontrol Version: {e}") from e

    def _run_kontrol_build(self) -> bool:
        try:
            click.echo("Starting Kontrol Build...")
            escaped_build_args = self._escape_shell_args(self.extra_build_args) if self.extra_build_args else ""
            kontrol_command = (
                "/bin/bash --login -c 'kontrol build "
                + (f" {escaped_build_args}" if self.extra_build_args else " ")
                + "'"
            )
            click.echo(f"$ {kontrol_command}")
            process = subprocess.Popen(
                kontrol_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            if process.stdout is None:
                click.echo("Error running Kontrol Build...")
                return False
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    click.echo(output.strip())
            rc = process.poll()
            if rc != 0:
                click.echo("Error detected during Kontrol Build...")
                return False
            return True
        except Exception as e:
            click.echo(f"Error running Kontrol Build: {e}")
            return False

    def _run_kontrol_prove(self) -> bool:
        # Run "kontrol prove"
        if self.prove_only_profile:  # Run "kontrol prove" with profile
            return self._execute_kontrol_prove_local(
                f"--config-profile {self.prove_only_profile}"
                + (f" {self.extra_prove_args}" if self.extra_prove_args else "")
            )
        else:  # Run "kontrol prove" with default profile or profiles defined in extra_prove_args
            try:
                click.echo("Starting Kontrol Prove...")
                config_profiles, options_list = self._parse_run_args(self.extra_prove_args)
                if not config_profiles:
                    return self._execute_kontrol_prove_local(self.extra_prove_args)
                else:
                    click.echo(config_profiles)
                    click.echo(options_list)
                    for profile in config_profiles:
                        click.echo(f'Running kontrol prove with profile: {profile}')
                        click.echo(f'kontrol prove {profile} ' + " ".join({options_list}))
                        rc = self._execute_kontrol_prove_local(profile + " " + options_list)
                        if not rc:
                            return False
                    return True
            except Exception as e:
                raise KaasCliException(f"Error running Kontrol Prove: {e}") from e

    def _execute_kontrol_prove_local(self, args: str) -> bool:
        escaped_args = self._escape_shell_args(args)
        process = subprocess.Popen(
            "kontrol prove --xml-test-report " + (f" {escaped_args}" if args else " "),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if process.stdout is None:
            click.echo("Error running Kontrol Prove...")
            return False
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                click.echo(output.strip())
        rc = process.poll()
        if rc != 0:
            click.echo("Error detected during Kontrol Prove...")
            return False
        return True

    def _run_remotely(
        self,
    ) -> bool:
        if self.client is not None:
            click.echo(f"  Running on {self.client._url}")
            click.echo("Visit your Compute Dashboard to check the status of your jobs.")

        repo_name, commit_hash, branch_name = self._is_git_repository()
        click.echo(f"  Repository Name: {repo_name}")
        click.echo(f"  Commit Hash: {commit_hash}")
        click.echo(f"  Branch Name: {branch_name}")

        kontrol_toml, foundry_toml = find_kontrol_configs()
        validate_config_location(self.test_root, kontrol_toml, foundry_toml)
        click.echo(f"  Kontrol Config File: {kontrol_toml}")
        click.echo(f"  Foundry Config File: {foundry_toml}")

        click.echo("Sending Request on Remote Proof Runner...")
        self.kontrol_version = self._get_or_set_kontrol_version()
        if self.client is None:
            click.echo("Error: KaasClient Communication Failed.")
            return False
        try:
            data = self.client.run_kontrol(
                self.org_name,
                self.vault_name,
                self.branch,
                self.extra_build_args,
                self.extra_prove_args,
                self.kontrol_version,
            )
            click.echo(
                f"  Results of remote runs can be found at {self.client.url}/app/organization/{self.org_name}/vault/{self.vault_name}"
            )
            click.echo(f"  \nYour Compute Job ID is: {data.jobId}\n")
            if self.watch:
                self._watch_job(data.jobId)
        except Exception as e:
            click.echo(f"ERROR: Running Kontrol Remote Proof Runner: \n{e}")
            return False
        return True

    def _watch_job(self, job_id: str) -> None:
        click.echo(f"Watching Job: {job_id}")
        last_status = None

        if not self.client:
            click.echo("Error: KaasClient is not provided.")
            sys.exit(1)

        try:
            while True:
                response_data = self.client.get(url=f'{self.client.url}{KONTROL_JOB_DETAILS_URL.format(job_id)}')
                # Check job status
                status = response_data.get('status')

                if status != last_status:
                    last_status = status
                    click.echo(f"Job {job_id} Status: {status}")
                if status == 'success':
                    click.echo(f"Job {job_id} completed successfully.")
                    sys.exit(0)
                elif status in ['cancelled', 'failure']:
                    click.echo(f"Job failed with status: {status}")
                    sys.exit(1)

                # Sleep for 5 seconds before checking the status again
                time.sleep(5)
        except Exception as e:
            click.echo(f"Error watching job: {e}")
            sys.exit(1)

    def _is_git_repository(self) -> tuple[str, str, str]:
        try:
            repo_name = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
            commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
            branch_name = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
            return repo_name, commit_hash, branch_name
        except subprocess.CalledProcessError as e:
            if "not a git repository" in str(e).lower():
                click.echo("Error: Not a git repository")
                sys.exit(1)
            else:
                click.echo(f"Error: {e}")
                raise KaasCliException(f"Unexpected error: {e}") from e
        except Exception as e:
            raise KaasCliException(f"Unexpected error: {e}") from e

    def _get_latest_kontrol_release(self) -> KontrolVersion:
        url = "https://api.github.com/repos/runtimeverification/kontrol/releases/latest"
        try:
            reponse = requests.get(url)
            if reponse.status_code == 200:
                return reponse.json()['tag_name']
            else:
                raise KaasCliException("Fetching Latest Release Failed..")
        except Exception as e:
            click.echo(f"Error: {e}")
            click.echo("  Specify a version already locally installed or check your internet connection")
            sys.exit(1)

    def _is_docker_installed(self) -> bool:
        # Check User environment for 'docker' command
        try:
            shutil.which('docker')
        except Exception as e:
            logging.error(f"Error checking for docker installation: {e}")
            return False
        return True

    def _is_kontrol_installed(self) -> bool:
        # Check User environment for 'kontrol' command
        click.echo("Checking local Kontrol installation...")
        try:
            shutil.which('kontrol')
        except Exception as e:
            click.echo(f"Error checking for kontrol: {e}")
            return False
        return True
