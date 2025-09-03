# Copyright (C) 2023-2025 Indoc Systems
#
# Contact Indoc Systems for any questions regarding the use of this source code.

from abc import ABC
from abc import abstractmethod
from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any


class BaseContainerClient(ABC):
    """Abstract base class for object storage clients."""

    @abstractmethod
    async def is_file_exists(self, key: str) -> bool:
        """Checks if file with specific key exists in container."""

        raise NotImplementedError()

    @abstractmethod
    async def upload_file(
        self,
        key: str,
        file_path: str,
        chunk_size: int = 4 * 1024 * 1024,
        progress_callback: Callable[[str, int, int], Awaitable[Any]] | None = None,
    ) -> dict[str, Any]:
        """Uploads a file to the specified bucket."""

        raise NotImplementedError()

    @abstractmethod
    async def download_file_to_bytes(
        self,
        key: str,
        chunk_size: int | None = 4 * 1024 * 1024,
        progress_callback: Callable[[str, int, int], Awaitable[Any]] | None = None,
    ) -> bytes:
        """Returns content in bytes of the specific file from the specified bucket."""

        raise NotImplementedError()

    @abstractmethod
    async def download_file(
        self,
        key: str,
        file_path: str,
        chunk_size: int | None = 4 * 1024 * 1024,
        progress_callback: Callable[[str, int, int], Awaitable[Any]] | None = None,
    ) -> None:
        """Download the specific file from the specified bucket to file_path."""

        raise NotImplementedError()

    @abstractmethod
    async def copy_file_from_url(
        self,
        key: str,
        source_url: str,
    ) -> str:
        """Copies a file from a URL to a blob in the specified container."""

        raise NotImplementedError()

    @abstractmethod
    async def delete_file(
        self,
        key: str,
    ) -> None:
        """Delete a file in the specified container."""

        raise NotImplementedError()

    @abstractmethod
    async def get_file_url(
        self,
        key: str,
    ) -> str:
        """Returns the URL that can be used to access the specified file."""

        raise NotImplementedError()
