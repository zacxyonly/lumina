# Contributing to Lumina

Thank you for your interest in contributing to Lumina! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain a professional environment

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Error messages and logs

### Suggesting Features

1. Check existing feature requests
2. Create a new issue with:
   - Clear use case
   - Proposed solution
   - Alternative approaches considered
   - Impact on existing functionality

### Pull Requests

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/lumina.git
   cd lumina
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Setup Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

4. **Make Your Changes**
   - Follow the code style guidelines below
   - Add tests for new features
   - Update documentation as needed

5. **Run Tests**
   ```bash
   pytest
   pytest --cov=lumina  # With coverage
   ```

6. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   ```
   
   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Test changes
   - `refactor:` Code refactoring
   - `style:` Code style changes
   - `chore:` Maintenance tasks

7. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub

## Code Style Guidelines

### Python Style
- Follow PEP 8
- Use type hints for all functions
- Maximum line length: 100 characters
- Use docstrings for all public functions/classes

### Example
```python
from typing import List, Dict, Any


async def process_data(
    items: List[str],
    config: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Process a list of items with given configuration.
    
    Args:
        items: List of items to process
        config: Configuration dictionary
    
    Returns:
        List of processed results
    
    Raises:
        ValueError: If items list is empty
    """
    if not items:
        raise ValueError("Items list cannot be empty")
    
    results = []
    for item in items:
        result = await process_item(item, config)
        results.append(result)
    
    return results
```

### Testing Guidelines

1. **Write Tests for New Features**
   ```python
   import pytest
   
   class TestNewFeature:
       """Test suite for new feature."""
       
       def test_basic_functionality(self):
           """Test basic feature works."""
           result = new_feature("input")
           assert result == "expected"
       
       @pytest.mark.asyncio
       async def test_async_functionality(self):
           """Test async feature."""
           result = await async_new_feature()
           assert result is not None
   ```

2. **Test Coverage**
   - Aim for >80% coverage
   - Test edge cases
   - Test error conditions

3. **Test Organization**
   ```
   tests/
   ├── test_core.py      # Core functionality
   ├── test_tools.py     # Tool system
   ├── test_llm.py       # LLM providers
   └── test_memory.py    # Memory system
   ```

## Project Structure

```
lumina/
├── lumina/              # Main package
│   ├── core/           # Core components
│   │   ├── agent.py    # Main agent
│   │   ├── llm.py      # LLM providers
│   │   └── memory.py   # Memory system
│   ├── tools/          # Tool system
│   │   ├── base.py     # Base classes
│   │   └── file.py     # File tools
│   ├── utils/          # Utilities
│   └── cli.py          # CLI interface
├── tests/              # Test suite
├── examples/           # Example scripts
└── docs/              # Documentation
```

## Adding New Tools

1. **Create Tool Class**
   ```python
   from lumina.tools.base import Tool, ToolParameter
   
   class MyTool(Tool):
       """Description of what the tool does."""
       
       name = "my_tool"
       description = "Brief description for LLM"
       parameters = [
           ToolParameter(
               name="input",
               type="string",
               description="What this parameter does",
               required=True
           )
       ]
       
       async def execute(self, input: str, **kwargs):
           """Execute the tool logic."""
           result = process(input)
           return {
               "status": "success",
               "result": result
           }
   ```

2. **Add Tests**
   ```python
   @pytest.mark.asyncio
   async def test_my_tool():
       tool = MyTool()
       result = await tool.run(input="test")
       assert result["status"] == "success"
   ```

3. **Update Documentation**
   - Add tool to README
   - Document parameters
   - Provide usage examples

## Adding New LLM Providers

1. **Implement Provider Class**
   ```python
   from lumina.core.llm import LLMProvider, Message, LLMResponse
   
   class NewProvider(LLMProvider):
       """Provider for NewLLM."""
       
       def __init__(self, api_key: str, model: str, **kwargs):
           super().__init__(api_key, model, **kwargs)
           # Initialize client
       
       async def chat(self, messages, temperature, max_tokens, tools, **kwargs):
           # Implement chat logic
           pass
       
       async def stream(self, messages, temperature, max_tokens, **kwargs):
           # Implement streaming
           pass
   ```

2. **Register in Factory**
   ```python
   # In lumina/core/llm.py
   providers = {
       "openai": OpenAIProvider,
       "anthropic": AnthropicProvider,
       "newprovider": NewProvider,  # Add here
   }
   ```

## Documentation

- Update README.md for user-facing changes
- Update docstrings for API changes
- Add examples for new features
- Update CHANGELOG.md

## Getting Help

- GitHub Issues: Bug reports and feature requests
- Discussions: Questions and general discussion
- Pull Request Comments: Code review and feedback

## Recognition

Contributors will be recognized in:
- README.md contributors section
- CHANGELOG.md for significant contributions
- GitHub contributors page

Thank you for contributing to Lumina! 🌟
