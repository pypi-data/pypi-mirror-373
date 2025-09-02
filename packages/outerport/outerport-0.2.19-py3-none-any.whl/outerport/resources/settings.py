from __future__ import annotations
import requests
from outerport.resources.base_resource import BaseResource, AsyncBaseResource
from outerport.models.setting import Setting, AsyncSetting
import aiohttp


class SettingsResource(BaseResource):
    def update(self, language: str) -> Setting:
        """
        Update user settings.

        :param language: The language to update the settings to.
        :return: The updated Setting object.
        """
        url = f"{self.client.base_url}/api/v0/settings"
        headers = self.client._json_headers()
        payload = {"language": language}
        resp = requests.put(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return Setting.from_api(data, self.client)

    def retrieve(self) -> Setting:
        """
        Get user settings.

        :return: The Setting object.
        """
        url = f"{self.client.base_url}/api/v0/settings"
        headers = self.client._json_headers()
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return Setting.from_api(data, self.client)


class AsyncSettingsResource(AsyncBaseResource):
    async def update(self, language: str) -> AsyncSetting:
        """
        Update user settings.

        :param language: The language to update the settings to.
        :return: The updated AsyncSetting object.
        """
        url = f"{self.client.base_url}/api/v0/settings"
        headers = self.client._json_headers()
        payload = {"language": language}
        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=headers, json=payload) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return AsyncSetting.from_api(data, self.client)

    async def retrieve(self) -> AsyncSetting:
        """
        Get user settings.

        :return: The AsyncSetting object.
        """
        url = f"{self.client.base_url}/api/v0/settings"
        headers = self.client._json_headers()
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return AsyncSetting.from_api(data, self.client)
