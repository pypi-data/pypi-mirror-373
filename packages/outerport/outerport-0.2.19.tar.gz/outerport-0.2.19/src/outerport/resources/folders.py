# outerport/resources/folders.py
from typing import List, Optional
import requests
import aiohttp
from outerport.models.folder import Folder, AsyncFolder
from outerport.resources.base_resource import BaseResource, AsyncBaseResource


class FoldersResource(BaseResource):
    def create(
        self,
        name: str,
        parent_id: Optional[str] = None,
    ) -> Folder:
        """
        Create a new folder.

        :param name: The name of the folder
        :param parent_id: Optional ID of the parent folder
        :return: The created Folder object
        """
        url = f"{self.client.base_url}/api/v0/folders"
        headers = self.client._json_headers()

        payload = {"name": name}
        if parent_id is not None:
            payload["parent_id"] = parent_id

        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return Folder.from_api(data, self.client)

    def list(
        self,
        parent_id: Optional[str] = None,
    ) -> List[Folder]:
        """
        List folders, optionally filtered by parent folder.

        :param parent_id: Optional parent folder ID to filter by. If not provided, returns root folders.
        :return: A list of Folder objects
        """
        url = f"{self.client.base_url}/api/v0/folders"
        headers = self.client._json_headers()

        params = {}
        if parent_id is not None:
            params["parent_id"] = parent_id

        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        raw_list = resp.json()

        return [Folder.from_api(d, self.client) for d in raw_list]

    def retrieve(self, folder_id: str) -> Folder:
        """
        Retrieve a single Folder by ID.

        :param folder_id: The ID of the folder to retrieve
        :return: The Folder object
        """
        url = f"{self.client.base_url}/api/v0/folders/{folder_id}"
        headers = self.client._json_headers()
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return Folder.from_api(data, self.client)

    def update(
        self,
        folder_id: str,
        name: Optional[str] = None,
        parent_id: Optional[str] = None,
    ) -> Folder:
        """
        Update a folder's metadata.

        :param folder_id: The ID of the folder to update
        :param name: Optional new name for the folder
        :param parent_id: Optional new parent folder ID
        :return: The updated Folder object
        """
        url = f"{self.client.base_url}/api/v0/folders/{folder_id}"
        headers = self.client._json_headers()

        payload = {}
        if name is not None:
            payload["name"] = name
        if parent_id is not None:
            payload["parent_id"] = parent_id

        resp = requests.put(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return Folder.from_api(data, self.client)

    def delete(self, folder_id: str) -> dict:
        """
        Delete a folder from the server.

        :param folder_id: The ID of the folder to delete
        :return: A dictionary containing the response from the server
        """
        url = f"{self.client.base_url}/api/v0/folders/{folder_id}"
        headers = self.client._json_headers()
        resp = requests.delete(url, headers=headers)
        resp.raise_for_status()
        return resp.json()

    def move_documents(self, folder_id: Optional[str], document_ids: List[str]) -> dict:
        """
        Move documents to a specific folder.

        :param folder_id: The ID of the folder to move documents to
        :param document_ids: List of document IDs to move
        :return: Response from the server
        """
        url = f"{self.client.base_url}/api/v0/folders/move-documents"
        headers = self.client._json_headers()

        payload = {
            "document_ids": document_ids,
            "folder_id": folder_id,
        }

        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()


class AsyncFoldersResource(AsyncBaseResource):
    async def create(
        self,
        name: str,
        parent_id: Optional[str] = None,
    ) -> AsyncFolder:
        """
        Create a new folder.

        :param name: The name of the folder
        :param parent_id: Optional ID of the parent folder
        :return: The created Folder object
        """
        url = f"{self.client.base_url}/api/v0/folders"
        headers = self.client._json_headers()

        payload = {"name": name}
        if parent_id is not None:
            payload["parent_id"] = parent_id

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return AsyncFolder.from_api(data, self.client)

    async def list(
        self,
        parent_id: Optional[str] = None,
    ) -> List[AsyncFolder]:
        """
        List folders, optionally filtered by parent folder.

        :param parent_id: Optional parent folder ID to filter by. If not provided, returns root folders.
        :return: A list of Folder objects
        """
        url = f"{self.client.base_url}/api/v0/folders"
        headers = self.client._json_headers()

        params = {}
        if parent_id is not None:
            params["parent_id"] = parent_id

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as resp:
                resp.raise_for_status()
                raw_list = await resp.json()
                return [AsyncFolder.from_api(d, self.client) for d in raw_list]

    async def retrieve(self, folder_id: str) -> AsyncFolder:
        """
        Retrieve a single Folder by ID.

        :param folder_id: The ID of the folder to retrieve
        :return: The Folder object
        """
        url = f"{self.client.base_url}/api/v0/folders/{folder_id}"
        headers = self.client._json_headers()

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return AsyncFolder.from_api(data, self.client)

    async def update(
        self,
        folder_id: str,
        name: Optional[str] = None,
        parent_id: Optional[str] = None,
    ) -> AsyncFolder:
        """
        Update a folder's metadata.

        :param folder_id: The ID of the folder to update
        :param name: Optional new name for the folder
        :param parent_id: Optional new parent folder ID
        :return: The updated Folder object
        """
        url = f"{self.client.base_url}/api/v0/folders/{folder_id}"
        headers = self.client._json_headers()

        payload = {}
        if name is not None:
            payload["name"] = name
        if parent_id is not None:
            payload["parent_id"] = parent_id

        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=headers, json=payload) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return AsyncFolder.from_api(data, self.client)

    async def delete(self, folder_id: str) -> dict:
        """
        Delete a folder from the server.

        :param folder_id: The ID of the folder to delete
        :return: A dictionary containing the response from the server
        """
        url = f"{self.client.base_url}/api/v0/folders/{folder_id}"
        headers = self.client._json_headers()

        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def move_documents(
        self, folder_id: Optional[str], document_ids: List[str]
    ) -> dict:
        """
        Move documents to a specific folder.

        :param folder_id: The ID of the folder to move documents to
        :param document_ids: List of document IDs to move
        :return: Response from the server
        """
        url = f"{self.client.base_url}/api/v0/folders/move-documents"
        headers = self.client._json_headers()

        payload = {
            "document_ids": document_ids,
            "folder_id": folder_id,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                resp.raise_for_status()
                return await resp.json()
