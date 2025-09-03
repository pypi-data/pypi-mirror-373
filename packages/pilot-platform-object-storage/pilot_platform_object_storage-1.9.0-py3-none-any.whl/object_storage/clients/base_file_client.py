# Copyright (C) 2023-2025 Indoc Systems
#
# Contact Indoc Systems for any questions regarding the use of this source code.

from abc import ABC
from abc import abstractmethod
from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any


class BaseFileClient(ABC):
    """Abstract base class for object storage clients."""

    @abstractmethod
    async def upload_file(
        self,
        file_path: str,
        chunk_size: int = 4 * 1024 * 1024,
        progress_callback: Callable[[str, int, int], Awaitable[Any]] | None = None,
    ) -> dict[str, Any]:
        """Uploads a file to the specified bucket."""

        raise NotImplementedError()

    @abstractmethod
    async def download_file_to_bytes(
        self,
        chunk_size: int | None = 4 * 1024 * 1024,
        progress_callback: Callable[[str, int, int], Awaitable[Any]] | None = None,
    ) -> bytes:
        """Returns content in bytes of the specific file from the specified bucket."""

        raise NotImplementedError()

    @abstractmethod
    async def download_partial_file_to_bytes(
        self,
        max_size: int,
        chunk_size: int | None = 4 * 1024 * 1024,
        progress_callback: Callable[[str, int, int], Awaitable[Any]] | None = None,
    ) -> bytes:
        """Returns partial content in bytes of the specific file from the specified bucket.

        :param max_size: Maximum number of bytes to download from the beginning of the file.
        :param chunk_size: Size of chunks to use when downloading.
        :param progress_callback: Optional callback to track download progress.
        :return: Partial file content as bytes.
        """

        raise NotImplementedError()

    @abstractmethod
    async def download_file(
        self,
        file_path: str,
        chunk_size: int | None = 4 * 1024 * 1024,
        progress_callback: Callable[[str, int, int], Awaitable[Any]] | None = None,
    ) -> None:
        """Download the specific file from the specified bucket to file_path."""

        raise NotImplementedError()

    @abstractmethod
    async def copy_file_from_url(
        self,
        source_url: str,
    ) -> str:
        """Copies a file from a URL to a blob in the specified container."""

        raise NotImplementedError()

    @abstractmethod
    async def delete_file(
        self,
    ) -> None:
        """Copies a file from a URL to a blob in the specified container."""

        raise NotImplementedError()

    @abstractmethod
    async def get_file_url(
        self,
    ) -> str:
        """Returns the URL that can be used to access the specified file."""

        raise NotImplementedError()

    @abstractmethod
    async def is_exists(self) -> bool:
        """Checks if file in the context exists."""

        raise NotImplementedError()
