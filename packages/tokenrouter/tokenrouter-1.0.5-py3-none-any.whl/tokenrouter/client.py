"""
TokenRouter SDK Client
"""

import os
import time
import json as jsonlib
import asyncio
from typing import Optional, Dict, Any, List, Union, AsyncIterator, Iterator
from urllib.parse import urljoin
import httpx
from httpx import Response, HTTPStatusError
from typing import TypedDict

from .models import (
    ChatCompletion,
    ChatCompletionMessage,
    ChatCompletionChunk,
)
from .exceptions import (
    TokenRouterError,
    AuthenticationError,
    RateLimitError,
    InvalidRequestError,
    APIConnectionError,
    APIStatusError,
    TimeoutError,
    QuotaExceededError,
)


class TextCompletionChoice(TypedDict, total=False):
    text: str
    index: int
    logprobs: Optional[Dict[str, Any]]
    finish_reason: Optional[str]


class TextCompletion(TypedDict, total=False):
    id: str
    object: str
    created: int
    model: str
    choices: List[TextCompletionChoice]
    usage: Optional[Dict[str, int]]


class BaseClient:
    """Base client with common functionality"""

    DEFAULT_BASE_URL = "https://api.tokenrouter.io"
    DEFAULT_TIMEOUT = 60.0
    DEFAULT_MAX_RETRIES = 3

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.api_key = api_key or os.environ.get("TOKENROUTER_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Set TOKENROUTER_API_KEY environment variable or pass api_key parameter."
            )

        self.base_url = (base_url or os.environ.get("TOKENROUTER_BASE_URL", self.DEFAULT_BASE_URL)).rstrip("/")
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.max_retries = max_retries or self.DEFAULT_MAX_RETRIES

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "tokenrouter-python/1.0.5",
        }
        if headers:
            self.headers.update(headers)

    def _handle_response_error(self, response: Response) -> None:
        """Handle HTTP response errors"""
        try:
            error_data = response.json()
            message = error_data.get("detail", response.text)
        except Exception:
            message = response.text or f"HTTP {response.status_code}"

        if response.status_code == 401:
            raise AuthenticationError(message, response.status_code)
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                message,
                response.status_code,
                headers=dict(response.headers),
                retry_after=int(retry_after) if retry_after else None,
            )
        elif response.status_code == 400:
            raise InvalidRequestError(message, response.status_code)
        elif response.status_code == 403:
            if "quota" in message.lower():
                raise QuotaExceededError(message, response.status_code)
            raise AuthenticationError(message, response.status_code)
        elif response.status_code >= 500:
            raise APIStatusError(message, response.status_code)
        else:
            raise TokenRouterError(message, response.status_code)


class ChatCompletions:
    """Chat completions interface (/v1/chat/completions)"""

    def __init__(self, client: "TokenRouter"):
        self.client = client

    def create(
        self,
        messages: List[Union[Dict[str, Any], ChatCompletionMessage]],
        model: str = "auto",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False,
        n: Optional[int] = None,
        logprobs: Optional[bool] = None,
        echo: Optional[bool] = None,
        user: Optional[str] = None,
        model_preferences: Optional[List[str]] = None,
        mode: Optional[str] = None,  # cost | quality | latency | balanced
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        response_format: Optional[Dict[str, Any]] = None,
        seed: Optional[int] = None,
        **kwargs,
    ) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]:

        messages_dict: List[Dict[str, Any]] = []
        for msg in messages:
            if isinstance(msg, ChatCompletionMessage):
                messages_dict.append(msg.to_dict())
            else:
                messages_dict.append(msg)

        payload: Dict[str, Any] = {
            "messages": messages_dict,
            "model": model,
            "stream": stream,
        }

        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if top_p is not None:
            payload["top_p"] = top_p
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if stop is not None:
            payload["stop"] = stop
        if n is not None:
            payload["n"] = n
        if logprobs is not None:
            payload["logprobs"] = logprobs
        if echo is not None:
            payload["echo"] = echo
        if user is not None:
            payload["user"] = user
        if model_preferences is not None:
            payload["model_preferences"] = model_preferences
        if mode is not None:
            payload["mode"] = mode
        if tools is not None:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        if response_format is not None:
            payload["response_format"] = response_format
        if seed is not None:
            payload["seed"] = seed

        payload.update(kwargs)

        if stream:
            return self.client._stream_request("/v1/chat/completions", payload)
        response = self.client._request("POST", "/v1/chat/completions", json=payload)
        return ChatCompletion.from_dict(response)


