from __future__ import annotations

import json
import logging
import os
import platform
import random
import shutil
import subprocess
from typing import Optional

import click
import docker
from docker.models.containers import Container

from .types import KaasCliException
from .utils import escape_shell_args, exec_docker_command, get_foundry_out_dir


class RunForge:
    """
    Run Forge (foundry) tests locally or in a container.
    """

    def __init__(
        self,
        foundry_version: str,
        mode: str,
        foundry_docker_image: str = "",
        extra_build_args: str = "",
        extra_test_args: str = "",
        watch: bool = False,
        test_root: str = "",
    ):
        self.foundry_version = foundry_version
        self.mode = mode
        self.foundry_docker_image = foundry_docker_image
        self.extra_build_args = extra_build_args or ""
        self.extra_test_args = extra_test_args or ""
        self.watch = watch
        self.test_root = test_root
        self.container: Optional[Container] = None

    def run(self) -> bool:
        """
        Dispatch to the appropriate runner based on mode.
        """
        if self.mode == 'local':
            return self._run_locally()
        elif self.mode == 'container':
            return self._run_in_container()
        else:
            click.echo(f"Invalid mode for Forge: {self.mode}")
            return False

    def _run_locally(self) -> bool:
        """
        Run `forge build` and `forge test` on the local host.
        """
        current_dir = os.getcwd()
        if self.test_root and self.test_root != ".":
            click.echo(f"Changing directory to: {self.test_root!r}")
            try:
                os.chdir(self.test_root)
            except FileNotFoundError:
                click.echo(f"Error: test_root directory {self.test_root!r} not found.")
                return False
        try:
            click.echo("Starting Forge build...")
            escaped_build_args = escape_shell_args(self.extra_build_args) if self.extra_build_args else ""
            forge_build_cmd = ["forge", "build"]
            if escaped_build_args:
                forge_build_cmd.extend(escaped_build_args.split())
            click.echo(f"$ {' '.join(forge_build_cmd)}")
            process = subprocess.Popen(
                forge_build_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
            if process.stdout:
                for line in iter(process.stdout.readline, ''):
                    click.echo(line.rstrip())
                process.stdout.close()
            rc = process.wait()
            if rc != 0:
                click.echo(f"Error detected during Forge build (exit code: {rc})...")
                return False

            click.echo("Starting Forge test...")
            escaped_test_args = escape_shell_args(self.extra_test_args) if self.extra_test_args else ""
            forge_test_cmd = ["forge", "test"]
            if escaped_test_args:
                forge_test_cmd.extend(escaped_test_args.split())
            click.echo(f"$ {' '.join(forge_test_cmd)}")
            process = subprocess.Popen(
                forge_test_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
            if process.stdout:
                for line in iter(process.stdout.readline, ''):
                    click.echo(line.rstrip())
                process.stdout.close()
            rc = process.wait()
            if rc != 0:
                click.echo(f"Error detected during Forge test (exit code: {rc})...")
                return False
            return True
        except Exception as e:
            click.echo(f"Error running Forge locally: {e}")
            return False
        finally:
            if self.test_root and self.test_root != ".":
                os.chdir(current_dir)

    def _setup_docker_container(self, client: docker.DockerClient) -> str:
        if self.foundry_docker_image:
            image = self.foundry_docker_image
        else:
            tag = self.foundry_version or 'stable'
            image = f"ghcr.io/foundry-rs/foundry:{tag}"

        click.echo(f"Pulling Forge image: {image!r}")
        try:
            docker_client = docker.from_env()
            docker_client.images.pull(image)
        except Exception as e:
            raise KaasCliException(f"Error pulling Forge image {image!r}: {e}") from e

        container_name = f"kaas-forge-container-{random.randint(1000, 9999)}"
        click.echo(f"Creating Forge container {container_name!r} with image {image!r}")
        try:
            self.container = docker_client.containers.run(
                image,
                name=container_name,
                command="/bin/bash",
                user="root",
                detach=True,
                tty=True,
                working_dir="/project",
                environment={"FOUNDRY_PROFILE": os.environ.get("FOUNDRY_PROFILE", "default")},
            )
            click.echo(f"Container {self.container.name!r} started.")
        except Exception as e:
            raise KaasCliException(f"Error creating or starting Forge container: {e}") from e
        return image

    def _copy_files_to_container(self, host_path: str = ".") -> None:
        if not self.container:
            raise KaasCliException("Container not initialized for copying files.")

        container_path = "/project"
        click.echo(
            f"Copying files from host path {os.path.abspath(host_path)!r} to container {self.container.name!r}:{container_path!r}"
        )

        original_cwd = os.getcwd()
        os.chdir(host_path)
        try:
            mac_release, _, _ = platform.mac_ver()
            tar_command = "COPYFILE_DISABLE=1 tar -cf - ." if mac_release else "tar -cf - ."

            docker_command = (
                f"docker exec -i {self.container.name} bash -c "
                f"'mkdir -p {container_path} && tar -xf - -C {container_path}'"
            )
            full_command = f"{tar_command} | {docker_command}"
            click.echo(f"Executing copy-to command: {full_command}")
            subprocess.run(full_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            click.echo("Files copied to container successfully.")
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode('utf-8', errors='ignore').strip()
            raise KaasCliException(f"Error copying files to container: {e}. Stderr: {stderr}") from e
        except Exception as e:
            raise KaasCliException(f"Error during file copy to container: {e}") from e
        finally:
            os.chdir(original_cwd)

    def _copy_files_from_container(self, image: str | None) -> None:
        if not self.container:
            click.echo("Container not initialized or already cleaned up. Skipping file copy from container.")
            return

        container_path = "/project"
        foundry_out_dirname = get_foundry_out_dir()
        container_out_path = os.path.join(container_path, foundry_out_dirname)
        host_target_dir = "."

        click.echo(
            f"Attempting to copy Foundry output {foundry_out_dirname!r} from {self.container.name!r}:{container_out_path!r} to host {os.path.abspath(host_target_dir)!r}"
        )

        # Helper function to find and copy a specific file using docker exec and docker cp
        def _find_and_copy_file_from_container(filename_to_copy: str) -> None:
            if not self.container:  # Should not happen if we are in this method
                return

            find_cmd_str = (
                f"docker exec -i {self.container.name} bash -cl 'find {container_path} -name {filename_to_copy!r}'"
            )
            click.echo(f"Attempting to find {filename_to_copy!r} in container path {container_path!r}...")
            try:
                find_result = subprocess.run(
                    find_cmd_str, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                path_in_container_str = find_result.stdout.decode('utf-8', errors='ignore').strip()

                if not path_in_container_str:
                    click.echo(
                        f"Warning: {filename_to_copy!r} not found by 'find' in {container_path!r}. Skipping copy."
                    )
                    logging.warning(f"{filename_to_copy!r} not found in {container_path!r} for copying.")
                    return

                # Ensure the found path is not empty and is a file (basic check)
                # `find` can return the path itself, which might be just /project if -name fails weirdly, though -maxdepth 1 helps.
                # A more robust check might involve `docker exec test -f {path_in_container_str}`
                if path_in_container_str == container_path or not os.path.basename(path_in_container_str):
                    click.echo(
                        f"Warning: 'find' command for {filename_to_copy!r} returned ambiguous path: {path_in_container_str!r}. Skipping copy."
                    )
                    logging.warning(
                        f"'find' command for {filename_to_copy!r} in {container_path!r} returned ambiguous path: {path_in_container_str!r}."
                    )
                    return

                click.echo(f"Found {filename_to_copy!r} at: {path_in_container_str!r}")

                # Construct destination path on host
                host_destination_path = os.path.join(host_target_dir, os.path.basename(path_in_container_str))

                copy_cmd_str = f"docker cp {self.container.name}:{path_in_container_str} {host_destination_path}"
                click.echo(
                    f"Attempting to copy {filename_to_copy!r} to host at {os.path.abspath(host_destination_path)!r}..."
                )

                subprocess.run(copy_cmd_str, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                click.echo(
                    f"Successfully copied {filename_to_copy!r} from container to {os.path.abspath(host_destination_path)!r}."
                )

            except subprocess.CalledProcessError as e_subproc:
                stderr_output = (
                    e_subproc.stderr.decode('utf-8', errors='ignore').strip()
                    if isinstance(e_subproc.stderr, bytes)
                    else str(e_subproc.stderr)
                )
                stdout_output = (
                    e_subproc.stdout.decode('utf-8', errors='ignore').strip()
                    if isinstance(e_subproc.stdout, bytes)
                    else str(e_subproc.stdout)
                )

                # Check if it was the find command or copy command that failed
                cmd_failed = "find" if "find" in e_subproc.cmd else "cp" if "cp" in e_subproc.cmd else "docker"

                click.echo(
                    f"Warning: Docker {cmd_failed} command for {filename_to_copy!r} failed. Exit code: {e_subproc.returncode}."
                )
                if stdout_output:
                    click.echo(f"  Stdout: {stdout_output}")
                if stderr_output:
                    click.echo(f"  Stderr: {stderr_output}")
                logging.warning(
                    f"Docker {cmd_failed} command for {filename_to_copy!r} failed. RC: {e_subproc.returncode}, STDOUT: {stdout_output}, STDERR: {stderr_output}"
                )
            except Exception as e_general:
                click.echo(
                    f"Warning: An unexpected error occurred when trying to copy {filename_to_copy!r}: {e_general!r}"
                )
                logging.warning(f"Unexpected error copying {filename_to_copy!r}: {e_general!r}")

        # Call the helper for each required JSON file
        _find_and_copy_file_from_container("foundry_test_report.json")
        _find_and_copy_file_from_container("forge_version.txt")

        # Merge two JSON files into one
        # Add a line to foundry_test_report.json with the forge_version.txt content w/ field "forge_version"
        try:
            with open("foundry_test_report.json", "r") as fr:
                report_data = json.load(fr)
            with open("forge_version.txt", "r") as fv:
                forge_version = {}
                for line in fv:
                    key_value = line.split(":")
                    forge_version[key_value[0]] = key_value[1].strip()
                report_data["forge_version"] = forge_version
            # Record the foundry docker image being used
            if image:
                report_data["foundry_docker_image"] = image
            with open("foundry_test_report.json", "w") as fr:
                json.dump(report_data, fr)
            click.echo(
                "Successfully merged forge_version.txt and foundry_test_report.json into foundry_test_report.json"
            )
        except Exception as e:
            click.echo(
                f"Warning: Failed to merge forge_version.txt and foundry_test_report.json into foundry_test_report.json: {e}"
            )
            logging.warning(
                f"Failed to merge forge_version.txt and foundry_test_report.json into foundry_test_report.json: {e}"
            )

    def _exec_forge_commands_in_container(self) -> bool:
        if not self.container:
            raise KaasCliException("Container not available to execute Forge commands.")

        # Forge Build
        escaped_build_args = escape_shell_args(self.extra_build_args) if self.extra_build_args else ""
        core_build_command = "forge build"
        if escaped_build_args:
            core_build_command += f" {escaped_build_args}"
        forge_build_cmd = f"/bin/bash -lc {core_build_command!r}"

        # Use list of args for exec_run to avoid complex shell quoting and B907 for this command
        # Forge commands typically don't need login shell (-l) from bash, but -xec for verbosity/exit on error is good.
        # However, container.exec_run with list doesn't use shell, so -x doesn't apply to bash itself.
        # We'll rely on forge's output and exit code.
        click.echo("Running Forge build in container.")
        click.echo(f"Command: {forge_build_cmd}")
        exit_code, log = exec_docker_command(self.container, forge_build_cmd)

        if exit_code != 0:
            click.echo(f"Forge build failed in container with exit code: {exit_code}")
            return False
        click.echo("Forge build completed successfully in container.")

        # Forge Test
        # This requires shell processing (the pipe | and tee)
        escaped_test_args = escape_shell_args(self.extra_test_args) if self.extra_test_args else ""
        core_test_command = "forge test --json"
        if escaped_test_args:
            core_test_command += f" {escaped_test_args}"
        core_test_command += " | tee foundry_test_report.json"
        forge_test_cmd = f"/bin/bash -lc {core_test_command!r}"

        forge_version_cmd = "/bin/bash -lc 'forge --version > forge_version.txt'"

        click.echo("Fetching Forge version")
        exit_code_version, log_version = exec_docker_command(self.container, forge_version_cmd)
        if exit_code_version != 0:
            click.echo(f"Warning: Forge version command failed with exit code: {exit_code_version}")

        click.echo("Running Forge test in container.")
        click.echo(f"Command: {forge_test_cmd}")
        exit_code_test, log_test = exec_docker_command(self.container, forge_test_cmd)
        click.echo(f"Exit Code: {exit_code_test}")

        if exit_code_test != 0:  # Use the specific exit code for the test command
            click.echo(f"Forge test failed in container with exit code: {exit_code_test}")
            return False

        click.echo("Forge test completed successfully in container.")
        return True

    def _cleanup_container(self) -> None:
        if self.container:
            click.echo(f"Cleaning up container {self.container.name!r}...")
            try:
                self.container.stop(timeout=5)
                click.echo("Container stopped.")
            except Exception as e:
                click.echo(f"Warning: Error stopping container {self.container.name!r}: {e}. Attempting to remove...")
                logging.warning(f"Error stopping container {self.container.name!r}: {e}")
            try:
                self.container.remove(force=True)
                click.echo("Container removed.")
            except Exception as e:
                click.echo(f"Warning: Error removing container {self.container.name!r}: {e}")
                logging.warning(f"Error removing container {self.container.name!r}: {e}")
            self.container = None
        else:
            click.echo("No active container found to clean up.")

    def _run_in_container(self) -> bool:
        if not shutil.which('docker'):
            click.echo("Docker is not installed. Please install Docker to run in a container.")
            return False

        docker_client: docker.DockerClient
        try:
            docker_client = docker.from_env()
        except Exception as e:
            click.echo(f"Error connecting to Docker: {e}")
            return False

        operation_succeeded = False
        image: str | None = None
        try:
            image = self._setup_docker_container(docker_client)
            host_source_path = self.test_root if self.test_root and self.test_root != "." else "."
            self._copy_files_to_container(host_path=host_source_path)

            operation_succeeded = self._exec_forge_commands_in_container()
            return operation_succeeded

        except KaasCliException as e:
            click.echo(f"A KaaS CLI error occurred: {e}")
            return False
        except Exception as e:
            click.echo(f"An unexpected error occurred: {e}")
            logging.exception("Unexpected error in _run_in_container")
            return False
        finally:
            if self.container:
                self._copy_files_from_container(image)
            self._cleanup_container()
