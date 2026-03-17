"""LLM provider abstraction layer."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from dataclasses import dataclass
import asyncio


@dataclass
class Message:
    """Chat message structure."""
    role: str  # system, user, assistant, tool
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


@dataclass
class LLMResponse:
    """LLM response structure."""
    content: str
    role: str = "assistant"
    tool_calls: Optional[List[Dict[str, Any]]] = None
    finish_reason: str = "stop"
    usage: Optional[Dict[str, int]] = None


class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.kwargs = kwargs
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> LLMResponse:
        """Send chat completion request."""
        pass
    
    @abstractmethod
    async def stream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream chat completion."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI provider implementation."""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview", **kwargs):
        super().__init__(api_key, model, **kwargs)
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("openai package required: pip install openai")
    
    async def chat(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> LLMResponse:
        """Send chat completion request to OpenAI."""
        msg_dicts = [{"role": m.role, "content": m.content} for m in messages]
        
        params = {
            "model": self.model,
            "messages": msg_dicts,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
        
        response = await self.client.chat.completions.create(**params)
        choice = response.choices[0]
        
        tool_calls = None
        if choice.message.tool_calls:
            tool_calls = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in choice.message.tool_calls
            ]
        
        return LLMResponse(
            content=choice.message.content or "",
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        )
    
    async def stream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream chat completion from OpenAI."""
        msg_dicts = [{"role": m.role, "content": m.content} for m in messages]
        
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=msg_dicts,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider implementation."""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", **kwargs):
        super().__init__(api_key, model, **kwargs)
        try:
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=api_key)
        except ImportError:
            raise ImportError("anthropic package required: pip install anthropic")
    
    async def chat(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> LLMResponse:
        """Send chat completion request to Anthropic."""
        # Separate system message
        system_msg = None
        msg_list = []
        
        for m in messages:
            if m.role == "system":
                system_msg = m.content
            else:
                msg_list.append({"role": m.role, "content": m.content})
        
        params = {
            "model": self.model,
            "messages": msg_list,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        if system_msg:
            params["system"] = system_msg
        
        if tools:
            params["tools"] = tools
        
        response = await self.client.messages.create(**params)
        
        content = ""
        tool_calls = None
        
        for block in response.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                if tool_calls is None:
                    tool_calls = []
                tool_calls.append({
                    "id": block.id,
                    "type": "function",
                    "function": {
                        "name": block.name,
                        "arguments": str(block.input)
                    }
                })
        
        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=response.stop_reason,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            }
        )
    
    async def stream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream chat completion from Anthropic."""
        system_msg = None
        msg_list = []
        
        for m in messages:
            if m.role == "system":
                system_msg = m.content
            else:
                msg_list.append({"role": m.role, "content": m.content})
        
        params = {
            "model": self.model,
            "messages": msg_list,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        if system_msg:
            params["system"] = system_msg
        
        async with self.client.messages.stream(**params) as stream:
            async for text in stream.text_stream:
                yield text


def create_provider(provider: str, api_key: str, model: str, **kwargs) -> LLMProvider:
    """Factory function to create LLM provider."""
    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
    }
    
    provider_class = providers.get(provider.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(providers.keys())}")
    
    return provider_class(api_key=api_key, model=model, **kwargs)
