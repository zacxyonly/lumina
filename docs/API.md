# Lumina API Documentation

Complete API reference for Lumina v1.0.0.

## Table of Contents

- [Core Agent](#core-agent)
- [LLM Providers](#llm-providers)
- [Tool System](#tool-system)
- [Memory System](#memory-system)
- [Configuration](#configuration)
- [Utilities](#utilities)

---

## Core Agent

### `Lumina`

Main agent class for autonomous task execution.

```python
from lumina import Lumina

agent = Lumina(
    config: Optional[LuminaConfig] = None,
    tools: Optional[List[Tool]] = None,
    enable_memory: bool = True
)
```

#### Parameters
- `config` (LuminaConfig, optional): Configuration object. Uses global config if None.
- `tools` (List[Tool], optional): Custom tools to register with the agent.
- `enable_memory` (bool): Whether to enable the memory system. Default: True.

#### Methods

##### `async run(task: str, context: Optional[str] = None, max_iterations: Optional[int] = None) -> str`

Execute a task autonomously.

```python
result = await agent.run(
    task="Create a TODO list",
    context="Focus on work priorities",
    max_iterations=15
)
```

**Parameters:**
- `task` (str): Task description
- `context` (str, optional): Additional context
- `max_iterations` (int, optional): Maximum iterations (uses config default if None)

**Returns:** Final response as string

##### `async chat(message: str) -> str`

Simple chat without tools.

```python
response = await agent.chat("Hello, how are you?")
```

**Parameters:**
- `message` (str): User message

**Returns:** Assistant response as string

##### `reset() -> None`

Reset agent state (clears messages, resets iteration count).

```python
agent.reset()
```

---

## LLM Providers

### `LLMProvider`

Base class for LLM providers.

```python
from lumina.core.llm import LLMProvider, Message, LLMResponse
```

### `create_provider(provider: str, api_key: str, model: str, **kwargs) -> LLMProvider`

Factory function to create LLM provider instances.

```python
from lumina.core.llm import create_provider

llm = create_provider(
    provider="openai",
    api_key="sk-...",
    model="gpt-4-turbo-preview"
)
```

**Supported Providers:**
- `openai`: OpenAI GPT models
- `anthropic`: Anthropic Claude models

### `Message`

Chat message structure.

```python
from lumina.core.llm import Message

msg = Message(
    role="user",  # system, user, assistant, tool
    content="Hello",
    name=None,
    tool_calls=None,
    tool_call_id=None
)
```

### `LLMResponse`

LLM response structure.

```python
response = LLMResponse(
    content="Response text",
    role="assistant",
    tool_calls=None,
    finish_reason="stop",
    usage={"prompt_tokens": 10, "completion_tokens": 20}
)
```

### Provider Methods

##### `async chat(messages: List[Message], temperature: float = 0.7, max_tokens: int = 4000, tools: Optional[List[Dict]] = None) -> LLMResponse`

Send chat completion request.

##### `async stream(messages: List[Message], temperature: float = 0.7, max_tokens: int = 4000) -> AsyncIterator[str]`

Stream chat completion.

---

## Tool System

### `Tool`

Base class for creating custom tools.

```python
from lumina.tools import Tool, ToolParameter

class MyTool(Tool):
    name = "my_tool"
    description = "What the tool does"
    parameters = [
        ToolParameter(
            name="param1",
            type="string",
            description="Parameter description",
            required=True
        )
    ]
    
    async def execute(self, param1: str, **kwargs):
        return {"status": "success", "result": "data"}
```

#### Required Attributes
- `name` (str): Tool identifier
- `description` (str): Tool description for LLM
- `parameters` (List[ToolParameter]): Tool parameters

#### Methods

##### `async execute(**kwargs) -> Dict[str, Any]`

Execute tool logic. Must return dict with `status` key.

##### `async run(**kwargs) -> Dict[str, Any]`

Run tool with parameter validation.

### `ToolParameter`

Tool parameter definition.

```python
param = ToolParameter(
    name="input",
    type="string",  # string, number, boolean, array, object
    description="Parameter description",
    required=True,
    enum=None,  # Optional: ["option1", "option2"]
    default=None
)
```

### `ToolRegistry`

Tool management system.

```python
from lumina.tools import ToolRegistry

registry = ToolRegistry()

# Register tool
registry.register(MyTool())

# Get tool
tool = registry.get("my_tool")

# Execute tool
result = await registry.execute("my_tool", param1="value")

# List tools
tools = registry.list_tools()

# Get tool specs for LLM
specs = registry.get_specs(format="openai")  # or "anthropic"
```

### Built-in Tools

#### File Tools

```python
from lumina.tools.file import (
    ReadFileTool,
    WriteFileTool,
    ListDirectoryTool,
    SearchFilesTool
)
```

**ReadFileTool**
```python
result = await tool.run(path="file.txt")
```

**WriteFileTool**
```python
result = await tool.run(
    path="file.txt",
    content="Hello",
    mode="write"  # or "append"
)
```

**ListDirectoryTool**
```python
result = await tool.run(
    path="/path/to/dir",
    recursive=False
)
```

**SearchFilesTool**
```python
result = await tool.run(
    path="/path",
    pattern="*.py"
)
```

---

## Memory System

### `Memory`

Memory management for agents.

```python
from lumina.core.memory import Memory

memory = Memory(
    memory_dir=Path("./memory"),
    max_short_term=20
)
```

#### Methods

##### `add_short_term(content: str, type: str = "conversation", **metadata) -> None`

Add to short-term memory.

```python
memory.add_short_term(
    "User likes Python",
    type="conversation",
    role="user"
)
```

##### `add_working(content: str, **metadata) -> None`

Add to working memory (current task).

```python
memory.add_working(
    "Analyzing file structure",
    task_id="task_123"
)
```

##### `clear_working() -> None`

Clear working memory.

##### `add_fact(fact: str, category: str = "general") -> None`

Add fact to long-term memory.

```python
memory.add_fact(
    "User's favorite color is blue",
    category="preferences"
)
```

##### `add_learning(learning: str, context: str = "") -> None`

Add learning to long-term memory.

```python
memory.add_learning(
    "User prefers detailed explanations",
    context="Communication style"
)
```

##### `set_preference(key: str, value: Any) -> None`

Set user preference.

```python
memory.set_preference("language", "python")
```

##### `get_preference(key: str, default: Any = None) -> Any`

Get user preference.

```python
lang = memory.get_preference("language", "english")
```

##### `get_relevant_context(query: str, max_results: int = 5) -> List[str]`

Get relevant context for a query.

```python
context = memory.get_relevant_context("Python code")
```

##### `cleanup_old_memories(days: int = 30) -> None`

Remove memories older than specified days.

---

## Configuration

### `LuminaConfig`

Configuration dataclass.

```python
from lumina.utils.config import LuminaConfig

config = LuminaConfig(
    provider="openai",
    model="gpt-4-turbo-preview",
    temperature=0.7,
    max_tokens=4000,
    max_iterations=10,
    verbose=True,
    debug=False,
    enable_memory=True
)
```

#### Class Methods

##### `from_env() -> LuminaConfig`

Load configuration from environment variables.

```python
config = LuminaConfig.from_env()
```

#### Instance Methods

##### `validate() -> bool`

Validate configuration (checks API keys, creates directories).

##### `get_api_key(provider: Optional[str] = None) -> Optional[str]`

Get API key for provider.

### Configuration Functions

```python
from lumina.utils.config import get_config, set_config

# Get global config
config = get_config()

# Set global config
set_config(new_config)
```

---

## Utilities

### Logging

```python
from lumina.utils.logger import get_logger, setup_logging

# Setup logging
logger = setup_logging(
    verbose=True,
    log_file=Path("lumina.log")
)

# Get logger
logger = get_logger()

# Log methods
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.debug("Debug message")
logger.success("Success message")
logger.agent_action("action", "detail")
logger.tool_call("tool_name", "params")
logger.thinking("Thinking process")
```

---

## Complete Example

```python
import asyncio
from pathlib import Path
from lumina import Lumina
from lumina.tools import Tool, ToolParameter
from lumina.utils.config import LuminaConfig

# Custom tool
class GreetTool(Tool):
    name = "greet"
    description = "Greet someone"
    parameters = [
        ToolParameter("name", "string", "Name to greet", True)
    ]
    
    async def execute(self, name: str, **kwargs):
        return {
            "status": "success",
            "result": f"Hello, {name}!"
        }

async def main():
    # Configure
    config = LuminaConfig(
        provider="openai",
        model="gpt-4-turbo-preview",
        temperature=0.7,
        verbose=True
    )
    
    # Create agent with custom tool
    agent = Lumina(
        config=config,
        tools=[GreetTool()],
        enable_memory=True
    )
    
    # Run task
    result = await agent.run("Please greet Alice")
    print(result)
    
    # Chat
    response = await agent.chat("What tools do you have?")
    print(response)
    
    # Reset for new task
    agent.reset()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Error Handling

All async methods may raise exceptions. Wrap in try-except:

```python
try:
    result = await agent.run("Task")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Error: {e}")
```

---

## Type Hints

Lumina uses comprehensive type hints. Enable type checking:

```python
from typing import List, Dict, Any, Optional
```

Use with mypy:
```bash
mypy lumina/
```

---

For more examples, see the `examples/` directory.
