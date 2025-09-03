# Copyright (C) 2023-2025 Indoc Systems
#
# Contact Indoc Systems for any questions regarding the use of this source code.

import logging
import math
from collections.abc import AsyncGenerator
from collections.abc import Awaitable
from collections.abc import Callable
from io import BytesIO
from pathlib import Path
from typing import Any
from typing import cast
from uuid import uuid4

import aiofiles
from aiofiles.os import makedirs
from aiofiles.os import stat
from aiofiles.threadpool.binary import AsyncBufferedReader
from azure.core.exceptions import ClientAuthenticationError
from azure.core.exceptions import HttpResponseError
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobBlock
from azure.storage.blob.aio import BlobClient
from azure.storage.blob.aio import ContainerClient

logger = logging.getLogger('pilot.object-storage')


class AzureClient:
    """Base base class for object storage clients."""

    def _handle_exception(self, exc: Exception) -> Exception:
        """Handles exceptions raised during Azure Blob Storage operations."""
        if isinstance(exc, ClientAuthenticationError):
            logger.exception(
                'Failed to authenticate with Azure. Check the correctness of tenant_id, client_id, or client_secret.'
            )
        elif isinstance(exc, ResourceNotFoundError):
            logger.info('The requested resource was not found.')
        elif isinstance(exc, HttpResponseError):
            logger.exception(f'Error in HTTP response: {exc.status_code} - {exc.reason}')
        else:
            logger.exception('Unexpected error occurred')
        return exc

    async def _create_parent_dir(self, file_path: str) -> None:
        """The funtion will create the parent folder by the file path."""

        dirname = str(Path(file_path).parent)
        await makedirs(dirname, exist_ok=True)

    async def _upload(
        self,
        client: BlobClient,
        file_path: str,
        key: str,
        progress_callback: Callable[[str, int, int], Awaitable[Any]] | None = None,
        chunk_size: int = 4 * 1024 * 1024,
    ) -> dict[str, Any]:
        """Upload a file to sas URL."""

        async with aiofiles.open(file_path, mode='rb') as f:
            file_length = (await stat(file_path)).st_size
            uploaded_blocks = await self._upload_chunks(client, f, file_length, key, chunk_size, progress_callback)
            return await self._commit_blob(client, uploaded_blocks)

    async def _upload_chunks(
        self,
        client: BlobClient,
        file_obj: AsyncBufferedReader | BytesIO,
        file_length: int,
        key: str,
        chunk_size: int = 4 * 1024 * 1024,
        progress_callback: Callable[[str, int, int], Awaitable[Any]] | None = None,
        current: int = 0,
    ) -> list[BlobBlock]:
        """Upload the file by cutting into chunks.

        If there is progress callback, will upload the chunk from the current point.
        """
        uploaded_blocks = []
        while True:
            if isinstance(file_obj, BytesIO):
                chunk = file_obj.read(chunk_size)
            else:
                chunk = await file_obj.read(chunk_size)
            if not chunk:
                break
            block_id = str(uuid4())
            await client.stage_block(block_id=block_id, data=chunk)
            current = min(current + len(chunk), file_length)
            if progress_callback:
                await progress_callback(key, current, file_length)
            uploaded_blocks.append(BlobBlock(block_id=block_id))
        return uploaded_blocks

    async def _upload_from_byte(
        self,
        client: BlobClient,
        key: str,
        buffer: BytesIO,
        chunk_size: int = 4 * 1024 * 1024,
        progress_callback: Callable[[str, int, int], Awaitable[Any]] | None = None,
    ) -> dict[str, Any]:
        """Upload a file from bytes to the specified container."""

        length = buffer.getbuffer().nbytes
        uploaded_blocks = await self._upload_chunks(client, buffer, length, key, chunk_size, progress_callback)
        return await self._commit_blob(client, uploaded_blocks)

    async def _commit_blob(self, client: BlobClient, block_list: list[BlobBlock] | None = None) -> dict[str, Any]:
        """Commits the uncommitted blocks of a blob, making them a part of the blob's content."""
        if block_list:
            return await client.commit_block_list(block_list)
        _, block_list = await client.get_block_list('uncommitted')
        return await client.commit_block_list(block_list)

    async def _download_bytes(
        self,
        client: BlobClient,
        key: str,
        get_chunk_size: int | None = 4 * 1024 * 1024,
        progress_callback: Callable[[str, int, int], Awaitable[Any]] | None = None,
    ) -> AsyncGenerator[bytes, bytes]:
        """Download a file bytes from the specified container."""

        stream = await client.download_blob(max_concurrency=4)
        current = 0
        chunk_size = get_chunk_size or 4 * 1024 * 1024
        number_of_chunks = math.ceil(stream.size / chunk_size)
        for _ in range(number_of_chunks):
            chunk = await stream.read(chunk_size)
            yield chunk
            current += len(chunk)
            if progress_callback:
                await progress_callback(key, current, stream.size)

    async def _download_partial_bytes(
        self,
        client: BlobClient,
        key: str,
        max_size: int,
        get_chunk_size: int | None = 4 * 1024 * 1024,
        progress_callback: Callable[[str, int, int], Awaitable[Any]] | None = None,
    ) -> AsyncGenerator[bytes, bytes]:
        """Download partial file bytes from the specified container.

        :param max_size: Maximum number of bytes to download from the beginning of the file.
        """

        # Download only the specified range from the beginning of the file
        stream = await client.download_blob(offset=0, length=max_size, max_concurrency=4)
        current = 0
        chunk_size = get_chunk_size or 4 * 1024 * 1024

        # Calculate the number of chunks needed for the partial download
        actual_size = min(max_size, stream.size) if hasattr(stream, 'size') else max_size
        number_of_chunks = math.ceil(actual_size / chunk_size)

        for _ in range(number_of_chunks):
            # Ensure we don't read more than the requested max_size
            remaining_bytes = max_size - current
            if remaining_bytes <= 0:
                break

            read_size = min(chunk_size, remaining_bytes)
            chunk = await stream.read(read_size)

            if not chunk:
                break

            yield chunk
            current += len(chunk)
            if progress_callback:
                await progress_callback(key, current, max_size)

    async def _download(
        self,
        client: BlobClient,
        key: str,
        file_path: str,
        get_chunk_size: int | None = 4 * 1024 * 1024,
        progress_callback: Callable[[str, int, int], Awaitable[Any]] | None = None,
    ) -> None:
        """Download a file from the specified container."""

        # if file exist, raise error
        if Path(file_path).exists():
            raise FileExistsError(f'File {file_path} already exists.')

        async with aiofiles.open(file_path, 'ab') as file:
            chunks_generator = self._download_bytes(client, key, get_chunk_size, progress_callback)
            async for chunk in chunks_generator:
                await file.write(chunk)

    async def _copy_from_url(
        self,
        client: BlobClient,
        source_url: str,
    ) -> str:
        """Copies a file from a URL to a blob in the specified container."""

        resp = await client.start_copy_from_url(source_url=source_url)
        copy_status = resp['copy_status']
        return cast(str, copy_status)

    async def _delete(self, client: BlobClient) -> None:
        """Delete the blob and all its snapshots."""

        return await client.delete_blob(delete_snapshots='include')

    async def _resume_upload(
        self,
        client: BlobClient,
        key: str,
        file_path: str,
        chunk_size: int = 4 * 1024 * 1024,
        progress_callback: Callable[[str, int, int], Awaitable[Any]] | None = None,
    ) -> None:
        """Uploads a file to an Azure Blob Storage container, resuming an interrupted upload if there is an uncommitted
        block list."""

        uploaded_blocks = []
        offset = 0

        _, block_list = await client.get_block_list('uncommitted')
        for block in block_list:
            uploaded_blocks.append(BlobBlock(block_id=block.id))
            offset += block.size

        current = offset
        file_length = (await stat(file_path)).st_size
        file_renaming_length = file_length - offset

        if file_renaming_length:
            async with aiofiles.open(file_path, mode='rb') as f:
                await f.seek(offset)
                uploaded_blocks += await self._upload_chunks(
                    client, f, file_length, key, chunk_size, progress_callback, current
                )

        await self._commit_blob(client, uploaded_blocks)

    async def _get_blob_chunks(
        self,
        client: BlobClient,
    ) -> tuple[list[BlobBlock], list[BlobBlock]]:
        """Returns a list of committeed and uncommitted the info of blob chunks."""

        commited_block_list, uncommited_block_list = await client.get_block_list('all')

        return commited_block_list, uncommited_block_list

    async def _get_blob_versions(
        self,
        client: ContainerClient,
        key: str,
    ) -> list[str]:
        """Get the version ids of a blob."""

        items = client.list_blobs(name_starts_with=key, include=['versions', 'deleted'])
        version_ids = [item['version_id'] async for item in items if item['version_id'] is not None]
        if version_ids == []:
            raise ResourceNotFoundError(message='No version id found')
        return version_ids

    async def _delete_versions(
        self,
        container_client: ContainerClient,
        key: str,
        version_ids: list[str],
        permanent_delete: bool = False,
    ) -> None:
        """Delete the specific version of the blob."""
        for version in version_ids:
            if permanent_delete:
                await container_client.delete_blob(blob=key, version_id=version, blob_delete_type='permanent')
            else:
                await container_client.delete_blob(blob=key, version_id=version)

    async def _undetele_blob_versions(self, container_client: ContainerClient, key: str) -> None:
        """Undelete the blob versions."""
        blob_client = container_client.get_blob_client(key)
        await blob_client.undelete_blob()

    async def _restore_latest_version(
        self,
        container_client: ContainerClient,
        key: str,
    ) -> str:
        """Restore the latest version of the blob."""
        version_ids = await self._get_blob_versions(container_client, key)
        version_ids.sort(reverse=True)

        # always restore the latest version, since we assume there is only one soft delete version
        latest_version = version_ids[0]
        version_blob_url = await self._format_blob_version_url(container_client, key, latest_version)
        blob_client = container_client.get_blob_client(key)

        # use the copy from url to restore the latest version
        await self._copy_from_url(blob_client, version_blob_url)
        return latest_version

    async def _format_blob_version_url(
        self,
        container_client: ContainerClient,
        key: str,
        version_id: str,
    ) -> str:
        """Format the versioned blob url."""
        blob_client = container_client.get_blob_client(key)
        return f'{blob_client.url}&versionId={version_id}'
