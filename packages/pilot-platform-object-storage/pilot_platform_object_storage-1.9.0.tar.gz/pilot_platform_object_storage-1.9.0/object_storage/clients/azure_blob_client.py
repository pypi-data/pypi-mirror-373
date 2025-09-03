# Copyright (C) 2023-2025 Indoc Systems
#
# Contact Indoc Systems for any questions regarding the use of this source code.

import logging
from collections.abc import Awaitable
from collections.abc import Callable
from io import BytesIO
from typing import Any

from azure.storage.blob import BlobBlock
from azure.storage.blob import BlobProperties
from azure.storage.blob.aio import BlobClient

from object_storage.clients.base_file_client import BaseFileClient
from object_storage.providers.azure import AzureClient

logger = logging.getLogger('pilot.object-storage')


class AzureBlobClient(BaseFileClient, AzureClient):
    """A client for interacting with Azure Blob Storage.

    Inherits from:
        - BaseObjectStorageblob_client: to provide a generic interface for object storage clients

    :param blob_sas_url:
        SAS URL to an Azure Blob Storage blob.
    """

    def __init__(
        self,
        blob_sas_url: str,
    ):
        self.blob_sas_url = blob_sas_url

    def _get_blob_name_from_sas(self) -> str:
        """Returns blob's key from sas URL."""

        try:
            url, _ = self.blob_sas_url.split('?')
            return url[url.rfind('/') + 1 :]
        except ValueError as exc:
            exc_msg = 'Missing sas token in `blob_sas_url`'
            logger.exception(exc_msg)
            raise ValueError(exc_msg) from exc

    async def is_exists(
        self,
    ) -> bool:
        """Checks if blob in the context exists."""

        try:
            async with BlobClient.from_blob_url(blob_url=self.blob_sas_url) as blob_client:
                return await blob_client.exists()
        except Exception as exc:
            raise self._handle_exception(exc)

    async def upload_file(
        self,
        file_path: str,
        chunk_size: int = 4 * 1024 * 1024,
        progress_callback: Callable[[str, int, int], Awaitable[Any]] | None = None,
    ) -> dict[str, Any]:
        """Uploads a file to a blob in the specified container."""

        key = self._get_blob_name_from_sas()
        try:
            async with BlobClient.from_blob_url(blob_url=self.blob_sas_url, max_block_size=chunk_size) as blob_client:
                return await self._upload(blob_client, file_path, key, progress_callback, chunk_size=chunk_size)
        except Exception as exc:
            raise self._handle_exception(exc)

    async def upload_file_from_bytes(
        self,
        buffer: BytesIO,
        chunk_size: int = 4 * 1024 * 1024,
        progress_callback: Callable[[str, int, int], Awaitable[Any]] | None = None,
    ) -> dict[str, Any]:
        """Uploads a file to a blob in the specified container."""

        key = self._get_blob_name_from_sas()
        try:
            async with BlobClient.from_blob_url(blob_url=self.blob_sas_url, max_block_size=chunk_size) as blob_client:
                return await self._upload_from_byte(blob_client, key, buffer, chunk_size, progress_callback)
        except Exception as exc:
            raise self._handle_exception(exc)

    async def resume_upload(
        self,
        file_path: str,
        chunk_size: int = 4 * 1024 * 1024,
        progress_callback: Callable[[str, int, int], Awaitable[Any]] | None = None,
    ) -> None:
        """Uploads a file to an Azure Blob Storage container, resuming an interrupted upload if there is an uncommitted
        block list."""

        key = self._get_blob_name_from_sas()
        try:
            async with BlobClient.from_blob_url(blob_url=self.blob_sas_url, max_block_size=chunk_size) as blob_client:
                await self._resume_upload(blob_client, key, file_path, chunk_size, progress_callback)
        except Exception as exc:
            raise self._handle_exception(exc)

    async def download_file_to_bytes(
        self,
        chunk_size: int | None = 4 * 1024 * 1024,
        progress_callback: Callable[[str, int, int], Awaitable[Any]] | None = None,
    ) -> bytes:
        """Download a file from the specified container."""

        key = self._get_blob_name_from_sas()
        try:
            async with BlobClient.from_blob_url(
                blob_url=self.blob_sas_url, max_chunk_get_size=chunk_size
            ) as blob_client:
                chunks_generator = self._download_bytes(blob_client, key, progress_callback=progress_callback)

                file_bytes = b''
                async for chunk in chunks_generator:
                    file_bytes += chunk
                return file_bytes
        except Exception as exc:
            raise self._handle_exception(exc)

    async def download_partial_file_to_bytes(
        self,
        max_size: int,
        chunk_size: int | None = 4 * 1024 * 1024,
        progress_callback: Callable[[str, int, int], Awaitable[Any]] | None = None,
    ) -> bytes:
        """Download partial content from the beginning of a file.

        This method is useful for previewing large files (e.g., CSV, JSON) where you only need to read the first portion
        of the file for display purposes.

        :param max_size: Maximum number of bytes to download from the beginning of the file.
        :param chunk_size: Size of chunks to use when downloading.
        :param progress_callback: Optional callback to track download progress.
        :return: Partial file content as bytes.
        """

        key = self._get_blob_name_from_sas()
        try:
            async with BlobClient.from_blob_url(
                blob_url=self.blob_sas_url, max_chunk_get_size=chunk_size
            ) as blob_client:
                chunks_generator = self._download_partial_bytes(
                    blob_client, key, max_size, progress_callback=progress_callback
                )

                file_bytes = b''
                async for chunk in chunks_generator:
                    file_bytes += chunk
                return file_bytes
        except Exception as exc:
            raise self._handle_exception(exc)

    async def download_file(
        self,
        file_path: str,
        chunk_size: int | None = 4 * 1024 * 1024,
        progress_callback: Callable[[str, int, int], Awaitable[Any]] | None = None,
    ) -> None:
        """Download a file from the specified container."""

        key = self._get_blob_name_from_sas()

        await self._create_parent_dir(file_path)

        try:
            async with BlobClient.from_blob_url(
                blob_url=self.blob_sas_url, max_chunk_get_size=chunk_size
            ) as blob_client:
                await self._download(
                    blob_client, key, file_path, get_chunk_size=chunk_size, progress_callback=progress_callback
                )
        except Exception as exc:
            raise self._handle_exception(exc)

    async def copy_file_from_url(
        self,
        source_url: str,
    ) -> str:
        """Copies a file from a URL to a blob in the specified container."""

        try:
            async with BlobClient.from_blob_url(blob_url=self.blob_sas_url) as blob_client:
                return await self._copy_from_url(blob_client, source_url)
        except Exception as exc:
            raise self._handle_exception(exc)

    async def delete_file(self) -> None:
        """Delete a file with all snapshots in a specific container."""

        try:
            async with BlobClient.from_blob_url(blob_url=self.blob_sas_url) as blob_client:
                return await self._delete(blob_client)
        except Exception as exc:
            raise self._handle_exception(exc)

    async def get_file_url(
        self,
    ) -> str:
        """Returns the URL that can be used to access the specified file."""

        try:
            async with BlobClient.from_blob_url(blob_url=self.blob_sas_url) as blob_client:
                return blob_client.url
        except Exception as exc:
            raise self._handle_exception(exc)

    async def get_file_properties(
        self,
    ) -> BlobProperties:
        """Retrieves the properties of a blob in the specified container."""
        try:
            async with BlobClient.from_blob_url(blob_url=self.blob_sas_url) as blob_client:
                return await blob_client.get_blob_properties()
        except Exception as exc:
            raise self._handle_exception(exc)

    async def commit_file(
        self,
        block_list: list[BlobBlock] | None = None,
    ) -> None:
        """Commits the uncommitted blocks of a blob, making them a part of the blob's content."""

        try:
            async with BlobClient.from_blob_url(blob_url=self.blob_sas_url) as blob_client:
                await self._commit_blob(blob_client, block_list=block_list)
        except Exception as exc:
            raise self._handle_exception(exc)

    async def get_file_chunks(
        self,
    ) -> tuple[list[BlobBlock], list[BlobBlock]]:
        """Returns a list of committeed and uncommitted the info of blob chunks."""

        try:
            async with BlobClient.from_blob_url(blob_url=self.blob_sas_url) as blob_client:
                return await self._get_blob_chunks(blob_client)
        except Exception as exc:
            raise self._handle_exception(exc)
