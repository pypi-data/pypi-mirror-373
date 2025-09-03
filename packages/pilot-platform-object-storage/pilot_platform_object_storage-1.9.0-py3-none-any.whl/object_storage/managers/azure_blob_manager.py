# Copyright (C) 2023-2025 Indoc Systems
#
# Contact Indoc Systems for any questions regarding the use of this source code.

import logging
import urllib.parse
from datetime import datetime
from datetime import timedelta
from typing import Any

from azure.storage.blob import BlobProperties
from azure.storage.blob import BlobSasPermissions
from azure.storage.blob import ContainerSasPermissions
from azure.storage.blob import generate_blob_sas
from azure.storage.blob import generate_container_sas
from azure.storage.blob.aio import BlobServiceClient

from object_storage.managers.base_manager import BaseObjectStorageManager

logger = logging.getLogger('pilot.object-storage')


class AzureBlobStorageManager(BaseObjectStorageManager[BlobProperties]):
    """A client for interacting with Azure Blob Storage.

    Inherits from:
        - BaseObjectStorageManager: to provide a generic interface for object storage clients

    :param connection_string:
        A connection string or SAS URL to an Azure Blob Storage account.
    """

    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    async def create_container(self, container_name: str) -> dict[str, Any]:
        """Creates a new container with the specified name."""

        async with BlobServiceClient.from_connection_string(self.connection_string) as service:
            container_client = service.get_container_client(container_name)
            resp = await container_client.create_container()
            return resp

    async def delete_container(self, container_name: str) -> dict[str, Any]:
        """Deletes container with the specified name."""

        async with BlobServiceClient.from_connection_string(self.connection_string) as service:
            container_client = service.get_container_client(container_name)
            resp = await container_client.delete_container()
            return resp

    async def list_objects(self, container_name: str) -> list[BlobProperties]:
        """Lists blobs in the specified container."""

        async with BlobServiceClient.from_connection_string(self.connection_string) as service:
            container_client = service.get_container_client(container_name)
            blobs: list[BlobProperties] = []
            async for blob in container_client.list_blobs(results_per_page=10):
                blobs.append(blob)
            return blobs

    async def is_container_exists(self, container_name: str) -> bool:
        """Checks if container with `container_name` exists in the Storage."""

        async with BlobServiceClient.from_connection_string(self.connection_string) as service:
            container_client = service.get_container_client(container_name)
            return await container_client.exists()

    async def get_blob_sas(
        self,
        container: str,
        key: str,
        read: bool = False,
        write: bool = False,
        delete: bool = False,
        move: bool = False,
        delete_previous_version: bool = False,
        permanent_delete: bool = False,
        name_alias: str = '',
        expiry_in: timedelta = timedelta(hours=1),
    ) -> str:
        """
        Summary:
            Generates a URL for a blob with a SAS token with specified permissions.
        Parameters:
            - container(str): The container name.
            - key(str): The blob name.
            - read(bool): Read permission.
            - write(bool): Write permission.
            - delete(bool): Delete permission.
            - move(bool): Move permission.
            - delete_previous_version(bool): Delete version permission.
            - permanent_delete(bool): Permanent delete permission.
            - name_alias(str): User-friendly name for the file when downloading.
            - expiry_in(timedelta): The duration for which the SAS token is valid.
        Return:
            - str: The URL with the SAS token.
        """

        async with BlobServiceClient.from_connection_string(self.connection_string) as service:
            sas_token = generate_blob_sas(
                account_name=service.account_name,
                account_key=service.credential.account_key,
                blob_name=urllib.parse.unquote(key),
                container_name=container,
                permission=BlobSasPermissions(
                    read=read,
                    write=write,
                    delete=delete,
                    move=move,
                    delete_previous_version=delete_previous_version,
                    permanent_delete=permanent_delete,
                ),
                start=datetime.utcnow(),
                expiry=datetime.utcnow() + expiry_in,
                # rename the file with user friendly name for presigned url download
                content_disposition=f'attachment; filename="{name_alias}"',
            )
        return f'{service.url}{container}/{key}?{sas_token}'

    async def get_container_sas(
        self,
        container: str,
        read: bool = False,
        write: bool = False,
        list: bool = False,  # noqa: A002 keeping compatibility with Azure API
        delete: bool = False,
        delete_previous_version: bool = False,
        permanent_delete: bool = False,
    ) -> str:
        """Generates a URL for the storage account with a SAS token that allows read, write, list, and delete access to
        containers and blobs."""
        async with BlobServiceClient.from_connection_string(self.connection_string) as service:
            sas_token = generate_container_sas(
                account_name=service.account_name,
                account_key=service.credential.account_key,
                container_name=container,
                permission=ContainerSasPermissions(
                    read=read,
                    write=write,
                    list=list,
                    delete=delete,
                    delete_previous_version=delete_previous_version,
                    permanent_delete=permanent_delete,
                ),
                start=datetime.utcnow(),
                expiry=datetime.utcnow() + timedelta(hours=1),
            )
        return f'{service.url}{container}?{sas_token}'
