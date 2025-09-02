# outerport/models/folder.py
from __future__ import annotations
from typing import Optional, TYPE_CHECKING, List, Union, TypeVar, Generic
from pydantic import BaseModel, PrivateAttr, ConfigDict
from datetime import datetime
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from outerport.client import OuterportClient
    from outerport.client import AsyncOuterportClient

T = TypeVar("T", bound=Union["OuterportClient", "AsyncOuterportClient"])


class FolderBase(BaseModel, Generic[T], ABC):
    """
    A base abstract Pydantic model that represents a Folder in the API.
    This class defines the common structure and interface for both sync and async folder operations.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    parent_id: Optional[str] = None
    owner_id: str
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
        Helper to create a Folder from an API response dict plus the client reference.
        """
        return cls(_client=client, **data)

    def _update_from_model(self, model: FolderBase) -> None:
        """
        Update current model in-place from another model instance.
        """
        for field_name, value in model.model_dump().items():
            setattr(self, field_name, value)

    @abstractmethod
    def delete(self) -> dict:
        """Delete this folder on the server."""
        pass

    @abstractmethod
    def reload(self) -> None:
        """Refresh this Folder with the latest data from the server."""
        pass

    @abstractmethod
    def update(
        self,
        name: Optional[str] = None,
        parent_id: Optional[str] = None,
    ) -> None:
        """Update this folder's metadata on the server."""
        pass

    @abstractmethod
    def move_documents(self, document_ids: List[str]) -> dict:
        """Move documents to this folder."""
        pass

    @abstractmethod
    def list_subfolders(self) -> List[FolderBase[T]]:
        """List all subfolders of this folder."""
        pass

    @abstractmethod
    def list_documents(self):
        """List all documents in this folder."""
        pass


class Folder(FolderBase["OuterportClient"]):
    """
    Synchronous implementation of Folder operations.
    """

    def delete(self) -> dict:
        """
        Delete this folder on the server.
        """
        return self._client.folders.delete(self.id)

    def reload(self) -> None:
        """
        Refresh this Folder with the latest data from the server.
        """
        fresh = self._client.folders.retrieve(self.id)
        self._update_from_model(fresh)

    def update(
        self,
        name: Optional[str] = None,
        parent_id: Optional[str] = None,
    ) -> None:
        """
        Update this folder's metadata on the server and refresh the local instance.

        :param name: Optional new name for the folder
        :param parent_id: Optional new parent folder ID
        """
        fresh = self._client.folders.update(
            self.id,
            name=name,
            parent_id=parent_id,
        )
        self._update_from_model(fresh)

    def move_documents(self, document_ids: List[str]) -> dict:
        """
        Move documents to this folder.

        :param document_ids: List of document IDs to move to this folder
        :return: Response from the server
        """
        return self._client.folders.move_documents(self.id, document_ids)

    def list_subfolders(self) -> List[Folder]:
        """
        List all subfolders of this folder.

        :return: List of Folder objects that are children of this folder
        """
        return self._client.folders.list(parent_id=self.id)

    def list_documents(self):
        """
        List all documents in this folder.

        :return: List of Document objects in this folder
        """
        return self._client.documents.list(folder_id=self.id)


class AsyncFolder(FolderBase["AsyncOuterportClient"]):
    """
    Asynchronous implementation of Folder operations.
    """

    async def delete(self) -> dict:
        """
        Delete this folder on the server.
        """
        return await self._client.folders.delete(self.id)

    async def reload(self) -> None:
        """
        Refresh this Folder with the latest data from the server.
        """
        fresh = await self._client.folders.retrieve(self.id)
        self._update_from_model(fresh)

    async def update(
        self,
        name: Optional[str] = None,
        parent_id: Optional[str] = None,
    ) -> None:
        """
        Update this folder's metadata on the server and refresh the local instance.

        :param name: Optional new name for the folder
        :param parent_id: Optional new parent folder ID
        """
        fresh = await self._client.folders.update(
            self.id,
            name=name,
            parent_id=parent_id,
        )
        self._update_from_model(fresh)

    async def move_documents(self, document_ids: List[str]) -> dict:
        """
        Move documents to this folder.

        :param document_ids: List of document IDs to move to this folder
        :return: Response from the server
        """
        return await self._client.folders.move_documents(self.id, document_ids)

    async def list_subfolders(self) -> List[AsyncFolder]:
        """
        List all subfolders of this folder.

        :return: List of AsyncFolder objects that are children of this folder
        """
        return await self._client.folders.list(parent_id=self.id)

    async def list_documents(self):
        """
        List all documents in this folder.

        :return: List of AsyncDocument objects in this folder
        """
        return await self._client.documents.list(folder_id=self.id)
