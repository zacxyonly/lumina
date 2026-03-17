"""LiteLLM provider integration for unified multi-LLM access."""

from typing import List, Dict, Any, Optional, AsyncIterator
from dataclasses import dataclass
import asyncio

from lumina.core.llm import LLMProvider, Message, LLMResponse


class LiteLLMProvider(LLMProvider):
    """LiteLLM provider for unified multi-LLM access.
    
    Supports: OpenAI, Anthropic, Google, Groq, Cohere, Replicate, etc.
    """
    
    def __init__(self, api_key: str, model: str, **kwargs):
        super().__init__(api_key, model, **kwargs)
        try:
            import litellm
            self.litellm = litellm
            
            # Set API key based on provider
            self._set_api_keys(api_key, model)
        except ImportError:
            raise ImportError(
                "litellm package required: pip install litellm\n"
                "Install with: pip install -U litellm"
            )
    
    def _set_api_keys(self, api_key: str, model: str):
        """Set API keys for the provider based on model."""
        import os
        
        # Extract provider from model name
        if model.startswith("gpt-"):
            os.environ["OPENAI_API_KEY"] = api_key
        elif model.startswith("claude-"):
            os.environ["ANTHROPIC_API_KEY"] = api_key
        elif model.startswith("gemini"):
            os.environ["GOOGLE_API_KEY"] = api_key
        elif "groq" in model.lower() or model in ["mixtral-8x7b-32768", "llama2-70b-4096"]:
            os.environ["GROQ_API_KEY"] = api_key
        elif model.startswith("command"):
            os.environ["COHERE_API_KEY"] = api_key
        else:
            # For unknown providers, try to set a generic API key
            os.environ["LITELLM_API_KEY"] = api_key
    
    async def chat(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> LLMResponse:
        """Send chat completion request using LiteLLM."""
        msg_dicts = []
        
        for m in messages:
            msg_dict = {"role": m.role, "content": m.content}
            msg_dicts.append(msg_dict)
        
        params = {
            "model": self.model,
            "messages": msg_dicts,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        # Add tools if provided
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
        
        try:
            # Use run_without_streaming for sync-like behavior in async context
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.litellm.completion(**params)
            )
            
            choice = response.choices[0]
            
            # Parse tool calls
            tool_calls = None
            if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
                tool_calls = [
                    {
                        "id": tc.id if hasattr(tc, 'id') else f"call_{idx}",
                        "type": tc.type if hasattr(tc, 'type') else "function",
                        "function": {
                            "name": tc.function.name if hasattr(tc.function, 'name') else tc.function,
                            "arguments": tc.function.arguments if hasattr(tc.function, 'arguments') else "{}"
                        }
                    }
                    for idx, tc in enumerate(choice.message.tool_calls)
                ]
            
            # Parse usage
            usage = None
            if hasattr(response, 'usage'):
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens if hasattr(response.usage, 'prompt_tokens') else 0,
                    "completion_tokens": response.usage.completion_tokens if hasattr(response.usage, 'completion_tokens') else 0,
                    "total_tokens": response.usage.total_tokens if hasattr(response.usage, 'total_tokens') else 0,
                }
            
            return LLMResponse(
                content=choice.message.content or "",
                tool_calls=tool_calls,
                finish_reason=choice.finish_reason if hasattr(choice, 'finish_reason') else "stop",
                usage=usage
            )
        
        except Exception as e:
            raise RuntimeError(f"LiteLLM API error: {str(e)}")
    
    async def stream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream chat completion using LiteLLM."""
        msg_dicts = []
        
        for m in messages:
            msg_dict = {"role": m.role, "content": m.content}
            msg_dicts.append(msg_dict)
        
        params = {
            "model": self.model,
            "messages": msg_dicts,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
            **kwargs
        }
        
        try:
            loop = asyncio.get_event_loop()
            stream = await loop.run_in_executor(
                None,
                lambda: self.litellm.completion(**params)
            )
            
            for chunk in stream:
                if hasattr(chunk.choices[0], 'delta'):
                    if hasattr(chunk.choices[0].delta, 'content'):
                        content = chunk.choices[0].delta.content
                        if content:
                            yield content
        
        except Exception as e:
            raise RuntimeError(f"LiteLLM streaming error: {str(e)}")


def get_provider_factory(use_litellm: bool = False):
    """Get provider factory function.
    
    Args:
        use_litellm: If True, use LiteLLM for all providers.
                    If False, use native providers for OpenAI/Anthropic.
    
    Returns:
        Factory function that creates provider instances.
    """
    if use_litellm:
        def factory(provider: str, api_key: str, model: str, **kwargs) -> LLMProvider:
            return LiteLLMProvider(api_key=api_key, model=model, **kwargs)
        return factory
    else:
        # Use default factory with native providers
        from lumina.core.llm import create_provider
        return create_provider
