# outerport/resources/questions.py
from typing import List, AsyncGenerator
import requests
from outerport.models.question import Question, AsyncQuestion
from outerport.resources.base_resource import BaseResource, AsyncBaseResource
from outerport.models.document import Document, AsyncDocument
import aiohttp
import json


class QuestionsResource(BaseResource):
    def create(
        self,
        documents: List[Document],
        question: str,
        chunk_type: str = "32000_char_chunk",
        llm_provider: str = "openai",
        answer_mode: str = "reasoning",
    ) -> Question:
        """
        Ask a question referencing some documents, wait for job completion, return a final Question object.
        """
        url = f"{self.client.base_url}/api/v0/questions"
        headers = self.client._json_headers()

        payload = {
            "document_ids": [d.id for d in documents],
            "chunk_type": chunk_type,
            "question": question,
            "llm_provider": llm_provider,
            "answer_mode": answer_mode,
        }

        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()  # e.g. { "question_id": 123, "job_status_id": 45, ... }

        question_id = data.get("question_id")
        job_status_id = data.get("job_status_id")
        if question_id is None:
            raise ValueError("No question_id returned from create().")

        # If there's a job status, poll until done
        if job_status_id:
            self.client.job_statuses.wait_for_completion(job_status_id)

        # Retrieve the final question object
        return self.retrieve(question_id)

    def retrieve(self, question_id: str) -> Question:
        url = f"{self.client.base_url}/api/v0/questions/{question_id}"
        headers = self.client._json_headers()
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return Question.from_api(data, self.client)

    def delete(self, question_id: str) -> dict:
        url = f"{self.client.base_url}/api/v0/questions/{question_id}"
        headers = self.client._json_headers()
        resp = requests.delete(url, headers=headers)
        resp.raise_for_status()
        return resp.json()


STREAMING_CHUNK_SIZE = 8192


class AsyncQuestionsResource(AsyncBaseResource):
    async def create(
        self,
        documents: List[AsyncDocument],
        question: str,
        chunk_type: str = "32000_char_chunk",
        llm_provider: str = "openai",
        answer_mode: str = "reasoning",
    ) -> AsyncGenerator[AsyncQuestion, None]:
        """
        Ask a question referencing some documents and stream the updates as the question is being processed.
        Returns an async generator that yields Question objects with updated information.
        """
        url = f"{self.client.base_url}/api/v0/questions"
        headers = self.client._json_headers()

        payload = {
            "document_ids": [d.id for d in documents],
            "chunk_type": chunk_type,
            "question": question,
            "llm_provider": llm_provider,
            "answer_mode": answer_mode,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                resp.raise_for_status()
                data = (
                    await resp.json()
                )  # e.g. { "question_id": 123, "job_status_id": 45, ... }

                question_id = data.get("question_id")
                if question_id is None:
                    raise ValueError("No question_id returned from create().")

                # Use the stream endpoint to get updates
                stream_url = (
                    f"{self.client.base_url}/api/v0/questions/{question_id}/stream"
                )
                async with session.get(stream_url, headers=headers) as stream_resp:
                    stream_resp.raise_for_status()

                    # Process the SSE stream with controlled chunk size
                    buffer = ""
                    while True:
                        chunk = await stream_resp.content.read(
                            STREAMING_CHUNK_SIZE
                        )  # Read smaller chunks
                        if not chunk:
                            break
                        chunk_str = chunk.decode("utf-8")
                        buffer += chunk_str

                        # Process complete SSE messages
                        while "\n\n" in buffer:
                            message, buffer = buffer.split("\n\n", 1)
                            if message.startswith("data: "):
                                data_json = message[6:]  # Remove "data: " prefix
                                question_data = json.loads(data_json)
                                yield AsyncQuestion.from_api(question_data, self.client)

                            # Check for completion event
                            if message.startswith("event: done"):
                                return

    async def retrieve(self, question_id: str) -> AsyncQuestion:
        """
        Retrieve a question by ID.

        :param question_id: The ID of the question to retrieve.
        :return: The Question object.
        """
        url = f"{self.client.base_url}/api/v0/questions/{question_id}"
        headers = self.client._json_headers()

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return AsyncQuestion.from_api(data, self.client)

    async def delete(self, question_id: str) -> dict:
        """
        Delete a question by ID.

        :param question_id: The ID of the question to delete.
        :return: A dictionary containing the response from the server.
        """
        url = f"{self.client.base_url}/api/v0/questions/{question_id}"
        headers = self.client._json_headers()

        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers) as resp:
                resp.raise_for_status()
                return await resp.json()
