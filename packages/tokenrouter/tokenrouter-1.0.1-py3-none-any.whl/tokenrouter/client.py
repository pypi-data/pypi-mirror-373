"""
TokenRouter SDK Client
"""

import os
import time
import json
import asyncio
from typing import Optional, Dict, Any, List, Union, AsyncIterator, Iterator
from urllib.parse import urljoin
import httpx
from httpx import Response, HTTPStatusError

from .models import (
    ChatCompletion,
    ChatCompletionMessage,
    ChatCompletionChunk,
    Model,
    ModelCosts,
    Analytics,
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


class BaseClient:
    """Base client with common functionality"""
    
    DEFAULT_BASE_URL = "http://localhost:8000"
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
            raise AuthenticationError("API key is required. Set TOKENROUTER_API_KEY environment variable or pass api_key parameter.")
        
        self.base_url = (base_url or os.environ.get("TOKENROUTER_BASE_URL", self.DEFAULT_BASE_URL)).rstrip("/")
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.max_retries = max_retries or self.DEFAULT_MAX_RETRIES
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "tokenrouter-python/1.0.0",
        }
        if headers:
            self.headers.update(headers)
    
    def _handle_response_error(self, response: Response) -> None:
        """Handle HTTP response errors"""
        try:
            error_data = response.json()
            message = error_data.get("detail", response.text)
        except:
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
    """Chat completions interface"""
    
    def __init__(self, client: "Client"):
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
        mode: Optional[str] = None,  # 'cost', 'quality', 'latency', or 'balanced'
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        response_format: Optional[Dict[str, Any]] = None,
        seed: Optional[int] = None,
        **kwargs,
    ) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]:
        """Create a chat completion"""
        
        # Convert messages to dicts if needed
        messages_dict = []
        for msg in messages:
            if isinstance(msg, ChatCompletionMessage):
                messages_dict.append(msg.to_dict())
            else:
                messages_dict.append(msg)
        
        # Build request payload
        payload = {
            "messages": messages_dict,
            "model": model,
            "stream": stream,
        }
        
        # Add optional parameters
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
        
        # Add any extra kwargs
        payload.update(kwargs)
        
        if stream:
            return self.client._stream_request("/v1/chat/completions", payload)
        else:
            response = self.client._request("POST", "/v1/chat/completions", json=payload)
            return ChatCompletion.from_dict(response)


class AsyncChatCompletions:
    """Async chat completions interface"""
    
    def __init__(self, client: "AsyncClient"):
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
        mode: Optional[str] = None,  # 'cost', 'quality', 'latency', or 'balanced'
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        response_format: Optional[Dict[str, Any]] = None,
        seed: Optional[int] = None,
        **kwargs,
    ) -> Union[ChatCompletion, AsyncIterator[ChatCompletionChunk]]:
        """Create a chat completion asynchronously"""
        
        # Convert messages to dicts if needed
        messages_dict = []
        for msg in messages:
            if isinstance(msg, ChatCompletionMessage):
                messages_dict.append(msg.to_dict())
            else:
                messages_dict.append(msg)
        
        # Build request payload
        payload = {
            "messages": messages_dict,
            "model": model,
            "stream": stream,
        }
        
        # Add optional parameters
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
        
        # Add any extra kwargs
        payload.update(kwargs)
        
        if stream:
            return self.client._stream_request("/v1/chat/completions", payload)
        else:
            response = await self.client._request("POST", "/v1/chat/completions", json=payload)
            return ChatCompletion.from_dict(response)


class TokenRouter(BaseClient):
    """Synchronous TokenRouter client"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = httpx.Client(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
        )
        self.chat = ChatCompletions(self)
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
    
    def close(self):
        """Close the client"""
        self.client.close()
    
    def _request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> Dict[str, Any]:
        """Make a synchronous HTTP request"""
        
        url = urljoin(self.base_url, path)
        
        try:
            response = self.client.request(
                method,
                url,
                json=json,
                params=params,
            )
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
        """Make a streaming request"""
        
        url = urljoin(self.base_url, path)
        
        with self.client.stream(
            "POST",
            url,
            json=json,
        ) as response:
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
    
    def completions(
        self,
        prompt: str,
        model: str = "auto",
        **kwargs,
    ) -> ChatCompletion:
        """Simple completion interface (converts to chat format)"""
        messages = [{"role": "user", "content": prompt}]
        return self.chat.create(messages, model=model, **kwargs)
    
    def list_models(self) -> List[Model]:
        """List available models"""
        response = self._request("GET", "/v1/models")
        if "data" in response:
            # OpenAI format response
            return [Model.from_dict({
                "id": m["id"],
                "name": m.get("id"),
                "provider": m.get("owned_by", "unknown"),
                "capabilities": [],
                "context_window": None,
                "max_output_tokens": None
            }) for m in response.get("data", [])]
        else:
            # Legacy format
            return [Model.from_dict(m) for m in response.get("models", [])]
    
    def get_costs(self) -> Dict[str, float]:
        """Get model costs"""
        return self._request("GET", "/costs")
    
    def get_analytics(self) -> Analytics:
        """Get usage analytics"""
        response = self._request("GET", "/analytics")
        return Analytics.from_dict(response)
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        return self._request("GET", "/health")


class AsyncTokenRouter(BaseClient):
    """Asynchronous TokenRouter client"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
        )
        self.chat = AsyncChatCompletions(self)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        await self.close()
    
    async def close(self):
        """Close the client"""
        await self.client.aclose()
    
    async def _request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> Dict[str, Any]:
        """Make an asynchronous HTTP request"""
        
        url = urljoin(self.base_url, path)
        
        try:
            response = await self.client.request(
                method,
                url,
                json=json,
                params=params,
            )
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
        """Make a streaming request"""
        
        url = urljoin(self.base_url, path)
        
        async with self.client.stream(
            "POST",
            url,
            json=json,
        ) as response:
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
    
    async def completions(
        self,
        prompt: str,
        model: str = "auto",
        **kwargs,
    ) -> ChatCompletion:
        """Simple completion interface (converts to chat format)"""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat.create(messages, model=model, **kwargs)
    
    async def list_models(self) -> List[Model]:
        """List available models"""
        response = await self._request("GET", "/v1/models")
        if "data" in response:
            # OpenAI format response
            return [Model.from_dict({
                "id": m["id"],
                "name": m.get("id"),
                "provider": m.get("owned_by", "unknown"),
                "capabilities": [],
                "context_window": None,
                "max_output_tokens": None
            }) for m in response.get("data", [])]
        else:
            # Legacy format
            return [Model.from_dict(m) for m in response.get("models", [])]
    
    async def get_costs(self) -> Dict[str, float]:
        """Get model costs"""
        return await self._request("GET", "/costs")
    
    async def get_analytics(self) -> Analytics:
        """Get usage analytics"""
        response = await self._request("GET", "/analytics")
        return Analytics.from_dict(response)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        return await self._request("GET", "/health")