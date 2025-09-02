from typing import List, Optional
import requests
from outerport.models.retention_policy import RetentionPolicy, AsyncRetentionPolicy
from outerport.resources.base_resource import BaseResource, AsyncBaseResource
import aiohttp


class RetentionPoliciesResource(BaseResource):
    def create(
        self,
        name: str,
        description: Optional[str] = None,
        duration_days: int = 7,
        delete_after_expiry: bool = True,
    ) -> RetentionPolicy:
        """
        Create a new retention policy.

        Args:
            name: str
            description: Optional[str]
            duration_days: int
            delete_after_expiry: bool

        Returns:
            RetentionPolicy: The created retention policy
        """
        # Check if the retention policy already exists
        existing_policy = self.retrieve_by_name(name)
        if existing_policy:
            return existing_policy

        url = f"{self.client.base_url}/api/v0/retention-policies"
        headers = self.client._json_headers()
        payload = {
            "name": name,
            "duration_days": duration_days,
            "delete_after_expiry": delete_after_expiry,
        }
        if description is not None:
            payload["description"] = description
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        return RetentionPolicy.from_api(resp.json(), self.client)

    def list(self) -> List[RetentionPolicy]:
        """
        List all retention policies.

        Returns:
            List[RetentionPolicy]: List of retention policies
        """
        url = f"{self.client.base_url}/api/v0/retention-policies"
        headers = self.client._json_headers()

        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        return [RetentionPolicy.from_api(d, self.client) for d in resp.json()]

    def retrieve(self, policy_id: str) -> RetentionPolicy:
        """
        Retrieve a single retention policy by ID.

        Args:
            policy_id: The ID of the retention policy to retrieve

        Returns:
            RetentionPolicy: The requested retention policy
        """
        url = f"{self.client.base_url}/api/v0/retention-policies/{policy_id}"
        headers = self.client._json_headers()

        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        return RetentionPolicy.from_api(resp.json(), self.client)

    def update(
        self,
        policy_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        duration_days: Optional[int] = None,
        delete_after_expiry: Optional[bool] = None,
    ) -> RetentionPolicy:
        """
        Update an existing retention policy.

        Args:
            policy_id: The ID of the retention policy to update
            name: Optional[str]
            description: Optional[str]
            duration_days: Optional[int]
            delete_after_expiry: Optional[bool]

        Returns:
            RetentionPolicy: The updated retention policy
        """
        url = f"{self.client.base_url}/api/v0/retention-policies/{policy_id}"
        headers = self.client._json_headers()

        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if duration_days is not None:
            payload["duration_days"] = duration_days
        if delete_after_expiry is not None:
            payload["delete_after_expiry"] = delete_after_expiry

        resp = requests.put(url, headers=headers, json=payload)
        resp.raise_for_status()
        return RetentionPolicy.from_api(resp.json(), self.client)

    def delete(self, policy_id: str) -> RetentionPolicy:
        """
        Delete a retention policy.

        Args:
            policy_id: The ID of the retention policy to delete

        Returns:
            RetentionPolicy: The deleted retention policy
        """
        url = f"{self.client.base_url}/api/v0/retention-policies/{policy_id}"
        headers = self.client._json_headers()

        resp = requests.delete(url, headers=headers)
        resp.raise_for_status()
        return RetentionPolicy.from_api(resp.json(), self.client)

    def retrieve_by_name(self, name: str) -> Optional[RetentionPolicy]:
        """
        Retrieve a single retention policy by name.

        Args:
            name: The name of the retention policy to retrieve

        Returns:
            Optional[RetentionPolicy]: The requested retention policy, or None if not found
        """
        policies = self.list()
        for policy in policies:
            if policy.name == name:
                return policy
        return None


class AsyncRetentionPoliciesResource(AsyncBaseResource):
    async def create(
        self,
        name: str,
        description: Optional[str] = None,
        duration_days: int = 7,
        delete_after_expiry: bool = True,
    ) -> AsyncRetentionPolicy:
        """
        Create a new retention policy asynchronously.

        Args:
            name: str
            description: Optional[str]
            duration_days: int
            delete_after_expiry: bool

        Returns:
            RetentionPolicy: The created retention policy
        """
        # Check if the retention policy already exists
        existing_policy = await self.retrieve_by_name(name)
        if existing_policy:
            return existing_policy

        url = f"{self.client.base_url}/api/v0/retention-policies"
        headers = self.client._json_headers()
        payload = {
            "name": name,
            "duration_days": duration_days,
            "delete_after_expiry": delete_after_expiry,
        }
        if description is not None:
            payload["description"] = description

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return AsyncRetentionPolicy.from_api(data, self.client)

    async def list(self) -> List[AsyncRetentionPolicy]:
        """
        List all retention policies asynchronously.

        Returns:
            List[RetentionPolicy]: List of retention policies
        """
        url = f"{self.client.base_url}/api/v0/retention-policies"
        headers = self.client._json_headers()

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return [AsyncRetentionPolicy.from_api(d, self.client) for d in data]

    async def retrieve(self, policy_id: str) -> AsyncRetentionPolicy:
        """
        Retrieve a single retention policy by ID asynchronously.

        Args:
            policy_id: The ID of the retention policy to retrieve

        Returns:
            RetentionPolicy: The requested retention policy
        """
        url = f"{self.client.base_url}/api/v0/retention-policies/{policy_id}"
        headers = self.client._json_headers()

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return AsyncRetentionPolicy.from_api(data, self.client)

    async def update(
        self,
        policy_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        duration_days: Optional[int] = None,
        delete_after_expiry: Optional[bool] = None,
    ) -> AsyncRetentionPolicy:
        """
        Update an existing retention policy asynchronously.

        Args:
            policy_id: The ID of the retention policy to update
            name: Optional[str]
            description: Optional[str]
            duration_days: Optional[int]
            delete_after_expiry: Optional[bool]

        Returns:
            RetentionPolicy: The updated retention policy
        """
        url = f"{self.client.base_url}/api/v0/retention-policies/{policy_id}"
        headers = self.client._json_headers()

        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if duration_days is not None:
            payload["duration_days"] = duration_days
        if delete_after_expiry is not None:
            payload["delete_after_expiry"] = delete_after_expiry

        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=headers, json=payload) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return AsyncRetentionPolicy.from_api(data, self.client)

    async def delete(self, policy_id: str) -> AsyncRetentionPolicy:
        """
        Delete a retention policy asynchronously.

        Args:
            policy_id: The ID of the retention policy to delete

        Returns:
            RetentionPolicy: The deleted retention policy
        """
        url = f"{self.client.base_url}/api/v0/retention-policies/{policy_id}"
        headers = self.client._json_headers()

        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return AsyncRetentionPolicy.from_api(data, self.client)

    async def retrieve_by_name(self, name: str) -> Optional[AsyncRetentionPolicy]:
        """
        Retrieve a single retention policy by name asynchronously.

        Args:
            name: The name of the retention policy to retrieve

        Returns:
            Optional[RetentionPolicy]: The requested retention policy, or None if not found
        """
        policies = await self.list()
        for policy in policies:
            if policy.name == name:
                return policy
        return None
