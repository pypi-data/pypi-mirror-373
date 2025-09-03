import os
import requests
from dotenv import load_dotenv
from typing import Optional, AsyncGenerator
import io
import vectorshift
import json as json_lib
import aiohttp
import asyncio

load_dotenv()

class RequestClient:
    def __init__(self):
        self.api_key = os.environ.get('VECTORSHIFT_API_KEY')
        self.base_url = 'https://api.vectorshift.ai/v1'

    def request(self, method: str, endpoint: str, query: dict = None, json: dict = None, api_key: Optional[str] = None, files: list[tuple[str, io.BufferedReader]] = None):
        api_key = api_key or vectorshift.api_key or self.api_key
        headers = {
            "Authorization": f"Bearer {api_key}",
        }

        if files:
            data = {}
            for key, value in json.items():
                if isinstance(value, (dict, list) ):
                    data[key] = json_lib.dumps(value)
                else:
                    data[key] = value
            response = requests.request(method, f'{self.base_url}{endpoint}', headers=headers, data=data, params=query, files=files)
        else:
            headers["Content-Type"] = "application/json"
            response = requests.request(method, f'{self.base_url}{endpoint}', headers=headers, json=json, params=query)

        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} {response.text}")
        return response.json()

    def stream_request(self, method: str, endpoint: str, query: dict = None, json: dict = None, api_key: Optional[str] = None, files: list[tuple[str, io.BufferedReader]] = None):
        api_key = api_key or vectorshift.api_key or self.api_key
        headers = {
            "Authorization": f"Bearer {api_key}",
        }
        if files:
            data = {}
            for key, value in json.items():
                if isinstance(value, (dict, list) ):
                    data[key] = json_lib.dumps(value)
                else:
                    data[key] = value

            response = requests.request(method, f'{self.base_url}{endpoint}', headers=headers, data=data, params=query, files=files, stream=True)
        else:
            headers["Content-Type"] = "application/json"
            response = requests.request(method, f'{self.base_url}{endpoint}', headers=headers, json=json, params=query, stream=True)

        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} {response.text}")
        # Return a generator for streaming response
        for line in response.iter_lines():
            if line:
                yield line


class AsyncRequestClient:
    def __init__(self):
        self.api_key = os.environ.get('VECTORSHIFT_API_KEY')
        self.base_url = 'https://api.vectorshift.ai/v1'  # Match the sync client
        self._session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """Close the aiohttp session"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def arequest(self, method: str, endpoint: str, query: dict = None, json: dict = None, api_key: Optional[str] = None, files: list[tuple[str, io.BufferedReader]] = None):
        api_key = api_key or vectorshift.api_key or self.api_key
        headers = {
            "Authorization": f"Bearer {api_key}",
        }
        print("Async JSON: ", json)  # Match sync client debugging

        session = await self._get_session()
        url = f'{self.base_url}{endpoint}'

        try:
            if files:
                # Handle multipart form data for file uploads
                data = aiohttp.FormData()
                for key, value in (json or {}).items():
                    if isinstance(value, (dict, list)):
                        data.add_field(key, json_lib.dumps(value))
                    else:
                        data.add_field(key, str(value))
                
                for file_field, file_obj in files:
                    data.add_field(file_field, file_obj, filename=getattr(file_obj, 'name', 'file'))
                
                async with session.request(method, url, data=data, headers=headers, params=query) as response:
                    if response.status != 200:
                        text = await response.text()
                        raise Exception(f"Error: {response.status} {text}")
                    return await response.json()
            else:
                headers["Content-Type"] = "application/json"
                async with session.request(method, url, json=json, headers=headers, params=query) as response:
                    if response.status != 200:
                        text = await response.text()
                        raise Exception(f"Error: {response.status} {text}")
                    return await response.json()
        except Exception as e:
            # Re-raise the exception with context
            raise Exception(f"Request failed: {str(e)}")

    async def astream_request(self, method: str, endpoint: str, query: dict = None, json: dict = None, api_key: Optional[str] = None, files: list[tuple[str, io.BufferedReader]] = None) -> AsyncGenerator[bytes, None]:
        """Async streaming request"""
        api_key = api_key or vectorshift.api_key or self.api_key
        headers = {
            "Authorization": f"Bearer {api_key}",
        }

        session = await self._get_session()
        url = f'{self.base_url}{endpoint}'

        try:
            if files:
                # Handle multipart form data for file uploads
                data = aiohttp.FormData()
                for key, value in (json or {}).items():
                    if isinstance(value, (dict, list)):
                        data.add_field(key, json_lib.dumps(value))
                    else:
                        data.add_field(key, str(value))
                
                for file_field, file_obj in files:
                    data.add_field(file_field, file_obj, filename=getattr(file_obj, 'name', 'file'))
                
                async with session.request(method, url, data=data, headers=headers, params=query) as response:
                    if response.status != 200:
                        text = await response.text()
                        raise Exception(f"Error: {response.status} {text}")
                    
                    async for line in response.content:
                        yield line
            else:
                headers["Content-Type"] = "application/json"
                async with session.request(method, url, json=json, headers=headers, params=query) as response:
                    if response.status != 200:
                        text = await response.text()
                        raise Exception(f"Error: {response.status} {text}")
                    
                    async for line in response.content:
                        yield line
        except Exception as e:
            raise Exception(f"Streaming request failed: {str(e)}")


request_client = RequestClient()
async_request_client = AsyncRequestClient()
