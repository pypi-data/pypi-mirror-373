# outerport/models/document_model.py
from __future__ import annotations
from typing import Optional, TYPE_CHECKING, IO, List, Union, TypeVar, Generic
from pydantic import BaseModel, PrivateAttr, ConfigDict
from datetime import datetime
from abc import ABC, abstractmethod
from .retention_policy import RetentionPolicy, AsyncRetentionPolicy
from .core import VisualComponent

if TYPE_CHECKING:
    from outerport.client import OuterportClient
    from outerport.client import AsyncOuterportClient

T = TypeVar("T", bound=Union["OuterportClient", "AsyncOuterportClient"])


class DocumentBase(BaseModel, Generic[T], ABC):
    """
    A base abstract Pydantic model that represents a Document in the API.
    This class defines the common structure and interface for both sync and async document operations.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    folder_id: Optional[str] = None
    owner_id: Optional[str] = None
    file_path: Optional[str] = None
    file_type: str
    file_url: Optional[str] = None
    summary: str
    visibility: Optional[str] = None
    version: int
    num_pages: int
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

    @classmethod
    def from_api(cls, data: dict, client: T):
        """
        Helper to create a Document from an API response dict plus the client reference.
        """
        return cls(_client=client, **data)

    def _update_from_model(self, model: DocumentBase) -> None:
        """
        Update current model in-place from another model instance.
        """
        for field_name, value in model.model_dump().items():
            setattr(self, field_name, value)

    @abstractmethod
    def delete(self) -> dict:
        """Delete this document on the server."""
        pass

    @abstractmethod
    def reload(self) -> None:
        """Refresh this Document with the latest data from the server."""
        pass

    @abstractmethod
    def update_metadata(
        self,
        name: Optional[str] = None,
        folder_id: Optional[str] = None,
        summary: Optional[str] = None,
    ) -> None:
        """Update this document's metadata on the server."""
        pass

    @abstractmethod
    def update_file(self, file: IO[bytes], file_name: Optional[str] = None) -> None:
        """Update this document's file content on the server."""
        pass

    @property
    @abstractmethod
    def visual_components(self) -> List[VisualComponent]:
        """Get the visual components associated with this document."""
        pass

    @property
    @abstractmethod
    def tags(self) -> List[str]:
        """Get the tags associated with this document."""
        pass

    @abstractmethod
    def add_tags(self, tags: List[str]) -> None:
        """Add tags to this document."""
        pass

    @abstractmethod
    def remove_tags(self, tags: List[str]) -> None:
        """Remove tags from this document."""
        pass

    @property
    @abstractmethod
    def retention_policies(self) -> List[RetentionPolicy]:
        """Get the retention policies associated with this document."""
        pass

    @abstractmethod
    def add_retention_policy(self, retention_policy: RetentionPolicy) -> None:
        """Add a retention policy to this document."""
        pass

    @abstractmethod
    def remove_retention_policy(self, retention_policy: RetentionPolicy) -> None:
        """Remove the retention policy from this document."""
        pass


