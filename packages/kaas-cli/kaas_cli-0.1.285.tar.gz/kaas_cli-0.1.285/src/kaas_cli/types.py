from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import IO, Any, Optional

from click import ClickException, ParamType, echo

File_Data = dict[str, tuple[Optional[str], Any, Optional[str]]]
Metadata = dict[str, Any]


class KaasCliException(ClickException):
    def show(self, file: IO[Any] | None = None) -> None:
        echo(f'{self.message}', file=file)


class NoFileFoundError(ClickException):
    """Custom exception indicating that no files were found for upload."""


def github_url_repr(username: str) -> str:
    return f"https://github.com/{username}"


@dataclass
class User:
    url: str = field(init=False)
    email: str | None
    createdAt: str  # noqa: N815
    username: str

    def __post_init__(self) -> None:
        self.url = github_url_repr(self.username)


@dataclass
class Vault:
    id: str
    name: str
    createdAt: str  # noqa: N815
    user: User


@dataclass
class Key:
    key: str
    name: str
    createdAt: str  # noqa: N815
    expiresAt: Optional[str] = None  # noqa: N815


@dataclass
class KontrolVersion(str, ParamType):
    name: str = "version"

    def convert(self, value: str, param: Any, _ctx: Any) -> Any:
        pattern = r"^v\d+\.\d+\.\d+$"
        if not re.match(pattern, value):
            self.fail(
                f"{value} is not a valid version. Use the format v<int MAJOR>.<int MINOR>.<int PATCH> (e.g., v1.0.1, v1.0.0, v0.1.2)",
                param,
            )
        return KontrolVersion(value)


@dataclass
class Cache:
    fileName: str  # noqa: N815
    url: str
    shortId: Optional[str] = None  # noqa: N815
    tag: Optional[str] = None
    lastModified: Optional[str] = None  # noqa: N815


@dataclass
class Job:
    jobId: str  # noqa: N815
    status: str


@dataclass
class Test:
    name: str
    version: str


@dataclass
class UploadFileMetadata:
    filename: str
    updated_at: str
    checksum: str
    size: int
    is_cache_zip: Optional[bool] = None  # Check if it's the [cacheHash].zip file
    folder: Optional[str] = None
