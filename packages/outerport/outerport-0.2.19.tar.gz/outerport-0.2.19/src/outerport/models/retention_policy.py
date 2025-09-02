from __future__ import annotations
from typing import TYPE_CHECKING, Optional, TypeVar, Generic, Union
from pydantic import BaseModel, PrivateAttr, ConfigDict
from datetime import datetime
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from outerport.client import OuterportClient
    from outerport.client import AsyncOuterportClient

T = TypeVar("T", bound=Union["OuterportClient", "AsyncOuterportClient"])


class RetentionPolicyBase(BaseModel, Generic[T], ABC):
    """
    A base abstract Pydantic model that represents a Retention Policy in your API.
    This class defines the common structure and interface for both sync and async operations.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    description: Optional[str] = None
    duration_days: int
    delete_after_expiry: bool = False
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

    def _update_from_model(self, model: RetentionPolicyBase) -> None:
        """
        Update current model in-place from another model instance.
        """
        for field_name, value in model.model_dump().items():
            setattr(self, field_name, value)

    @classmethod
    def from_api(cls, data: dict, client: T):
        """
        Helper to create a RetentionPolicy from an API response dict plus the client reference.
        """
        return cls(_client=client, **data)

    @abstractmethod
    def save(self) -> None:
        """Save the current retention policy to the server."""
        pass

    @abstractmethod
    def reload(self) -> None:
        """Refresh this RetentionPolicy with the latest data from the server."""
        pass

    @abstractmethod
    def delete(self) -> None:
        """Delete this retention policy from the server."""
        pass


class RetentionPolicy(RetentionPolicyBase["OuterportClient"]):
    """
    Synchronous implementation of RetentionPolicy operations.
    """

    def save(self) -> None:
        """
        Save the current retention policy to the server.
        """
        if hasattr(self, "id"):
            # Update existing policy
            result = self._client.retention_policies.update(
                self.id,
                self.name,
                self.description,
                self.duration_days,
                self.delete_after_expiry,
            )
        else:
            # Create new policy
            result = self._client.retention_policies.create(
                self.name,
                self.description,
                self.duration_days,
                self.delete_after_expiry,
            )

        # Update current model with returned data
        self._update_from_model(result)

    def reload(self) -> None:
        """
        Refresh this RetentionPolicy with the latest data from the server.
        """
        if not hasattr(self, "id"):
            raise ValueError("Cannot reload a retention policy without an ID")

        fresh = self._client.retention_policies.retrieve(self.id)
        self._update_from_model(fresh)

    def delete(self) -> None:
        """
        Delete this retention policy from the server.
        """
        if not hasattr(self, "id"):
            raise ValueError("Cannot delete a retention policy without an ID")

        self._client.retention_policies.delete(self.id)


class AsyncRetentionPolicy(RetentionPolicyBase["AsyncOuterportClient"]):
    """
    Asynchronous implementation of RetentionPolicy operations.
    """

    async def save(self) -> None:
        """
        Save the current retention policy to the server.
        """
        if hasattr(self, "id"):
            # Update existing policy
            result = await self._client.retention_policies.update(
                self.id,
                self.name,
                self.description,
                self.duration_days,
                self.delete_after_expiry,
            )
        else:
            # Create new policy
            result = await self._client.retention_policies.create(
                self.name,
                self.description,
                self.duration_days,
                self.delete_after_expiry,
            )

        # Update current model with returned data
        self._update_from_model(result)

    async def reload(self) -> None:
        """
        Refresh this RetentionPolicy with the latest data from the server.
        """
        if not hasattr(self, "id"):
            raise ValueError("Cannot reload a retention policy without an ID")

        fresh = await self._client.retention_policies.retrieve(self.id)
        self._update_from_model(fresh)

    async def delete(self) -> None:
        """
        Delete this retention policy from the server.
        """
        if not hasattr(self, "id"):
            raise ValueError("Cannot delete a retention policy without an ID")

        await self._client.retention_policies.delete(self.id)
