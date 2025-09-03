"""
TokenRouter SDK Models
"""

from typing import Optional, List, Dict, Any, Union, Literal
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class Usage:
    """Token usage information"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Usage":
        return cls(
            prompt_tokens=data.get("prompt_tokens", 0),
            completion_tokens=data.get("completion_tokens", 0),
            total_tokens=data.get("total_tokens", 0),
        )


@dataclass
class ChatCompletionMessage:
    """Chat message"""
    role: Literal["system", "user", "assistant", "function", "tool"]
    content: Optional[str] = None
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = {"role": self.role}
        if self.content is not None:
            data["content"] = self.content
        if self.name is not None:
            data["name"] = self.name
        if self.function_call is not None:
            data["function_call"] = self.function_call
        if self.tool_calls is not None:
            data["tool_calls"] = self.tool_calls
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatCompletionMessage":
        return cls(
            role=data["role"],
            content=data.get("content"),
            name=data.get("name"),
            function_call=data.get("function_call"),
            tool_calls=data.get("tool_calls"),
        )


@dataclass
class ChatCompletionChoice:
    """Chat completion choice"""
    index: int
    message: ChatCompletionMessage
    finish_reason: Optional[str] = None
    logprobs: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatCompletionChoice":
        return cls(
            index=data.get("index", 0),
            message=ChatCompletionMessage.from_dict(data["message"]),
            finish_reason=data.get("finish_reason"),
            logprobs=data.get("logprobs"),
        )


@dataclass
class ChatCompletion:
    """Chat completion response"""
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Optional[Usage] = None
    system_fingerprint: Optional[str] = None
    cost_usd: Optional[float] = None
    latency_ms: Optional[float] = None
    routed_model: Optional[str] = None
    
    @property
    def content(self) -> Optional[str]:
        """Convenience property to get the first choice's content"""
        if self.choices and len(self.choices) > 0:
            return self.choices[0].message.content
        return None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatCompletion":
        return cls(
            id=data.get("id", ""),
            object=data.get("object", "chat.completion"),
            created=data.get("created", int(datetime.now().timestamp())),
            model=data.get("model", ""),
            choices=[ChatCompletionChoice.from_dict(c) for c in data.get("choices", [])],
            usage=Usage.from_dict(data["usage"]) if "usage" in data else None,
            system_fingerprint=data.get("system_fingerprint"),
            cost_usd=data.get("cost_usd"),
            latency_ms=data.get("latency_ms"),
            routed_model=data.get("routed_model"),
        )


@dataclass
class ChatCompletionChunk:
    """Streaming chat completion chunk"""
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Optional[Usage] = None
    system_fingerprint: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatCompletionChunk":
        return cls(
            id=data.get("id", ""),
            object=data.get("object", "chat.completion.chunk"),
            created=data.get("created", int(datetime.now().timestamp())),
            model=data.get("model", ""),
            choices=data.get("choices", []),
            usage=Usage.from_dict(data["usage"]) if "usage" in data else None,
            system_fingerprint=data.get("system_fingerprint"),
        )
    
    @classmethod
    def from_sse_data(cls, data: str) -> Optional["ChatCompletionChunk"]:
        """Parse SSE data into a chunk"""
        if data.strip() == "[DONE]":
            return None
        try:
            return cls.from_dict(json.loads(data))
        except json.JSONDecodeError:
            return None


@dataclass
class Model:
    """Model information"""
    id: str
    name: str
    provider: str
    capabilities: List[str] = field(default_factory=list)
    context_window: Optional[int] = None
    max_output_tokens: Optional[int] = None
    input_cost_per_1k: Optional[float] = None
    output_cost_per_1k: Optional[float] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Model":
        return cls(
            id=data["id"],
            name=data.get("name", data["id"]),
            provider=data.get("provider", "unknown"),
            capabilities=data.get("capabilities", []),
            context_window=data.get("context_window"),
            max_output_tokens=data.get("max_output_tokens"),
            input_cost_per_1k=data.get("input_cost_per_1k"),
            output_cost_per_1k=data.get("output_cost_per_1k"),
        )


@dataclass
class ModelCosts:
    """Model cost information"""
    model: str
    cost_per_1k_tokens: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelCosts":
        return cls(
            model=data["model"],
            cost_per_1k_tokens=data["cost_per_1k_tokens"],
        )


@dataclass
class Analytics:
    """Analytics information"""
    total_requests: int
    total_tokens: int
    total_cost_usd: float
    average_latency_ms: float
    model_distribution: Dict[str, int]
    error_rate: float
    cache_hit_rate: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Analytics":
        return cls(
            total_requests=data.get("total_requests", 0),
            total_tokens=data.get("total_tokens", 0),
            total_cost_usd=data.get("total_cost_usd", 0.0),
            average_latency_ms=data.get("average_latency_ms", 0.0),
            model_distribution=data.get("model_distribution", {}),
            error_rate=data.get("error_rate", 0.0),
            cache_hit_rate=data.get("cache_hit_rate", 0.0),
        )