# outerport/models/question_model.py
from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING, TypeVar, Generic, Union
from pydantic import BaseModel, PrivateAttr, ConfigDict
from datetime import datetime
from abc import ABC, abstractmethod
from .document import Document

if TYPE_CHECKING:
    from outerport.client import OuterportClient
    from outerport.client import AsyncOuterportClient

T = TypeVar("T", bound=Union["OuterportClient", "AsyncOuterportClient"])


class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class Evidence(BaseModel):
    id: str
    evidence: str
    reasoning: str
    document_id: str
    relevancy_score: float
    sequence_number: int
    page_number: int
    bboxes: Optional[List[BoundingBox]] = None


class QuestionBase(BaseModel, Generic[T], ABC):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    question_text: str
    documents: List[Document] = []
    plan: Optional[str] = None
    evidences: List[Evidence] = []
    final_answer: Optional[str] = None
    answer_mode: str
    llm_provider: str
    chunk_type: str
    num_chunks: int
    num_chunks_processed: int
    job_status_id: Optional[str] = None
    current_state: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    _client: T = PrivateAttr()

    def __init__(self, **data):
        client = data.pop("_client", None)
        super().__init__(**data)
        self._client = client

    def _update_from_model(self, model: QuestionBase) -> None:
        """
        Update current model in-place from another model instance.
        """
        for field_name, value in model.model_dump().items():
            if field_name != "_client":
                setattr(self, field_name, value)

    @classmethod
    def from_api(cls, data: dict, client: T):
        return cls(_client=client, **data)

    @abstractmethod
    def reload(self) -> None:
        """Refresh this Question with the latest data from the server."""
        pass

    @abstractmethod
    def delete(self) -> dict:
        """Delete this question on the server."""
        pass


class Question(QuestionBase["OuterportClient"]):
    """
    Synchronous implementation of Question operations.
    """

    def reload(self) -> None:
        """
        Refresh this Question with the latest data from the server.
        """
        fresh = self._client.questions.retrieve(self.id)
        self._update_from_model(fresh)

    def delete(self) -> dict:
        """
        Delete this question on the server.
        """
        return self._client.questions.delete(self.id)


class AsyncQuestion(QuestionBase["AsyncOuterportClient"]):
    """
    Asynchronous implementation of Question operations.
    """

    async def reload(self) -> None:
        """
        Refresh this Question with the latest data from the server.
        """
        fresh = await self._client.questions.retrieve(self.id)
        self._update_from_model(fresh)

    async def delete(self) -> dict:
        """
        Delete this question on the server.
        """
        return await self._client.questions.delete(self.id)