class LegacyCompletions:
    """OpenAI legacy completions interface (/v1/completions)"""

    def __init__(self, client: "TokenRouter"):
        self.client = client

    def create(
        self,
        prompt: Union[str, List[Union[str, int, List[int]]]],
        model: str = "auto",
        mode: Optional[str] = None,
        model_preferences: Optional[List[str]] = None,
        stream: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        user: Optional[str] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        **kwargs,
    ) -> Union[TextCompletion, Iterator[Dict[str, Any]]]:
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
        }
        if mode is not None:
            payload["mode"] = mode
        if model_preferences is not None:
            payload["model_preferences"] = model_preferences
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if user is not None:
            payload["user"] = user
        if top_p is not None:
            payload["top_p"] = top_p
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if stop is not None:
            payload["stop"] = stop
        payload.update(kwargs)

        if stream:
            return self.client._stream_request_raw("/v1/completions", payload)
        return self.client._request("POST", "/v1/completions", json=payload)


class ChatNamespace:
    """Namespace for chat APIs, matching OpenAI style: client.chat.completions.create"""

    def __init__(self, client: "TokenRouter"):
        self.completions = ChatCompletions(client)


class TokenRouter(BaseClient):
    """Synchronous TokenRouter client"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = httpx.Client(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
        )
        # Namespaced routes matching OpenAI style
        self.chat = ChatNamespace(self)
        self.completions = LegacyCompletions(self)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self) -> None:
        self.client.close()

    # Native TokenRouter endpoint: /route
    def create(
        self,
        messages: List[Union[Dict[str, Any], ChatCompletionMessage]],
        model: str = "auto",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False,
        user: Optional[str] = None,
        model_preferences: Optional[List[str]] = None,
        mode: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]:
        messages_dict: List[Dict[str, Any]] = []
        for msg in messages:
            if isinstance(msg, ChatCompletionMessage):
                messages_dict.append(msg.to_dict())
            else:
                messages_dict.append(msg)

        payload: Dict[str, Any] = {
            "messages": messages_dict,
            "model": model,
            "stream": stream,
        }
        if temperature is not None:
            payload["temperature"] = temperature
        if max_completion_tokens is not None:
            payload["max_completion_tokens"] = max_completion_tokens
        elif max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if top_p is not None:
            payload["top_p"] = top_p
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if stop is not None:
            payload["stop"] = stop
        if user is not None:
            payload["user"] = user
        if model_preferences is not None:
            payload["model_preferences"] = model_preferences
        if mode is not None:
            payload["mode"] = mode
        if tools is not None:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        if response_format is not None:
            payload["response_format"] = response_format
        payload.update(kwargs)

        if stream:
            return self._stream_request("/route", payload)
        response = self._request("POST", "/route", json=payload)
        return ChatCompletion.from_dict(response)

    def _request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> Dict[str, Any]:
        url = urljoin(self.base_url, path)
        try:
            response = self.client.request(method, url, json=json, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {e}")
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Connection failed: {e}")
        except HTTPStatusError as e:
            if retry_count < self.max_retries and e.response.status_code >= 500:
                time.sleep(2 ** retry_count)
                return self._request(method, path, json, params, retry_count + 1)
            self._handle_response_error(e.response)
        except Exception as e:
            raise TokenRouterError(f"Unexpected error: {e}")

    def _stream_request(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
    ) -> Iterator[ChatCompletionChunk]:
        url = urljoin(self.base_url, path)
        with self.client.stream("POST", url, json=json) as response:
            try:
                response.raise_for_status()
            except HTTPStatusError:
                self._handle_response_error(response)
            for line in response.iter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    chunk = ChatCompletionChunk.from_sse_data(data)
                    if chunk:
                        yield chunk

    def _stream_request_raw(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
    ) -> Iterator[Dict[str, Any]]:
        url = urljoin(self.base_url, path)
        with self.client.stream("POST", url, json=json) as response:
            try:
                response.raise_for_status()
            except HTTPStatusError:
                self._handle_response_error(response)
            for line in response.iter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        yield jsonlib.loads(data)
                    except Exception:
                        continue

    # Strict to Request_1: no additional utility endpoints


class AsyncChatCompletions:
    def __init__(self, client: "AsyncTokenRouter"):
        self.client = client

    async def create(
        self,
        messages: List[Union[Dict[str, Any], ChatCompletionMessage]],
        model: str = "auto",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False,
        n: Optional[int] = None,
        logprobs: Optional[bool] = None,
        echo: Optional[bool] = None,
        user: Optional[str] = None,
        model_preferences: Optional[List[str]] = None,
        mode: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        response_format: Optional[Dict[str, Any]] = None,
        seed: Optional[int] = None,
        **kwargs,
    ) -> Union[ChatCompletion, AsyncIterator[ChatCompletionChunk]]:
        messages_dict: List[Dict[str, Any]] = []
        for msg in messages:
            if isinstance(msg, ChatCompletionMessage):
                messages_dict.append(msg.to_dict())
            else:
                messages_dict.append(msg)

        payload: Dict[str, Any] = {
            "messages": messages_dict,
            "model": model,
            "stream": stream,
        }
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if top_p is not None:
            payload["top_p"] = top_p
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if stop is not None:
            payload["stop"] = stop
        if n is not None:
            payload["n"] = n
        if logprobs is not None:
            payload["logprobs"] = logprobs
        if echo is not None:
            payload["echo"] = echo
        if user is not None:
            payload["user"] = user
        if model_preferences is not None:
            payload["model_preferences"] = model_preferences
        if mode is not None:
            payload["mode"] = mode
        if tools is not None:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        if response_format is not None:
            payload["response_format"] = response_format
        if seed is not None:
            payload["seed"] = seed
        payload.update(kwargs)

        if stream:
            return self.client._stream_request("/v1/chat/completions", payload)
        response = await self.client._request("POST", "/v1/chat/completions", json=payload)
        return ChatCompletion.from_dict(response)


class AsyncLegacyCompletions:
    def __init__(self, client: "AsyncTokenRouter"):
        self.client = client

    async def create(
        self,
        prompt: Union[str, List[Union[str, int, List[int]]]],
        model: str = "auto",
        mode: Optional[str] = None,
        model_preferences: Optional[List[str]] = None,
        stream: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        user: Optional[str] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        **kwargs,
    ) -> Union[TextCompletion, AsyncIterator[Dict[str, Any]]]:
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
        }
        if mode is not None:
            payload["mode"] = mode
        if model_preferences is not None:
            payload["model_preferences"] = model_preferences
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if user is not None:
            payload["user"] = user
        if top_p is not None:
            payload["top_p"] = top_p
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if stop is not None:
            payload["stop"] = stop
        payload.update(kwargs)

        if stream:
            return self.client._stream_request_raw("/v1/completions", payload)
        return await self.client._request("POST", "/v1/completions", json=payload)


class AsyncChatNamespace:
    """Namespace for async chat APIs, matching OpenAI style: client.chat.completions.create"""

    def __init__(self, client: "AsyncTokenRouter"):
        self.completions = AsyncChatCompletions(client)


class AsyncTokenRouter(BaseClient):
    """Asynchronous TokenRouter client"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
        )
        self.chat = AsyncChatNamespace(self)
        self.completions = AsyncLegacyCompletions(self)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def close(self) -> None:
        await self.client.aclose()

    # Native TokenRouter endpoint: /route (async)
    async def create(
        self,
        messages: List[Union[Dict[str, Any], ChatCompletionMessage]],
        model: str = "auto",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False,
        user: Optional[str] = None,
        model_preferences: Optional[List[str]] = None,
        mode: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Union[ChatCompletion, AsyncIterator[ChatCompletionChunk]]:
        messages_dict: List[Dict[str, Any]] = []
        for msg in messages:
            if isinstance(msg, ChatCompletionMessage):
                messages_dict.append(msg.to_dict())
            else:
                messages_dict.append(msg)

        payload: Dict[str, Any] = {
            "messages": messages_dict,
            "model": model,
            "stream": stream,
        }
        if temperature is not None:
            payload["temperature"] = temperature
        if max_completion_tokens is not None:
            payload["max_completion_tokens"] = max_completion_tokens
        elif max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if top_p is not None:
            payload["top_p"] = top_p
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if stop is not None:
            payload["stop"] = stop
        if user is not None:
            payload["user"] = user
        if model_preferences is not None:
            payload["model_preferences"] = model_preferences
        if mode is not None:
            payload["mode"] = mode
        if tools is not None:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        if response_format is not None:
            payload["response_format"] = response_format
        payload.update(kwargs)

        if stream:
            return self._stream_request("/route", payload)
        response = await self._request("POST", "/route", json=payload)
        return ChatCompletion.from_dict(response)

    async def _request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> Dict[str, Any]:
        url = urljoin(self.base_url, path)
        try:
            response = await self.client.request(method, url, json=json, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {e}")
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Connection failed: {e}")
        except HTTPStatusError as e:
            if retry_count < self.max_retries and e.response.status_code >= 500:
                await asyncio.sleep(2 ** retry_count)
                return await self._request(method, path, json, params, retry_count + 1)
            self._handle_response_error(e.response)
        except Exception as e:
            raise TokenRouterError(f"Unexpected error: {e}")

    async def _stream_request(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[ChatCompletionChunk]:
        url = urljoin(self.base_url, path)
        async with self.client.stream("POST", url, json=json) as response:
            try:
                response.raise_for_status()
            except HTTPStatusError:
                self._handle_response_error(response)
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    chunk = ChatCompletionChunk.from_sse_data(data)
                    if chunk:
                        yield chunk

    async def _stream_request_raw(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        url = urljoin(self.base_url, path)
        async with self.client.stream("POST", url, json=json) as response:
            try:
                response.raise_for_status()
            except HTTPStatusError:
                self._handle_response_error(response)
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        yield jsonlib.loads(data)
                    except Exception:
                        continue
