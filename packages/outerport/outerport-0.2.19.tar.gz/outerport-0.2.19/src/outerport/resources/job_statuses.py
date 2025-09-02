# outerport/resources/job_statuses.py
import time
import requests
from outerport.models.job_status import JobStatus
from outerport.resources.base_resource import BaseResource, AsyncBaseResource
import aiohttp
import asyncio


class JobStatusesResource(BaseResource):
    def retrieve(self, job_status_id: str) -> JobStatus:
        """
        Fetch a job status by ID.

        :param job_status_id: The ID of the job status to fetch.
        :return: The job status.
        """
        url = f"{self.client.base_url}/api/v0/job-statuses/{job_status_id}"
        headers = self.client._json_headers()
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return JobStatus(**data)

    def wait_for_completion(
        self, job_status_id: str, timeout: int = 240, poll_interval: float = 1.0
    ) -> JobStatus:
        """
        Poll for a job to complete or error out.

        :param timeout: Max seconds to wait.
        :param poll_interval: Seconds between polls.
        :raises RuntimeError: If the job ends in an error state.
        :raises TimeoutError: If the job doesn't complete within the timeout period.
        :raises requests.exceptions.RequestException: If there's an error communicating with the API.
        :return: The completed JobStatus
        """
        start_time = time.time()
        while True:
            js = self.retrieve(job_status_id)
            if js.is_done():
                return js
            if js.is_error():
                raise RuntimeError(f"Job {job_status_id} errored: {js.error_message}")
            if (time.time() - start_time) > timeout:
                raise TimeoutError(
                    f"Job {job_status_id} did not complete in {timeout} s."
                )
            time.sleep(poll_interval)


class AsyncJobStatusesResource(AsyncBaseResource):
    async def retrieve(self, job_status_id: str) -> JobStatus:
        """
        Fetch a job status by ID asynchronously.

        :param job_status_id: The ID of the job status to fetch.
        :return: The job status.
        """
        url = f"{self.client.base_url}/api/v0/job-statuses/{job_status_id}"
        headers = self.client._json_headers()

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return JobStatus(**data)

    async def wait_for_completion(
        self, job_status_id: str, timeout: int = 240, poll_interval: float = 1.0
    ) -> JobStatus:
        """
        Poll for a job to complete or error out asynchronously.

        :param timeout: Max seconds to wait.
        :param poll_interval: Seconds between polls.
        :raises RuntimeError: If the job ends in an error state.
        :raises TimeoutError: If the job doesn't complete within the timeout period.
        :raises aiohttp.ClientError: If there's an error communicating with the API.
        :return: The completed JobStatus
        """
        start_time = time.time()
        while True:
            js = await self.retrieve(job_status_id)
            if js.is_done():
                return js
            if js.is_error():
                raise RuntimeError(f"Job {job_status_id} errored: {js.error_message}")
            if (time.time() - start_time) > timeout:
                raise TimeoutError(
                    f"Job {job_status_id} did not complete in {timeout} s."
                )
            await asyncio.sleep(poll_interval)
