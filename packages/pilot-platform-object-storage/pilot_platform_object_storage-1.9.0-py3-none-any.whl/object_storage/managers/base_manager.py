# Copyright (C) 2023-2025 Indoc Systems
#
# Contact Indoc Systems for any questions regarding the use of this source code.

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

T = TypeVar('T')


class BaseObjectStorageManager(ABC, Generic[T]):
    """Abstract base class for object storage managers."""

    @abstractmethod
    async def create_container(self, container_name: str) -> dict[str, Any]:
        """Creates a container in the object storage service."""

        raise NotImplementedError()

    @abstractmethod
    async def delete_container(self, container_name: str) -> dict[str, Any]:
        """Deletes container from the object storage service."""

        raise NotImplementedError()

    @abstractmethod
    async def list_objects(self, container_name: str) -> list[T]:
        """Lists all objects in the specified container."""

        raise NotImplementedError()

    @abstractmethod
    async def is_container_exists(self, container_name: str) -> bool:
        """Checks if container with `container_name` exists in the Storage."""

        raise NotImplementedError()
