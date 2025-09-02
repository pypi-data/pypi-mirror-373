# outerport/resources/documents.py
from typing import IO, List, Optional, Dict, Any
import requests
import aiohttp
from outerport.models.document import Document, AsyncDocument
from outerport.resources.base_resource import BaseResource, AsyncBaseResource
from outerport.models.retention_policy import RetentionPolicy, AsyncRetentionPolicy
from outerport.models.core import VisualComponent


class DocumentsResource(BaseResource):
    def create(
        self,
        file: IO[bytes],
        file_name: Optional[str] = None,
        folder_id: Optional[str] = None,
        processing_hint: Optional[str] = None,
        timeout: int = 480, 
    ) -> Document:
        """
        Upload a document and wait synchronously for it to finish processing.
        Returns a fully-populated Document object.

        :param file: The file to upload.
        :param file_name: The name of the file to upload.
        :param folder_id: The ID of the folder to create the document in.
        :param processing_hint: The processing hint for the document.
        :param timeout: The timeout in seconds for the document to finish processing.
        :return: The uploaded Document object.
        """

        url = f"{self.client.base_url}/api/v0/documents"
        headers = self.client._form_headers()

        if not file_name:
            file_name = getattr(file, "name", None)
            if not file_name:
                raise ValueError("File has no name")

        files = {"file": (file_name, file, "application/octet-stream")}

        data = {}
        if folder_id is not None:
            data["folder_id"] = str(folder_id)
        if file_name is not None:
            data["name"] = file_name
        if processing_hint is not None:
            data["processing_hint"] = processing_hint

        resp = requests.post(url, headers=headers, files=files, data=data)
        resp.raise_for_status()

        data = resp.json()  # e.g. { "job_status_id": 1, "document_id": "123", ... }
        job_status_id = data.get("job_status_id")
        document_id = data.get("document_id")
        if not job_status_id or not document_id:
            raise ValueError("Upload response missing job_status_id or document_id.")

        # Wait for job to complete
        self.client.job_statuses.wait_for_completion(job_status_id, timeout=timeout)

        # Now retrieve the final Document from the server
        return self.retrieve(document_id)

    def from_url(
        self,
        url: str,
        name: Optional[str] = None,
        folder_id: Optional[str] = None,
    ) -> Document:
        """
        Create a document from a URL and wait for it to finish processing.
        Returns a fully-populated Document object.

        :param url: The URL to create the document from
        :param name: Optional custom name for the document
        :param folder_id: The ID of the folder to create the document in.
        :return: The created Document object
        """
        api_url = f"{self.client.base_url}/api/v0/documents"
        headers = self.client._form_headers()

        data: Dict[str, Any] = {"url": url}
        if name:
            data["name"] = name
        if folder_id is not None:
            data["folder_id"] = str(folder_id)

        resp = requests.post(api_url, headers=headers, data=data)
        resp.raise_for_status()

        data = resp.json()
        job_status_id = data.get("job_status_id")
        document_id = data.get("document_id")

        if not job_status_id or not document_id:
            raise ValueError("Creation response missing job_status_id or document_id.")

        # Wait for job to complete
        self.client.job_statuses.wait_for_completion(job_status_id)

        # Now retrieve the final Document from the server
        return self.retrieve(document_id)

    def list(
        self,
        folder_id: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> List[Document]:
        """
        List all documents as a list of Document objects.

        :param folder_id: The ID of the folder to filter documents by.
        :param tag: The name of the tag to filter documents by.
        :return: A list of Document objects.
        """
        url = f"{self.client.base_url}/api/v0/documents"
        headers = self.client._json_headers()
        params = {}
        if folder_id:
            params["folder_id"] = folder_id
        if tag:
            params["tag_name"] = tag
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        raw_list = resp.json()  # e.g. [ { "id": 1, ... }, { ... } ]

        return [Document.from_api(d, self.client) for d in raw_list]

    def retrieve(self, document_id: str) -> Document:
        """
        Retrieve a single Document by ID.

        :param document_id: The ID of the document to retrieve.
        :return: The Document object.
        """
        url = f"{self.client.base_url}/api/v0/documents/{document_id}"
        headers = self.client._json_headers()
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return Document.from_api(data, self.client)

    def delete(self, document_id: str) -> dict:
        """
        Delete the document from the server.

        :param document_id: The ID of the document to delete.
        :return: A dictionary containing the response from the server.
        """
        url = f"{self.client.base_url}/api/v0/documents/{document_id}"
        headers = self.client._json_headers()
        resp = requests.delete(url, headers=headers)
        resp.raise_for_status()
        return resp.json()

    def update_metadata(
        self,
        document_id: str,
        name: Optional[str] = None,
        folder_id: Optional[str] = None,
        summary: Optional[str] = None,
    ) -> Document:
        """
        Update a document's metadata.

        :param document_id: The ID of the document to update.
        :param name: Optional new name for the document.
        :param folder_id: Optional new folder ID for the document.
        :param summary: Optional new summary for the document.
        :return: The updated Document object.
        """
        url = f"{self.client.base_url}/api/v0/documents/{document_id}"
        headers = self.client._json_headers()

        payload = {}
        if name is not None:
            payload["name"] = name
        if folder_id is not None:
            payload["folder_id"] = folder_id
        if summary is not None:
            payload["summary"] = summary

        resp = requests.put(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return Document.from_api(data, self.client)

    def update_file(
        self, document_id: str, file: IO[bytes], file_name: Optional[str] = None
    ) -> Document:
        """
        Update a document's file content and wait for processing to complete.

        :param document_id: The ID of the document to update.
        :param file: The new file content to upload.
        :param file_name: Optional name for the file.
        :return: The updated Document object.
        """
        url = f"{self.client.base_url}/api/v0/documents/{document_id}/file"
        headers = self.client._form_headers()

        if not file_name:
            file_name = getattr(file, "name", None)
            if not file_name:
                raise ValueError("File has no name")

        files = {"file": (file_name, file, "application/octet-stream")}
        resp = requests.put(url, headers=headers, files=files)
        resp.raise_for_status()

        data = resp.json()
        job_status_id = data.get("job_status_id")
        if not job_status_id:
            raise ValueError("Update response missing job_status_id.")

        # Wait for job to complete
        self.client.job_statuses.wait_for_completion(job_status_id)

        # Now retrieve the final Document from the server
        return self.retrieve(document_id)

    def get_visual_components(self, document_id: str) -> List[VisualComponent]:
        """
        Get the visual components associated with a document.

        :param document_id: The ID of the document to get visual components for.
        :return: A list of VisualComponent objects.
        """
        datas: List[VisualComponent] = []
        for page_num in list(range(self.retrieve(document_id).num_pages)):
            url = f"{self.client.base_url}/api/v0/documents/{document_id}/visual-components"
            headers = self.client._json_headers()
            resp = requests.get(url, headers=headers, params={"page_number": page_num})
            resp.raise_for_status()
            data = resp.json()
            visual_components = [VisualComponent(**d) for d in data]
            datas.extend(visual_components)
        return datas

    def list_tags(self) -> List[str]:
        """
        List all tags that the user has access to.

        :return: A list of tag names.
        """
        url = f"{self.client.base_url}/api/v0/documents/tags"
        headers = self.client._json_headers()
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return []
        return [tag["name"] for tag in data]

    def get_tags(self, document_id: str) -> List[str]:
        """
        Get all tags for a document.

        :param document_id: The ID of the document to get tags for.
        :return: A list of tag names.
        """
        url = f"{self.client.base_url}/api/v0/documents/{document_id}/tags"
        headers = self.client._json_headers()
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return []
        return [tag["name"] for tag in data]

    def add_tags(self, document_id: str, tags: List[str]) -> Document:
        """
        Add tags to a document.

        :param document_id: The ID of the document to tag.
        :param tags: List of tag names to add to the document.
        :return: The updated Document object.
        """
        url = f"{self.client.base_url}/api/v0/documents/{document_id}/tags"
        headers = self.client._json_headers()
        payload = {"tag_names": tags}

        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return Document.from_api(data, self.client)

    def remove_tags(self, document_id: str, tags: List[str]) -> Document:
        """
        Remove tags from a document.

        :param document_id: The ID of the document to remove tags from.
        :param tags: List of tag names to remove from the document.
        :return: The updated Document object.
        """
        url = f"{self.client.base_url}/api/v0/documents/{document_id}/tags"
        headers = self.client._json_headers()
        payload = {"tag_names": tags}

        resp = requests.delete(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return Document.from_api(data, self.client)

    def search(
        self,
        query: str,
        folder_id: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> List[Document]:
        """
        Search for documents based on the provided query and filters.

        :param query: The search query string.
        :param folder_id: Optional folder ID to filter documents by.
        :param tag: Optional tag name to filter documents by.
        :return: List of Document objects.
        """
        url = f"{self.client.base_url}/api/v0/documents/search"
        headers = self.client._json_headers()

        payload: Dict[str, Any] = {"query": query}
        if folder_id is not None:
            payload["folder_id"] = folder_id
        if tag is not None:
            payload["tag_name"] = tag

        # Initiate search
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

        search_id = data.get("search_id")
        job_status_id = data.get("job_status_id")

        if not search_id:
            raise ValueError("Search response missing search_id")

        # Wait for search job to complete if there is one
        if job_status_id:
            self.client.job_statuses.wait_for_completion(job_status_id)

        # Get final results
        url = f"{self.client.base_url}/api/v0/documents/search/{search_id}"
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        documents = data["documents"]
        return [Document.from_api(d, self.client) for d in documents]

    def get_retention_policies(self, document_id: str) -> List[RetentionPolicy]:
        """
        Get all retention policies for a document.

        :param document_id: The ID of the document to get retention policies for.
        :return: A list of RetentionPolicy objects.
        """
        url = (
            f"{self.client.base_url}/api/v0/documents/{document_id}/retention-policies"
        )
        headers = self.client._json_headers()
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return [RetentionPolicy.from_api(d, self.client) for d in data]

    def add_retention_policy_by_id(
        self, document_id: str, retention_policy_id: str
    ) -> Document:
        """
        Add a retention policy to a document.

        :param document_id: The ID of the document to add the retention policy to.
        :param retention_policy_id: The ID of the retention policy to add to the document.
        """
        url = (
            f"{self.client.base_url}/api/v0/documents/{document_id}/retention-policies"
        )
        headers = self.client._json_headers()
        params = {"retention_policy_id": retention_policy_id}
        resp = requests.post(url, headers=headers, params=params)
        resp.raise_for_status()
        # Reload the document to get the latest state
        return self.retrieve(document_id)

    def remove_retention_policy_by_id(
        self, document_id: str, retention_policy_id: str
    ) -> Document:
        """
        Remove the retention policy from a document.

        :param document_id: The ID of the document to remove the retention policy from.
        """
        url = f"{self.client.base_url}/api/v0/documents/{document_id}/retention-policies/{retention_policy_id}"
        headers = self.client._json_headers()
        resp = requests.delete(url, headers=headers)
        resp.raise_for_status()
        # Reload the document to get the latest state
        return self.retrieve(document_id)


class AsyncDocumentsResource(AsyncBaseResource):
    async def create(
        self,
        file: IO[bytes],
        file_name: Optional[str] = None,
        folder_id: Optional[str] = None,
        processing_hint: Optional[str] = None,
        timeout: int = 480, 
    ) -> AsyncDocument:
        """
        Upload a document and wait asynchronously for it to finish processing.
        Returns a fully-populated Document object.

        :param file: The file to upload.
        :param file_name: The name of the file to upload.
        :param folder_id: The ID of the folder to create the document in.
        :param processing_hint: The processing hint for the document.
        :param timeout: The timeout in seconds for the document to finish processing.
        :return: The uploaded Document object.
        """
        url = f"{self.client.base_url}/api/v0/documents"
        headers = self.client._form_headers()

        if not file_name:
            file_name = getattr(file, "name", None)
            if not file_name:
                raise ValueError("File has no name")

        mpwriter = aiohttp.MultipartWriter("form-data")

        file_part = mpwriter.append(file)
        file_part.set_content_disposition(
            "form-data", name="file", filename=file_name, quote_fields=False
        )

        if file_name is not None:
            name_part = mpwriter.append(file_name)
            name_part.set_content_disposition("form-data", name="name")

        if folder_id is not None:
            folder_part = mpwriter.append(str(folder_id))
            folder_part.set_content_disposition("form-data", name="folder_id")

        if processing_hint is not None:
            mpwriter.append(processing_hint)
            mpwriter.set_content_disposition("form-data", name="processing_hint")

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=mpwriter) as resp:
                resp.raise_for_status()
                data = (
                    await resp.json()
                )  # e.g. { "job_status_id": 1, "document_id": "123", ... }

                job_status_id = data.get("job_status_id")
                document_id = data.get("document_id")
                if not job_status_id or not document_id:
                    raise ValueError(
                        "Upload response missing job_status_id or document_id."
                    )

                # Wait for job to complete
                await self.client.job_statuses.wait_for_completion(job_status_id, timeout=timeout)

                # Now retrieve the final Document from the server
                return await self.retrieve(document_id)

    async def from_url(
        self,
        url: str,
        name: Optional[str] = None,
        folder_id: Optional[str] = None,
    ) -> AsyncDocument:
        """
        Create a document from a URL and wait for it to finish processing.
        Returns a fully-populated Document object.

        :param url: The URL to create the document from
        :param name: Optional custom name for the document
        :param folder_id: The ID of the folder to create the document in.
        :return: The created Document object
        """
        api_url = f"{self.client.base_url}/api/v0/documents"
        headers = self.client._form_headers()

        data = aiohttp.FormData()
        data.add_field("url", url)
        if name:
            data.add_field("name", name)
        if folder_id is not None:
            data.add_field("folder_id", str(folder_id))

        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, headers=headers, data=data) as resp:
                resp.raise_for_status()
                data = await resp.json()

                job_status_id = data.get("job_status_id")
                document_id = data.get("document_id")
                if not job_status_id or not document_id:
                    raise ValueError(
                        "Creation response missing job_status_id or document_id."
                    )

                # Wait for job to complete
                await self.client.job_statuses.wait_for_completion(job_status_id)

                # Now retrieve the final Document from the server
                return await self.retrieve(document_id)

    async def list(
        self,
        folder_id: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> List[AsyncDocument]:
        """
        List all documents as a list of Document objects.

        :param folder_id: The ID of the folder to filter documents by.
        :param tag: The name of the tag to filter documents by.
        :return: A list of Document objects.
        """
        url = f"{self.client.base_url}/api/v0/documents"
        headers = self.client._json_headers()

        params = {}
        if folder_id:
            params["folder_id"] = folder_id
        if tag:
            params["tag_name"] = tag

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as resp:
                resp.raise_for_status()
                raw_list = await resp.json()  # e.g. [ { "id": 1, ... }, { ... } ]

                return [AsyncDocument.from_api(d, self.client) for d in raw_list]

    async def retrieve(self, document_id: str) -> AsyncDocument:
        """
        Retrieve a single Document by ID.

        :param document_id: The ID of the document to retrieve.
        :return: The Document object.
        """
        url = f"{self.client.base_url}/api/v0/documents/{document_id}"
        headers = self.client._json_headers()

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return AsyncDocument.from_api(data, self.client)

    async def delete(self, document_id: str) -> dict:
        """
        Delete the document from the server.

        :param document_id: The ID of the document to delete.
        :return: A dictionary containing the response from the server.
        """
        url = f"{self.client.base_url}/api/v0/documents/{document_id}"
        headers = self.client._json_headers()

        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def update_metadata(
        self,
        document_id: str,
        name: Optional[str] = None,
        folder_id: Optional[str] = None,
        summary: Optional[str] = None,
    ) -> AsyncDocument:
        """
        Update a document's metadata.

        :param document_id: The ID of the document to update.
        :param name: Optional new name for the document.
        :param folder_id: Optional new folder ID for the document.
        :param summary: Optional new summary for the document.
        :return: The updated Document object.
        """
        url = f"{self.client.base_url}/api/v0/documents/{document_id}"
        headers = self.client._json_headers()

        payload = {}
        if name is not None:
            payload["name"] = name
        if folder_id is not None:
            payload["folder_id"] = folder_id
        if summary is not None:
            payload["summary"] = summary

        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=headers, json=payload) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return AsyncDocument.from_api(data, self.client)

    async def update_file(
        self, document_id: str, file: IO[bytes], file_name: Optional[str] = None
    ) -> AsyncDocument:
        """
        Update a document's file content and wait for processing to complete.

        :param document_id: The ID of the document to update.
        :param file: The new file content to upload.
        :param file_name: Optional name for the file.
        :return: The updated Document object.
        """
        url = f"{self.client.base_url}/api/v0/documents/{document_id}/file"
        headers = self.client._form_headers()

        if not file_name:
            file_name = getattr(file, "name", None)
            if not file_name:
                raise ValueError("File has no name")

        mpwriter = aiohttp.MultipartWriter("form-data")

        part = mpwriter.append(file)
        part.set_content_disposition(
            "form-data", name="file", filename=file_name, quote_fields=False
        )

        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=headers, data=mpwriter) as resp:
                resp.raise_for_status()
                data = await resp.json()

                job_status_id = data.get("job_status_id")
                if not job_status_id:
                    raise ValueError("Update response missing job_status_id.")

                # Wait for job to complete
                await self.client.job_statuses.wait_for_completion(job_status_id)

                # Now retrieve the final Document from the server
                return await self.retrieve(document_id)

    async def get_visual_components(self, document_id: str) -> List[VisualComponent]:
        """
        Get the visual components associated with a document.

        :param document_id: The ID of the document to get visual components for.
        :return: A list of VisualComponent objects.
        """
        datas: List[VisualComponent] = []
        document = await self.retrieve(document_id)
        for page_num in list(range(document.num_pages)):
            url = f"{self.client.base_url}/api/v0/documents/{document_id}/visual-components"
            headers = self.client._json_headers()
            resp = requests.get(url, headers=headers, params={"page_number": page_num})
            resp.raise_for_status()
            data = resp.json()
            visual_components = [VisualComponent(**d) for d in data]
            datas.extend(visual_components)
        return datas

    async def get_tags(self, document_id: str) -> List[str]:
        """
        Get all tags for a document.

        :param document_id: The ID of the document to get tags for.
        :return: A list of tag names.
        """
        url = f"{self.client.base_url}/api/v0/documents/{document_id}/tags"
        headers = self.client._json_headers()

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                if not data:
                    return []
                return [tag["name"] for tag in data]

    async def add_tags(self, document_id: str, tags: List[str]) -> AsyncDocument:
        """
        Add tags to a document.

        :param document_id: The ID of the document to tag.
        :param tags: List of tag names to add to the document.
        :return: The updated Document object.
        """
        url = f"{self.client.base_url}/api/v0/documents/{document_id}/tags"
        headers = self.client._json_headers()
        payload = {"tag_names": tags}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return AsyncDocument.from_api(data, self.client)

    async def remove_tags(self, document_id: str, tags: List[str]) -> AsyncDocument:
        """
        Remove tags from a document.

        :param document_id: The ID of the document to remove tags from.
        :param tags: List of tag names to remove from the document.
        :return: The updated Document object.
        """
        url = f"{self.client.base_url}/api/v0/documents/{document_id}/tags"
        headers = self.client._json_headers()
        payload = {"tag_names": tags}

        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers, json=payload) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return AsyncDocument.from_api(data, self.client)

    async def search(
        self,
        query: str,
        folder_id: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> List[AsyncDocument]:
        """
        Search for documents based on the provided query and filters.

        :param query: The search query string.
        :param folder_id: Optional folder ID to filter documents by.
        :param tag: Optional tag name to filter documents by.
        :return: List of Document objects.
        """
        url = f"{self.client.base_url}/api/v0/documents/search"
        headers = self.client._json_headers()

        payload: Dict[str, Any] = {"query": query}
        if folder_id is not None:
            payload["folder_id"] = folder_id
        if tag is not None:
            payload["tag_name"] = tag

        async with aiohttp.ClientSession() as session:
            # Initiate search
            async with session.post(url, headers=headers, json=payload) as resp:
                resp.raise_for_status()
                data = await resp.json()

                search_id = data.get("search_id")
                job_status_id = data.get("job_status_id")

                if not search_id:
                    raise ValueError("Search response missing search_id")

                # Wait for search job to complete if there is one
                if job_status_id:
                    await self.client.job_statuses.wait_for_completion(job_status_id)

                # Get final results
                url = f"{self.client.base_url}/api/v0/documents/search/{search_id}"
                async with session.get(url, headers=headers) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    documents = data["documents"]
                    return [AsyncDocument.from_api(d, self.client) for d in documents]

    async def get_retention_policies(
        self, document_id: str
    ) -> List[AsyncRetentionPolicy]:
        """
        Get all retention policies for a document.

        :param document_id: The ID of the document to get retention policies for.
        :return: A list of RetentionPolicy objects.
        """
        url = (
            f"{self.client.base_url}/api/v0/documents/{document_id}/retention-policies"
        )
        headers = self.client._json_headers()

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return [AsyncRetentionPolicy.from_api(d, self.client) for d in data]

    async def add_retention_policy_by_id(
        self, document_id: str, retention_policy_id: str
    ) -> AsyncDocument:
        """
        Add a retention policy to a document.

        :param document_id: The ID of the document to add the retention policy to.
        :param retention_policy_id: The ID of the retention policy to add to the document.
        """
        url = (
            f"{self.client.base_url}/api/v0/documents/{document_id}/retention-policies"
        )
        headers = self.client._json_headers()
        params = {"retention_policy_id": retention_policy_id}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, params=params) as resp:
                resp.raise_for_status()
                # Reload the document to get the latest state
                return await self.retrieve(document_id)

    async def remove_retention_policy_by_id(
        self, document_id: str, retention_policy_id: str
    ) -> AsyncDocument:
        """
        Remove the retention policy from a document.

        :param document_id: The ID of the document to remove the retention policy from.
        """
        url = f"{self.client.base_url}/api/v0/documents/{document_id}/retention-policies/{retention_policy_id}"
        headers = self.client._json_headers()

        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers) as resp:
                resp.raise_for_status()
                # Reload the document to get the latest state
                return await self.retrieve(document_id)
