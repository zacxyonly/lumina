# Lumina Quick Start Guide

Get up and running with Lumina in 5 minutes!

## Installation

```bash
# Clone repository
git clone https://github.com/zacxyonly/lumina.git
cd lumina

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

## Configuration (Interactive Setup)

The easiest way to configure Lumina is using the interactive setup wizard:

```bash
python -m lumina.wizard
```

This will guide you through:
- Selecting your LLM provider (OpenAI, Anthropic, Google, Groq, etc.)
- Entering your API key
- Choosing a model
- Configuring agent settings
- Testing the configuration

### Manual Configuration

If you prefer manual setup:

1. **Copy environment template**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your API key**
   ```env
   LUMINA_PROVIDER=openai
   OPENAI_API_KEY=sk-your-key-here
   ```

3. **Verify configuration**
   ```bash
   python -m lumina.cli --verbose
   ```

## Basic Usage

### Command Line

```bash
# Single command
python -m lumina.cli "List all Python files in this directory"

# Interactive mode
python -m lumina.cli

# With specific model
python -m lumina.cli --provider anthropic --model claude-3-5-sonnet "Your task here"
```

### Python Script

```python
import asyncio
from lumina import Lumina

async def main():
    # Create agent
    agent = Lumina()
    
    # Run a task
    result = await agent.run("Create a file called hello.txt with 'Hello, World!'")
    print(result)

asyncio.run(main())
```

## Supported Providers

Lumina supports multiple LLM providers:

- **OpenAI**: GPT-4, GPT-4 Turbo, GPT-3.5-Turbo
- **Anthropic**: Claude 3, Claude 3.5 Sonnet
- **Google**: Gemini Pro
- **Groq**: Mixtral, Llama 2
- **Plus many more via LiteLLM**

## Common Tasks

### File Operations

```bash
# Read a file
python -m lumina.cli "Read the contents of README.md"

# Create a file
python -m lumina.cli "Create a file called notes.txt with my TODO list"

# Search files
python -m lumina.cli "Find all Python files in this project"
```

### Multi-Step Tasks

```bash
python -m lumina.cli "Create a folder called 'data', then create 3 text files inside it with different content"
```

### Custom Tools

```python
from lumina import Lumina
from lumina.tools import Tool, ToolParameter

class WeatherTool(Tool):
    name = "get_weather"
    description = "Get weather for a city"
    parameters = [
        ToolParameter("city", "string", "City name", True)
    ]
    
    async def execute(self, city: str, **kwargs):
        # Your weather API logic here
        return {"status": "success", "weather": "sunny"}

# Use custom tool
agent = Lumina(tools=[WeatherTool()])
```

## Tips

1. **Use verbose mode for debugging**
   ```bash
   python -m lumina.cli --verbose "Your task here"
   ```

2. **Reset agent state between tasks**
   ```python
   agent.reset()
   ```

3. **Disable memory for stateless operations**
   ```bash
   python -m lumina.cli --no-memory "Quick task"
   ```

4. **Control iterations for complex tasks**
   ```bash
   python -m lumina.cli --max-iterations 20 "Complex multi-step task"
   ```

## Troubleshooting

### "API key not found"
- Run `python -m lumina.wizard` for interactive setup
- Or check your `.env` file and verify the API key is set
- Ensure you've selected the correct provider

### "Module not found"
- Activate virtual environment
- Run `pip install -r requirements.txt`

### "Max iterations reached"
- Increase `--max-iterations`
- Break task into smaller steps
- Check if tools are working correctly

## Next Steps

- **Setup wizard** (recommended): `python -m lumina.wizard`
- Read the full [README.md](README.md)
- Check [examples/basic_usage.py](examples/basic_usage.py)
- Explore the [API documentation](docs/API.md)
- See [production features](docs/PRODUCTION_FEATURES.md)

## Need Help?

- **Setup issues**: Run `python -m lumina.wizard`
- **GitHub Issues**: [Report bugs](https://github.com/zacxyonly/lumina/issues)
- **Discussions**: [Ask questions](https://github.com/zacxyonly/lumina/discussions)
- **Examples**: [See more examples](examples/)

Happy building with Lumina! 🌟
