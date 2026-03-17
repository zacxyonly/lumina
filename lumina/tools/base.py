"""Base tool class and tool registry."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import json


@dataclass
class ToolParameter:
    """Tool parameter definition."""
    name: str
    type: str  # string, number, boolean, array, object
    description: str
    required: bool = True
    enum: Optional[List[Any]] = None
    default: Optional[Any] = None


@dataclass
class ToolSpec:
    """Tool specification for LLM."""
    name: str
    description: str
    parameters: List[ToolParameter] = field(default_factory=list)
    
    def to_openai_format(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format."""
        properties = {}
        required = []
        
        for param in self.parameters:
            prop = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                prop["enum"] = param.enum
            if param.default is not None:
                prop["default"] = param.default
            
            properties[param.name] = prop
            if param.required:
                required.append(param.name)
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                }
            }
        }
    
    def to_anthropic_format(self) -> Dict[str, Any]:
        """Convert to Anthropic tool format."""
        properties = {}
        required = []
        
        for param in self.parameters:
            prop = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                prop["enum"] = param.enum
            
            properties[param.name] = prop
            if param.required:
                required.append(param.name)
        
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            }
        }


class Tool(ABC):
    """Base class for all tools."""
    
    name: str = "base_tool"
    description: str = "Base tool class"
    parameters: List[ToolParameter] = []
    
    def __init__(self):
        self.spec = ToolSpec(
            name=self.name,
            description=self.description,
            parameters=self.parameters
        )
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters.
        
        Returns:
            Dict with 'status' and 'result' keys
        """
        pass
    
    def validate_params(self, **kwargs) -> bool:
        """Validate input parameters."""
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                raise ValueError(f"Missing required parameter: {param.name}")
        return True
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Run the tool with validation."""
        self.validate_params(**kwargs)
        return await self.execute(**kwargs)


class ToolRegistry:
    """Registry for managing available tools."""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        """Register a tool."""
        self.tools[tool.name] = tool
    
    def unregister(self, name: str) -> None:
        """Unregister a tool."""
        if name in self.tools:
            del self.tools[name]
    
    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self.tools.keys())
    
    def get_specs(self, format: str = "openai") -> List[Dict[str, Any]]:
        """Get tool specifications for LLM."""
        if format == "openai":
            return [tool.spec.to_openai_format() for tool in self.tools.values()]
        elif format == "anthropic":
            return [tool.spec.to_anthropic_format() for tool in self.tools.values()]
        else:
            raise ValueError(f"Unknown format: {format}")
    
    async def execute(self, name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name."""
        tool = self.get(name)
        if not tool:
            return {
                "status": "error",
                "error": f"Tool not found: {name}"
            }
        
        try:
            return await tool.run(**kwargs)
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