class Document(DocumentBase["OuterportClient"]):
    """
    Synchronous implementation of Document operations.
    """

    def delete(self) -> dict:
        """
        Delete this document on the server.
        """
        return self._client.documents.delete(self.id)

    def reload(self) -> None:
        """
        Refresh this Document with the latest data from the server.
        """
        fresh = self._client.documents.retrieve(self.id)
        self._update_from_model(fresh)

    def update_metadata(
        self,
        name: Optional[str] = None,
        folder_id: Optional[str] = None,
        summary: Optional[str] = None,
    ) -> None:
        """
        Update this document's metadata on the server and refresh the local instance.

        :param name: Optional new name for the document
        :param folder_id: Optional new folder ID for the document
        :param summary: Optional new summary for the document
        """
        fresh = self._client.documents.update_metadata(
            self.id,
            name=name,
            folder_id=folder_id,
            summary=summary,
        )
        self._update_from_model(fresh)

    def update_file(self, file: IO[bytes], file_name: Optional[str] = None) -> None:
        """
        Update this document's file content on the server and refresh the local instance.

        :param file: The new file content to upload
        :param file_name: Optional name for the file
        """
        fresh = self._client.documents.update_file(self.id, file, file_name)
        self._update_from_model(fresh)

    @property
    def visual_components(self) -> List[VisualComponent]:
        """
        Get the visual components associated with this document.
        """
        return self._client.documents.get_visual_components(self.id)

    @property
    def tags(self) -> List[str]:
        """
        Get the tags associated with this document.
        """
        return self._client.documents.get_tags(self.id)

    def add_tags(self, tags: List[str]) -> None:
        """
        Add tags to this document and refresh the local instance.

        :param tags: List of tag names to add to the document.
        """
        fresh = self._client.documents.add_tags(self.id, tags)
        self._update_from_model(fresh)

    def remove_tags(self, tags: List[str]) -> None:
        """
        Remove tags from this document and refresh the local instance.

        :param tags: List of tag names to remove from the document.
        """
        fresh = self._client.documents.remove_tags(self.id, tags)
        self._update_from_model(fresh)

    @property
    def retention_policies(self) -> List[RetentionPolicy]:
        """
        Get the retention policies associated with this document.
        """
        return self._client.documents.get_retention_policies(self.id)

    def add_retention_policy(self, retention_policy: RetentionPolicy) -> None:
        """
        Add a retention policy to this document and refresh the local instance.

        :param retention_policy: The retention policy to add to the document.
        """
        fresh = self._client.documents.add_retention_policy_by_id(
            self.id, retention_policy.id
        )
        self._update_from_model(fresh)

    def remove_retention_policy(self, retention_policy: RetentionPolicy) -> None:
        """
        Remove the retention policy from this document and refresh the local instance.
        """
        fresh = self._client.documents.remove_retention_policy_by_id(
            self.id, retention_policy.id
        )
        self._update_from_model(fresh)


class AsyncDocument(DocumentBase["AsyncOuterportClient"]):
    """
    Asynchronous implementation of Document operations.
    """

    async def delete(self) -> dict:
        """
        Delete this document on the server.
        """
        return await self._client.documents.delete(self.id)

    async def reload(self) -> None:
        """
        Refresh this Document with the latest data from the server.
        """
        fresh = await self._client.documents.retrieve(self.id)
        self._update_from_model(fresh)

    async def update_metadata(
        self,
        name: Optional[str] = None,
        folder_id: Optional[str] = None,
        summary: Optional[str] = None,
    ) -> None:
        """
        Update this document's metadata on the server and refresh the local instance.

        :param name: Optional new name for the document
        :param folder_id: Optional new folder ID for the document
        :param summary: Optional new summary for the document
        """
        fresh = await self._client.documents.update_metadata(
            self.id,
            name=name,
            folder_id=folder_id,
            summary=summary,
        )
        self._update_from_model(fresh)

    async def update_file(
        self, file: IO[bytes], file_name: Optional[str] = None
    ) -> None:
        """
        Update this document's file content on the server and refresh the local instance.

        :param file: The new file content to upload
        :param file_name: Optional name for the file
        """
        fresh = await self._client.documents.update_file(self.id, file, file_name)
        self._update_from_model(fresh)

    @property
    async def tags(self) -> List[str]:
        """
        Get all tags associated with this document.

        :return: A list of tag names.
        """
        return await self._client.documents.get_tags(self.id)

    async def add_tags(self, tags: List[str]) -> None:
        """
        Add tags to this document and refresh the local instance.

        :param tags: List of tag names to add to the document.
        """
        fresh = await self._client.documents.add_tags(self.id, tags)
        self._update_from_model(fresh)

    async def remove_tags(self, tags: List[str]) -> None:
        """
        Remove tags from this document and refresh the local instance.

        :param tags: List of tag names to remove from the document.
        """
        fresh = await self._client.documents.remove_tags(self.id, tags)
        self._update_from_model(fresh)

    @property
    async def retention_policies(self) -> List[AsyncRetentionPolicy]:
        """
        Get the retention policies associated with this document.
        """
        return await self._client.documents.get_retention_policies(self.id)

    async def add_retention_policy(self, retention_policy: RetentionPolicy) -> None:
        """
        Add a retention policy to this document and refresh the local instance.

        :param retention_policy: The retention policy to add to the document.
        """
        fresh = await self._client.documents.add_retention_policy_by_id(
            self.id, retention_policy.id
        )
        self._update_from_model(fresh)

    async def remove_retention_policy(self, retention_policy: RetentionPolicy) -> None:
        """
        Remove the retention policy from this document and refresh the local instance.
        """
        fresh = await self._client.documents.remove_retention_policy_by_id(
            self.id, retention_policy.id
        )
        self._update_from_model(fresh)
