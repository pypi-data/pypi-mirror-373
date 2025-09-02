from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Generic, Union
from pydantic import BaseModel, PrivateAttr, ConfigDict
from datetime import datetime
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from outerport.client import OuterportClient
    from outerport.client import AsyncOuterportClient

T = TypeVar("T", bound=Union["OuterportClient", "AsyncOuterportClient"])


class SettingBase(BaseModel, Generic[T], ABC):
    """
    A base abstract Pydantic model that represents User Settings in your API.
    This class defines the common structure and interface for both sync and async operations.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str
    language: str
    created_at: datetime
    updated_at: datetime

    # Private attribute to store the client
    _client: T = PrivateAttr()

    def __init__(self, **data):
        """
        Pydantic's __init__ is overridden so we can attach _client after the model is constructed.
        """
        client = data.pop("_client", None)
        super().__init__(**data)
        self._client = client

    def _update_from_model(self, model: SettingBase) -> None:
        """
        Update current model in-place from another model instance.
        """
        for field_name, value in model.model_dump().items():
            setattr(self, field_name, value)

    @classmethod
    def from_api(cls, data: dict, client: T):
        """
        Helper to create a Setting from an API response dict plus the client reference.
        """
        return cls(_client=client, **data)

    @abstractmethod
    def save(self) -> None:
        """Save the current settings to the server."""
        pass

    @abstractmethod
    def reload(self) -> None:
        """Refresh this Setting with the latest data from the server."""
        pass


class Setting(SettingBase["OuterportClient"]):
    """
    Synchronous implementation of Setting operations.
    """

    def save(self) -> None:
        """
        Save the current settings to the server.
        """
        # Use the update method with just the language
        result = self._client.settings.update(self.language)
        # Update current model with the returned data
        self._update_from_model(result)

    def reload(self) -> None:
        """
        Refresh this Setting with the latest data from the server.
        """
        fresh = self._client.settings.retrieve()
        self._update_from_model(fresh)


class AsyncSetting(SettingBase["AsyncOuterportClient"]):
    """
    Asynchronous implementation of Setting operations.
    """

    async def save(self) -> None:
        """
        Save the current settings to the server.
        """
        result = await self._client.settings.update(self.language)
        # Update current model with the returned data
        self._update_from_model(result)

    async def reload(self) -> None:
        """
        Refresh this Setting with the latest data from the server.
        """
        fresh = await self._client.settings.retrieve()
        self._update_from_model(fresh)
