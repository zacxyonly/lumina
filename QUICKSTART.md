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

## Configuration

1. **Copy environment template**
   ```bash
   cp .env.example .env
   ```

2. **Add your API key**
   
   Edit `.env` and add your OpenAI or Anthropic API key:
   ```env
   LUMINA_PROVIDER=openai
   OPENAI_API_KEY=sk-your-key-here
   ```

3. **Test configuration**
   ```bash
   python -c "from lumina import Lumina; print('Config OK!')"
   ```

## Basic Usage

### Command Line

```bash
# Single command
python -m lumina.cli "List all Python files in this directory"

# Interactive mode
python -m lumina.cli

# With specific provider
python -m lumina.cli --provider anthropic "Summarize README.md"
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

## Next Steps

- Read the full [README.md](README.md)
- Check [examples/basic_usage.py](examples/basic_usage.py)
- Learn about [custom tools](CONTRIBUTING.md#adding-new-tools)
- Explore the [API documentation](#)

## Troubleshooting

### "API key not found"
- Check your `.env` file exists
- Verify API key is correct
- Ensure you've selected the right provider

### "Module not found"
- Activate virtual environment
- Run `pip install -r requirements.txt`

### "Max iterations reached"
- Increase `--max-iterations`
- Break task into smaller steps
- Check if tools are working correctly

## Need Help?

- GitHub Issues: [Report bugs](https://github.com/yourusername/lumina/issues)
- Discussions: [Ask questions](https://github.com/yourusername/lumina/discussions)
- Examples: [See more examples](examples/)

Happy building with Lumina! 🌟
