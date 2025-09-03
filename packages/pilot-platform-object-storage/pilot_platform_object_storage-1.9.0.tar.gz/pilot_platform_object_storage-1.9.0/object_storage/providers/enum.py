# Copyright (C) 2023-2025 Indoc Systems
#
# Contact Indoc Systems for any questions regarding the use of this source code.

from enum import Enum


class Provider(str, Enum):
    """The Provider enum class defines the supported object storage providers."""

    AZURE = 'azure'

    @property
    def value(self) -> str:
        return self._value_

    @classmethod
    def values(cls) -> list[str]:
        return [field.value for field in cls]
