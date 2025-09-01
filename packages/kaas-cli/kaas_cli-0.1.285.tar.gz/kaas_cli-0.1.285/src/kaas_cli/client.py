from __future__ import annotations

import hashlib
import json
import logging
import os
import pickle
import shutil
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import TYPE_CHECKING, Any, BinaryIO, Callable, Final, List, Optional, Protocol, runtime_checkable
from zipfile import ZipFile

import click
import jmespath
import requests
from dacite import from_dict
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from hurry.filesize import size
from requests import JSONDecodeError, Session

from kaas_cli.config import DEFAULT_PROJECT_ID, DEFAULT_TOKEN, SERVER_URL
from kaas_cli.types import Cache, KaasCliException

from .constants import (
    CONFIG_LOG_PATH,
    CONFIG_SESSION_PATH,
    DEVICE_LOGIN_URL,
    GRAPHQL_URL,
    KONTROL_JOB_URL,
    ORG_VAULT_CACHE_URLS,
    ORG_VAULT_CACHES_URL,
    ORGANIZATIONS_URL,
    UPLOAD_SUCCESS_MESSAGE,
    USER_URL,
    VAULTS_ROOT_URL,
)
from .types import Job, NoFileFoundError, Test, UploadFileMetadata

if TYPE_CHECKING:
    from .types import KontrolVersion


def md5(filepath: Path) -> str:
    h = hashlib.md5()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filepath, 'rb', buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()


@dataclass(frozen=True)
class DeviceAuth:
    device_code: str
    expires_in: int
    interval: int
    user_code: str
    verification_uri: str


@dataclass(frozen=True)
class Confirmation:
    success: bool


@runtime_checkable
class ProgressBar(Protocol):
    def update(self, n: int) -> None: ...


class ProgressFileWrapper:
    def __init__(self, fileobj: BinaryIO, progress_bar: ProgressBar, progress_bar_lock: Lock) -> None:
        self._fileobj = fileobj
        self._progress_bar = progress_bar
        self._progress_bar_lock = progress_bar_lock
        self._total_read = 0
        self._file_size = os.fstat(self._fileobj.fileno()).st_size

    def __len__(self) -> int:
        # Required for setting Content-Length
        return self._file_size

    def read(self, amt: Optional[int] = None) -> bytes:
        amt_to_use = -1 if amt is None else amt
        data = self._fileobj.read(amt_to_use)
        read_bytes = len(data)
        with self._progress_bar_lock:
            self._progress_bar.update(read_bytes)
        return data

    def __getattr__(self, attr):  # type: ignore
        return getattr(self._fileobj, attr)


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):  # type: ignore
        if is_dataclass(o):
            return asdict(o)  # type: ignore
        return super().default(o)


class CustomSession(Session):
    def get(self, *args: Any, **kwargs: Any) -> Any:
        response = super().get(*args, **kwargs)
        try:
            json_response = response.json()
            if 'error' in json_response:
                raise ValueError(json_response['error'], json_response.get('message', 'No message provided'))
            return json_response
        except JSONDecodeError as e:
            logging.error(f"GET request JSON decode failed: {e}")
            raise e
        except ValueError as e:
            logging.error(f"GET request failed: {e}")
            raise e

    def post(self, *args: Any, **kwargs: Any) -> Any:
        response = super().post(*args, **kwargs)
        try:
            json_response = response.json()
            if 'error' in json_response:
                raise ValueError(json_response['error'], json_response.get('message', 'No message provided'))
            return json_response
        except JSONDecodeError as e:
            logging.error(f"POST request JSON decode failed: {e}")
            raise e
        except ValueError as e:
            logging.error(f"POST request failed: {e}")
            click.echo(f"POST request failed: {e}")
            raise e

    def post_return_no_content(self, *args: Any, **kwargs: Any) -> None:
        response = super().post(*args, **kwargs)
        try:
            if not response.ok:
                raise ValueError(response.text)
        except ValueError as e:
            logging.error(f"POST request failed: {e}")
            raise e

    def get_text(self, *args: Any, **kwargs: Any) -> Any:
        response = super().get(*args, **kwargs)
        return response.text


class AuthenticatedSession(CustomSession):
    def __init__(self, access_token: str) -> None:
        super().__init__()
        self.access_token = access_token
        self.headers.update({'Authorization': f'Bearer {self.access_token}'})


