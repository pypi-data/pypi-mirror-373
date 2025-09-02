from typing import Optional

from .resources.documents import DocumentsResource
from .resources.folders import FoldersResource
from .resources.questions import QuestionsResource
from .resources.settings import SettingsResource
from .resources.job_statuses import JobStatusesResource
from .resources.retention_policies import RetentionPoliciesResource
from .resources.documents import AsyncDocumentsResource
from .resources.folders import AsyncFoldersResource
from .resources.job_statuses import AsyncJobStatusesResource
from .resources.questions import AsyncQuestionsResource
from .resources.settings import AsyncSettingsResource
from .resources.retention_policies import AsyncRetentionPoliciesResource


class OuterportClient:
    """
    Outerport API client.
    It exposes each resource class as a property.
    """

    def __init__(
        self, api_key: Optional[str] = None, base_url: str = "http://localhost:8080"
    ) -> None:
        """
        :param api_key: API key or bearer token for Authorization.
        :param base_url: Base URL of the Outerport API.
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.is_async = False

        # Resource namespaces
        self.documents = DocumentsResource(self)
        self.folders = FoldersResource(self)
        self.questions = QuestionsResource(self)
        self.settings = SettingsResource(self)
        self.job_statuses = JobStatusesResource(self)
        self.retention_policies = RetentionPoliciesResource(self)

    def _json_headers(self) -> dict:
        """
        Return standard JSON headers. Adds Authorization if api_key is set.
        """
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _form_headers(self) -> dict:
        """
        Return headers for multipart/form-data (file uploads).
        """
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers


class AsyncOuterportClient:
    """
    Asynchronous Outerport API client.
    It exposes each resource class as a property.
    """

    def __init__(
        self, api_key: Optional[str] = None, base_url: str = "http://localhost:8080"
    ) -> None:
        """
        :param api_key: API key or bearer token for Authorization.
        :param base_url: Base URL of the Outerport API.
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.is_async = True

        # Resource namespaces
        # You'll need to create async versions of these resources
        self.documents = AsyncDocumentsResource(self)
        self.folders = AsyncFoldersResource(self)
        self.questions = AsyncQuestionsResource(self)
        self.settings = AsyncSettingsResource(self)
        self.job_statuses = AsyncJobStatusesResource(self)
        self.retention_policies = AsyncRetentionPoliciesResource(self)

    def _json_headers(self) -> dict:
        """
        Return standard JSON headers. Adds Authorization if api_key is set.
        """
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _form_headers(self) -> dict:
        """
        Return headers for multipart/form-data (file uploads).
        """
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