class KaasClient:
    _client: Client
    _session: CustomSession
    _url: str
    _token: str | None
    _vault: str | None
    _org: str | None

    def __init__(
        self,
        url: str,
        *,
        token: str | None = None,
        vault: str | None = None,
        org: str | None = None,
    ) -> None:
        self._url = url or SERVER_URL
        self._token = token or DEFAULT_TOKEN
        self._vault = vault
        self._org = org

        if not self._vault and DEFAULT_PROJECT_ID:
            self._vault = DEFAULT_PROJECT_ID.split('/')[1]
        if not self._org and DEFAULT_PROJECT_ID:
            self._org = DEFAULT_PROJECT_ID.split('/')[0]

        self._configure_logging()
        self._setup_client()
        self._session = CustomSession()
        if token:
            self._session = AuthenticatedSession(token)
        else:
            self._load_session_if_exists()

    def _setup_client(self) -> None:
        """Setup the GraphQL client."""
        transport = RequestsHTTPTransport(
            url=f'{self._url}{GRAPHQL_URL}',
            verify=True,
        )
        self._client = Client(transport=transport, fetch_schema_from_transport=True)

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

    def _load_session_if_exists(self) -> None:
        """Load session if the session file exists."""
        if CONFIG_SESSION_PATH.exists():
            self._load_session()

    def hello(self, name: str | None = None) -> None:
        click.echo(f"Hello, {name}!")

    def _save_session(self, file_path: Path = CONFIG_SESSION_PATH) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open('wb') as file:
            pickle.dump(self._session, file)

    def _load_session(self, file_path: Path = CONFIG_SESSION_PATH) -> None:
        with file_path.open('rb') as file:
            self._session = pickle.load(file)

    def _remove_session(self, file_path: Path = CONFIG_SESSION_PATH) -> bool:
        file_path.unlink()
        return True

    def _list_local_files(self, directory: str) -> list[Path]:
        return [path for path in Path(directory).glob('**/*') if path.is_file()]

    def list_local_proofs(self, directory: str) -> list[dict[str, Any]]:
        list_local_files = [
            {
                'name': self._read_proof(path / 'proof.json').get('id'),
                'size': size(sum(f.stat().st_size for f in path.glob('**/*') if f.is_file())),
                'last_update_date': self._read_proof(path / 'proof.json').get('last_update_date'),
            }
            for path in Path(directory).glob('**/*')
            if path.is_dir() and len(path.name.split(':')) == 2
        ]
        return list_local_files

    def _read_proof(self, proof_path: Path) -> dict[str, Any]:
        if not proof_path.exists():
            return {'id': None, 'last_update_date': None}

        with proof_path.open() as file:
            data = json.load(file)
            return {
                'id': data.get('id'),
                'last_update_date': datetime.fromtimestamp(os.path.getmtime(proof_path)).isoformat(),
            }

    def list_remote(self) -> Any:
        try:
            json_data = self._session.get(url=f'{self._url}{USER_URL}')
        except Exception:
            raise KaasCliException("List remote proofs failed") from None
        return json_data

    def _get_default_vault(self) -> str | None:
        try:
            json_data = self._session.get(url=f'{self._url}{USER_URL}')
        except Exception:
            raise KaasCliException("Get default vault failed") from None
        vault_hash = jmespath.search('vaults[0].hash', json_data)
        return vault_hash

    def _get_upload_urls(
        self, metadata: dict[str, UploadFileMetadata], vault: str, org: str, tag: str | None
    ) -> dict[str, str]:
        data = self._session.post(
            url=f'{self._url}{ORG_VAULT_CACHE_URLS.format(org, vault)}',
            data=json.dumps(
                {
                    'files': metadata,
                    'tag': tag,
                },
                cls=EnhancedJSONEncoder,
            ),
            headers={
                'Content-Type': 'application/json',
            },
        )
        return data

    def _upload_file(
        self,
        file_path: Path,
        url: str,
        metadata: dict[str, UploadFileMetadata],
        uploaded_files: list[UploadFileMetadata],
        upload_results: dict[str, Any],
        verbose: bool,
        progress_bar: ProgressBar,
        progress_bar_lock: Lock,
    ) -> None:
        file_size = file_path.stat().st_size
        file_path_str = str(file_path)
        with file_path.open('rb') as file:
            if verbose:
                click.echo(f"Uploading {file_path}")

            wrapped_file = ProgressFileWrapper(file, progress_bar, progress_bar_lock)

            headers = {'Content-Length': str(file_size)}
            response = requests.put(url, data=wrapped_file, headers=headers)
            # Check if the upload was successful
            if response.status_code in [200, 201]:  # Success status codes can vary, e.g., 200 OK or 201 Created
                if verbose:
                    click.echo(f"Successfully uploaded: {file_path}")
                upload_results[str(file_path)] = {'success': True, 'status_code': response.status_code}
                uploaded_files.append(metadata[file_path_str])
            else:
                click.echo(f"Failed to upload {file_path} to {url}. Status code: {response.status_code}")
                click.echo(response.text)
                click.echo(response.reason)
                upload_results[str(file_path)] = {
                    'success': False,
                    'status_code': response.status_code,
                    'error_message': response.text,
                }

    def _upload_files(
        self,
        urls: dict[str, str],
        metadata: dict[str, UploadFileMetadata],
        cache_hash: str,
        tests: list[Test],
        tag: str | None,
        verbose: bool,
        job_id: str | None = None,
    ) -> dict[str, Any]:
        upload_results: dict[str, Any] = {}
        uploaded_files: list[UploadFileMetadata] = []

        file_paths = list(urls.keys())
        total_size = sum(Path(file_path).stat().st_size for file_path in file_paths)

        if verbose:
            click.echo(f"Uploading {len(file_paths)} new file(s)...")

        progress_bar_lock = Lock()
        progress_bar: ProgressBar
        with click.progressbar(
            length=total_size, label='Uploading files', show_percent=True, show_eta=True
        ) as progress_bar:
            # Upload files in parallel
            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(
                        self._upload_file,
                        Path(file_path_str),
                        url,
                        metadata,
                        uploaded_files,
                        upload_results,
                        verbose,
                        progress_bar,
                        progress_bar_lock,
                    )
                    for file_path_str, url in urls.items()
                ]
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"An error occurred: {e}")

        # Create the cache record in database after all files are uploaded
        self._session.post_return_no_content(
            url=f'{self._url}{ORG_VAULT_CACHES_URL.format(self._org, self._vault)}',
            data=json.dumps(
                {'cacheHash': cache_hash, 'tag': tag, 'tests': tests, 'uploadedFiles': uploaded_files, 'jobId': job_id},
                cls=EnhancedJSONEncoder,
            ),
            headers={
                'Content-Type': 'application/json',
            },
        )

        return upload_results

    def archive_files(
        self,
        file_list: List[Path],
        archive_name: str,
        archive_format: str = 'zip',
        root_dir: Path | None = None,
        target_dir: Path | None = None,
    ) -> str:
        """
        Archives a list of files into a single archive file while preserving the directory structure.

        Args: file_list (List[Path]): List of file paths to include in the archive. archive_name (str): The name of
        the output archive file without extension. archive_format (str): Format of the archive ('zip', 'tar',
        etc.). Default is 'zip'. root_dir (Path): The root directory to use for preserving the relative paths. If
        None, the common parent of all files will be used.

        Returns:
        str: The path to the created archive file.
        """
        if root_dir is None:
            # Find the common parent directory of all files
            common_paths: set[Path] = set(Path(file_list[0]).parents)
            for file_path in file_list[1:]:
                common_paths = set(common_paths) & set(Path(file_path).parents)
            root_dir = min(common_paths, key=lambda p: len(p.parts))

        # Ensure the archive name does not include an extension
        archive_path = Path(archive_name).with_suffix('')

        # Create a temporary directory to hold the files to be archived
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            for file_path in file_list:
                if file_path.is_file():
                    # Calculate relative path to the root_dir
                    relative_path = file_path.relative_to(root_dir)
                    # Create any necessary directories
                    (temp_dir_path / relative_path).parent.mkdir(parents=True, exist_ok=True)
                    # Copy file to the new location preserving the folder structure
                    shutil.copy(file_path, temp_dir_path / relative_path)

            # Create the archive from the temporary directory
            archive_path = Path(shutil.make_archive(str(archive_path), archive_format, root_dir=temp_dir_path))

        # Move the archive to the desired directory and return the new path
        final_archive_path = archive_path.with_suffix(f'.{archive_format}')
        shutil.move(archive_path, final_archive_path)

        if target_dir is not None:
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(final_archive_path, target_dir / final_archive_path.name)
            final_archive_path = target_dir / final_archive_path.name

        return str(Path(final_archive_path))

    def get_tests(self, root_dir: Path) -> list[Test]:
        # Find tests that are the directories of proofs/[test_name:version]
        tests: list[Test] = []
        dirs_under_proofs = os.listdir(root_dir / 'proofs')
        for dir_name in dirs_under_proofs:
            if len(dir_name.split(':')) == 2:
                test_name, version = dir_name.split(':')
                tests.append(Test(name=test_name, version=version))
        return tests

    def get_artifact_metadata(self, archive_path: str, digest_file_path: Path) -> dict[str, UploadFileMetadata]:
        """
        Extracts metadata from an archive file.

        Args:
        archive_path (str): Path to the archive file.

        root_dir (Path): The root directory to use for preserving the relative paths.

        Returns:
        dict[str, UploadFileMetadata]: Metadata extracted from the archive file.
        """
        if not digest_file_path.exists():
            raise FileNotFoundError(f"The digest file {digest_file_path} does not exist.")

        # Initialize an empty dictionary for metadata
        # NOTE: The key of the metadata dictionary is the local file path where the file is stored.
        metadata: dict[str, UploadFileMetadata] = {}

        # Create a Path object from the archive_path
        archive_file = Path(archive_path)

        # Check if the archive file exists
        if not archive_file.exists():
            raise FileNotFoundError(f"The archive file {archive_path} does not exist.")

        try:
            metadata[archive_path] = UploadFileMetadata(
                filename=archive_file.name,
                updated_at=datetime.fromtimestamp(archive_file.stat().st_mtime).isoformat(),
                checksum=md5(digest_file_path),
                size=archive_file.stat().st_size,
                is_cache_zip=True,  # This is the [cacheHash].zip file
            )
        except Exception as e:
            # Handle any exception that might occur during metadata extraction
            raise e

        return metadata

    def get_version_from_digest(self, file_list: Any, tag: str | None) -> str:
        """
        Reads a JSON file named 'digest' from the provided file list, extracts hash values from specified fields,
        and returns a short unique hash string.

        Args:
        file_list (list[Path]): List of file paths.

        Returns:
        str: A short unique hash string (40 characters) derived from the digest file contents.
        """
        # Find the 'digest' file in the file list
        digest_file = next((file for file in file_list if file.name == 'digest'), None)
        if digest_file is None:
            raise FileNotFoundError("No 'digest' file found in the provided file list.")

        # Read the 'digest' JSON file
        with open(digest_file, 'r') as file:
            data = json.load(file)

        # Extract the hash values from specified fields
        kompilation_hash = data.get('kompilation', 'Not found')
        foundry_hash = data.get('foundry', 'Not found')
        kontrol_version = data.get('kontrol', 'Not found')

        # Create a shorter unique hash by combining the three values and hashing them
        combined_string = f"{kompilation_hash}{foundry_hash}${kontrol_version}${tag or ''}"
        hash_object = hashlib.sha256(combined_string.encode())
        # Return first 40 characters of the hex digest for a shorter but still unique hash
        return hash_object.hexdigest()[:40]

    def archive_files_and_add_to_metadata(
        self, glob: str, root_dir: Path, target_dir: Path, cache_hash: str, metadata: dict[str, UploadFileMetadata]
    ) -> None:
        """
        Archives files matching the specified glob pattern and adds them to the provided metadata dictionary.

        Args:
        glob (str): The glob pattern to match files to archive.
        root_dir (str): The root directory to search for files.
        metadata (dict[str, UploadFileMetadata]): The metadata dictionary to add the archived files to.
        """
        # Find all files matching the glob pattern
        files = list(Path(root_dir).glob(glob))
        if not files:
            raise FileNotFoundError(f"No files found matching the glob pattern: {glob}")

        # TODO: Archive files in parallel
        with click.progressbar(files, label='Archiving files', show_eta=True) as progress_files:
            # Archive the files and add them to the metadata dictionary
            for file_path in progress_files:
                # Calculate the relative path to the root directory
                relative_path = file_path.relative_to(root_dir)
                # Create the archive name from the relative path
                archive_name = f"{relative_path.name}.zip"
                # Archive the single file
                archive_path = self.archive_files(
                    [file_path],
                    archive_name,
                    archive_format='zip',
                    root_dir=root_dir,
                    target_dir=target_dir / relative_path.parent,
                )
                # Add the archived file to the metadata dictionary
                metadata[archive_path] = UploadFileMetadata(
                    filename=archive_name,
                    folder=cache_hash + "/" + str(relative_path.parent),
                    updated_at=datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    checksum=md5(Path(file_path)),
                    size=file_path.stat().st_size,
                    # NOTE: We can't use the checksum of the archive file here as it will be different each time we archive the file
                )

    def upload_files_s3(
        self, directory: str, verbose: bool, tag: str | None = None, job_id: str | None = None
    ) -> str | None:
        click.echo(f"Uploading files from directory: {directory}")
        file_list = self._list_local_files(directory)
        if not file_list or len(file_list) == 0:
            raise KaasCliException(f'No files to upload in dir: {directory}')

        # Check if there is `digest` file
        digest_file = next((file for file in file_list if file.name == 'digest'), None)
        if digest_file is None:
            raise KaasCliException(f"No 'digest' file found in dir: {directory}")

        # Check if there is proof
        proofs = self.list_local_proofs(directory)
        if not proofs:
            raise KaasCliException(f'No proofs to upload in dir: {directory}')

        # Create temp directory
        temp_dir = Path(tempfile.mkdtemp())
        if verbose:
            click.echo(f"Temp directory created at {temp_dir}")

        cache_hash = self.get_version_from_digest(file_list, tag)
        artifact_archive_path = self.archive_files(
            file_list, cache_hash, archive_format='zip', root_dir=Path(directory), target_dir=temp_dir
        )

        # NOTE: The key of the metadata dictionary is the local file path where the file is stored.
        metadata = self.get_artifact_metadata(artifact_archive_path, Path(directory) / 'digest')

        # Archive each proofs/[test_name:version]/kcfg/kcfg.json
        self.archive_files_and_add_to_metadata(
            glob='**/proofs/**/kcfg/kcfg.json',
            root_dir=Path(directory),
            target_dir=temp_dir,
            cache_hash=cache_hash,
            metadata=metadata,
        )

        # Archive each proofs/[test_name:version]/kcfg/nodes/[node_id].json
        self.archive_files_and_add_to_metadata(
            glob='**/proofs/**/kcfg/nodes/*.json',
            root_dir=Path(directory),
            target_dir=temp_dir,
            cache_hash=cache_hash,
            metadata=metadata,
        )

        # Add kontrol_prove_report.xml if it exists
        report_file = Path(directory) / '..' / 'kontrol_prove_report.xml'
        if report_file.exists():
            # copy the kontrol_prove_report.xml to temp_dir
            report_path = temp_dir / report_file.name
            shutil.copy(report_file, report_path)

            # show full path to the report file
            if verbose:
                click.echo(f"Report file {report_file.resolve()} found")
            metadata[str(report_path)] = UploadFileMetadata(
                filename=report_file.name,
                folder=cache_hash,
                updated_at=datetime.fromtimestamp(report_file.stat().st_mtime).isoformat(),
                checksum=md5(report_path),
                size=report_path.stat().st_size,
            )
        else:
            if verbose:
                click.echo(f"Report file {report_file.resolve()} not found")

        # Archive the kompiled/compiled.json file if it exists
        # , then add it to the metadata
        compiled_file = Path(directory) / 'kompiled' / 'compiled.json'
        if compiled_file.exists():
            kompiled_archive_path = self.archive_files(
                [compiled_file],
                "compiled.json.zip",
                archive_format='zip',
                root_dir=Path(directory),
                target_dir=temp_dir / 'kompiled',
            )
            metadata[kompiled_archive_path] = UploadFileMetadata(
                filename=compiled_file.name + ".zip",
                folder=cache_hash + "/kompiled",
                updated_at=datetime.fromtimestamp(compiled_file.stat().st_mtime).isoformat(),
                checksum=md5(compiled_file),
                size=compiled_file.stat().st_size,
            )
            if verbose:
                click.echo(f"Archived kompiled/compiled.json file: {kompiled_archive_path}")
        else:
            if verbose:
                click.echo(
                    f"kompiled/compiled.json file {compiled_file.resolve()} not found, skipping archiving kompiled/compiled.json file."
                )

        if self._vault is None or self._org is None:
            raise KaasCliException("vault and org must be provided")

        tests = self.get_tests(Path(directory))
        if len(tests) == 0:
            raise KaasCliException(f"No tests found in dir: {directory}")

        if verbose:
            click.echo(f"Generating presigned URLs for {len(metadata)} files to upload.")
        urls = self._get_upload_urls(metadata=metadata, vault=self._vault, tag=tag, org=self._org)
        try:
            if verbose:
                click.echo(f"Uploading cache to {self._org}/{self._vault} with tag {tag}...")
            self._upload_files(urls, metadata, cache_hash, tests, tag=tag, verbose=verbose, job_id=job_id)
            if verbose:
                click.echo(UPLOAD_SUCCESS_MESSAGE)
        except NoFileFoundError as e:
            click.echo(e)
        except Exception as e:
            raise KaasCliException(f"Failed to upload cache to S3: {e}") from None

        # remove the temp_dir that stores the files to upload
        shutil.rmtree(temp_dir)
        if verbose:
            click.echo(f"Temp directory {temp_dir} removed")

        return None

    def download_version_or_tag(
        self, org_name: str, vault_name: str, version_or_tag: str, target_directory: str, verbose: bool
    ) -> Any:
        caches = self.list_caches(org_name, vault_name, version_or_tag)
        if not caches or len(caches) == 0:
            raise KaasCliException(f"No cache found for {org_name}/{vault_name}:{version_or_tag}")
        try:
            latest_cache = caches[0]
            url_to_download = latest_cache.url
            downloaded_file_path = self.replace_path(
                f"{org_name}/{vault_name}/{latest_cache.fileName}", target_directory
            )
            self.download_file(url_to_download, downloaded_file_path, verbose)
            self.process_archive(downloaded_file_path, target_directory, verbose)
        except Exception as e:
            raise KaasCliException(f"Download {org_name}/{vault_name}:{version_or_tag} failed: {str(e)}") from e

        return f'Version {version_or_tag} downloaded to {target_directory}'

    def download_latest_version(self, org_name: str, vault_name: str, target_directory: str, verbose: bool) -> Any:
        caches = self.list_caches(org_name, vault_name)
        if not caches or len(caches) == 0:
            raise KaasCliException(f"No cache found for {org_name}/{vault_name}")
        try:
            latest_cache = caches[0]
            url_to_download = latest_cache.url
            downloaded_file_path = self.replace_path(
                f"{org_name}/{vault_name}/{latest_cache.fileName}", target_directory
            )
            self.download_file(url_to_download, downloaded_file_path, verbose)
            self.process_archive(downloaded_file_path, target_directory, verbose)
        except Exception as e:
            raise KaasCliException(f"Download failed: {e}") from None

        return f'Latest version of {latest_cache.lastModified} downloaded to {target_directory}'

    def process_archive(self, archive_path: str, extract_to: str, verbose: bool) -> None:
        """
        Extracts files from an archive to a specified directory and then removes the archive.

        Args:
        archive_path (str): The path to the archive file.
        extract_to (str): The directory to extract the files to.
        """
        # Ensure the target directory exists
        os.makedirs(extract_to, exist_ok=True)

        # Extract the archive
        with ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)

        # Remove the archive file after extraction
        os.remove(archive_path)
        # Delete the folder that contains archive file if it is empty
        if not os.listdir(os.path.dirname(archive_path)):
            os.rmdir(os.path.dirname(archive_path))
        if verbose:
            click.echo(f"Extracted archive to {extract_to}")

    def login(self) -> DeviceAuth:
        try:
            data = self._session.post(url=f'{self._url}{DEVICE_LOGIN_URL}')
        except Exception:
            raise KaasCliException("Login failed") from None
        return DeviceAuth(**data)

    def confirm_login(self, device_code: str) -> Confirmation:
        try:
            data = self._session.get(url=f'{self._url}{DEVICE_LOGIN_URL}', params={'device_code': device_code})
        except Exception:
            raise KaasCliException("Login failed") from None
        self._session = AuthenticatedSession(data['token'])
        self._save_session()
        return Confirmation(True)

    def check(self) -> Confirmation:
        data = self._session.get(url=f'{self._url}{USER_URL}')
        if data:
            return Confirmation(True)
        else:
            return Confirmation(False)

    def _get_download_url(self, vault_hash: str, tag: str | None = None) -> dict:
        query = f"?tag={tag}" if tag else ""
        org_name, vault_name = vault_hash.split('/')
        data = self._session.get(url=f'{self._url}{ORG_VAULT_CACHE_URLS.format(org_name, vault_name)}{query}')
        return data

    def download_file(self, url: str, folder_path: str, verbose: bool) -> None:
        file_path = Path(folder_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        is_run_by_ci = (
            os.getenv('CI', False)
            or os.getenv('GITHUB_ACTIONS', False)
            or os.getenv('GITLAB_CI', False)
            or os.getenv('CIRCLECI', False)
            or os.getenv('JENKINS_URL', False)
        )
        with open(file_path, 'wb') as file:
            if verbose:
                click.echo(f"Downloading {file_path}")
            with requests.get(url, stream=True) as response:
                # Check if the request was successful
                response.raise_for_status()

                total_length_str = response.headers.get('content-length')
                if total_length_str is None:
                    # Write the content of the response to the file in chunks
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                else:
                    dl = 0
                    total_length = int(total_length_str)
                    for data in response.iter_content(chunk_size=8192):
                        dl += len(data)
                        file.write(data)
                        done = int(50 * dl / total_length)
                        if not is_run_by_ci:
                            sys.stdout.write("\r[%s%s] %s%%" % ('=' * done, ' ' * (50 - done), done * 2))
                            sys.stdout.flush()
                    print("\n")

    def replace_path(self, input_string: str, target_directory: str) -> str:

        # Find the index of the first dash '/'
        dash_index = input_string.find('/')

        # Replace everything up to the first dash with 'test'
        result = target_directory + input_string[dash_index:]

        return result

    def read_new_files(self, files: list[str], target_directory: str) -> list[str]:
        new_files = []
        for file_name in files:
            file_path = Path(target_directory, file_name)
            if not file_path.exists():
                new_files.append(file_name)
        return new_files

    def list_orgs(self) -> list[str]:
        try:
            data = self._session.get(url=f'{self._url}{ORGANIZATIONS_URL}')
        except Exception as e:
            sys.exit(f"List orgs failed: {e}")
            raise KaasCliException("List orgs failed") from None
        return data

    def list_vaults(self) -> list[str]:
        try:
            data = self._session.get(url=f'{self._url}{VAULTS_ROOT_URL}')
        except Exception as e:
            sys.exit(f"List vaults failed: {e}")
            raise KaasCliException("List vaults failed") from None
        return data

    def list_caches(self, org_name: str, vault_name: str, search: str | None = None) -> list[Cache]:
        query = f"?search={search}" if search else ""
        try:
            data = self._session.get(url=f'{self._url}{ORG_VAULT_CACHES_URL.format(org_name, vault_name)}{query}')
            caches = [from_dict(Cache, cache) for cache in data]
            return caches
        except Exception as e:
            raise KaasCliException(f"List caches failed: {e}") from None

    def logout(self) -> bool:
        """
        Log out the user by clearing the session and authentication token.
        Returns True if the logout was successful, False otherwise.
        """
        try:
            return self._remove_session()
        except Exception as e:
            logging.error(f"Logout failed: {e}")
            return False

    def run_kontrol(
        self,
        org_name: str,
        vault_name: str,
        branch: str,
        extra_build_args: str,
        extra_prove_args: str,
        kontrol_version: KontrolVersion,
    ) -> Job:
        try:
            data = self._session.post(
                url=f'{self._url}{KONTROL_JOB_URL.format(org_name, vault_name)}',
                json={
                    "branch": branch,
                    "kontrolVersion": kontrol_version,
                    "kontrolDockerImage": "runtimeverification/kontrol:ubuntu-jammy-" + kontrol_version.lstrip('v'),
                    "kaasCliBranch": "master",
                    "extraBuildArgs": f"{extra_build_args}" if extra_build_args else " ",
                    "foundryProfile": os.environ.get("FOUNDRY_PROFILE", "default"),
                    "profiles": [
                        {
                            "profileName": "default",
                            "extraProveArgs": f"{extra_prove_args}" if extra_prove_args else " ",
                            "tag": "latest",
                        }
                    ],
                    "workflowBranch": "main",
                    "kaasServerUrl": self._url,
                },
            )
            job = from_dict(Job, data)
            return job
        except Exception as e:
            raise KaasCliException(f"Run kontrol failed: {e}") from None

    @property
    def url(self) -> str:
        return self._url

    @property
    def get(self) -> Callable:
        return self._session.get


QUERY_HELLO: Final = gql(
    """
    query Hello($name: String!) {
        hello(name: $name)
    }
    """
)
