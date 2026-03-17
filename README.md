# 🌟 Lumina v1.0.0

**Production-Grade AI Agent Framework Built for Controlled Autonomy**

Lumina (Latin for "light") is a lightweight, secure, and production-ready autonomous AI agent framework. Unlike hobby projects, Lumina is designed from the ground up for **safe deployment** with comprehensive permission systems, audit logging, and observability.

> *"A framework built for reliability, not just demos."*

## ✨ Core Philosophy

**Controlled Autonomy**: Powerful enough to be useful, safe enough to be trusted.

- ✅ **Permission-First** - Granular control over every action
- ✅ **Traceable** - Complete audit trails for debugging and compliance
- ✅ **Schema-Driven** - Strict tool contracts prevent errors
- ✅ **Recoverable** - Built-in retry, fallback, and replan mechanisms
- ✅ **Observable** - Real-time state visibility for humans
- ✅ **Evaluable** - Internal benchmarking tracks quality over time

## 🎯 Features

### Production-Grade Core
- 🔐 **Permission System** - 5-level permission model with resource limits
- 📋 **Audit Logging** - Complete execution traces for every run
- 📐 **Tool Contracts** - Schema validation, retry policies, side-effect tracking
- 🧠 **State Management** - Transparent, human-readable execution state
- 📊 **Evaluation System** - Built-in benchmarking and quality metrics
- ⚙️ **Confirmation Gates** - User approval for dangerous operations
- 🔄 **Error Recovery** - Multi-level retry with automatic fallback

### Developer Experience
- 🤖 **Autonomous Agent** - Self-directed task planning and execution
- 🔧 **Extensible Tools** - Easy plugin architecture with strict contracts
- 💾 **Memory Management** - Context-aware 3-tier memory system
- 🎯 **Multi-Provider** - OpenAI, Anthropic support (more coming)
- 📊 **Rich CLI** - Beautiful terminal UI with real-time feedback
- 🔄 **Async Architecture** - High-performance async/await
- 🛡️ **Type Safety** - Full type hints throughout
- 🧪 **Testing Tools** - Dry-run mode, deterministic execution

## 🚀 Quick Start

```bash
# Clone and setup
git clone <your-repo-url>
cd lumina
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run with safe defaults
python -m lumina.cli "List Python files in this directory"
```

### Production-Safe Example

```python
from lumina import Lumina
from lumina.core.permissions import POLICY_SAFE_AUTO

# Safe by default - confirms dangerous actions
agent = Lumina(policy=POLICY_SAFE_AUTO)

result = await agent.run("Analyze this codebase and suggest improvements")
print(result)

# Review what happened
trace = agent.audit_logger.load_trace(agent.session_id)
print(f"Tools called: {trace.total_tool_calls}")
print(f"Cost: ${trace.total_cost:.4f}")
```

## 📦 Installation

### Requirements
- Python 3.10+
- pip or poetry

### Dependencies
```bash
pip install -r requirements.txt
```

## 🏗️ Architecture

```
lumina/
├── core/                     # Core framework components
│   ├── agent.py             # Main agent orchestrator
│   ├── llm.py               # LLM provider abstraction
│   ├── memory.py            # 3-tier memory system
│   ├── permissions.py       # Permission & security system
│   ├── audit.py             # Audit logging & tracing
│   ├── contracts.py         # Tool contract enforcement
│   ├── state.py             # State management
│   └── evaluator.py         # Benchmarking system
├── tools/                   # Tool ecosystem
│   ├── base.py              # Tool base class & registry
│   ├── file.py              # File operations
│   └── calculator.py        # Mathematical operations
├── utils/                   # Utilities
│   ├── logger.py            # Structured logging
│   └── config.py            # Configuration management
└── cli.py                   # Command-line interface
```

### What Makes Lumina Different?

**Not just another agent wrapper**. Lumina addresses the gaps most frameworks ignore:

| Feature | Typical Framework | Lumina |
|---------|------------------|--------|
| Permissions | "Just run it" | 5-level granular control |
| Audit | Maybe some logs | Complete execution traces |
| Tool Safety | Hope it works | Contract validation + retry |
| State Visibility | Black box | Human-readable state |
| Error Recovery | Crash and restart | Multi-level retry + fallback |
| Quality Tracking | Manual testing | Built-in benchmarking |
| Confirmations | All or nothing | Per-action approval gates |

See [Production Features](docs/PRODUCTION_FEATURES.md) for detailed documentation.

## 🔧 Configuration

Create a `.env` file:

```env
# LLM Provider (openai, anthropic, google, groq)
LUMINA_PROVIDER=openai
LUMINA_MODEL=gpt-4-turbo-preview

# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
GROQ_API_KEY=...

# Agent Settings
LUMINA_MAX_ITERATIONS=10
LUMINA_TEMPERATURE=0.7
LUMINA_VERBOSE=true
```

## 🎯 Usage Examples

### Basic Usage
```python
from lumina import Lumina

agent = Lumina()
result = await agent.run("Create a TODO app in React")
print(result)
```

### Custom Tools
```python
from lumina.tools import Tool

class CustomTool(Tool):
    name = "custom_tool"
    description = "Does something custom"
    
    async def execute(self, **params):
        return {"status": "success"}

agent = Lumina(tools=[CustomTool()])
```

### CLI Usage
```bash
# Interactive mode
python -m lumina.cli

# Single command
python -m lumina.cli "What's the weather in Jakarta?"

# With specific provider
python -m lumina.cli --provider anthropic "Summarize this file: data.txt"
```

## 🛠️ Available Tools

- **FileSystem** - Read, write, search files
- **WebBrowser** - Fetch URLs, search web
- **CodeExecutor** - Run Python/Node.js code safely
- **Calculator** - Mathematical operations
- **Memory** - Store and retrieve context

## 🧠 Memory System

Lumina maintains:
- **Short-term memory** - Current conversation context
- **Working memory** - Active task state
- **Long-term memory** - Persistent facts and learnings

## 🔐 Security

- Sandboxed code execution
- File system access controls
- API key encryption
- Rate limiting

## 📊 Monitoring

View agent activity:
```bash
# Live monitoring
python -m lumina.cli --monitor

# View logs
tail -f logs/lumina.log
```

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=lumina

# Specific test
pytest tests/test_agent.py
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repo
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📝 Roadmap

- [ ] v1.1.0 - GUI interface
- [ ] v1.2.0 - Multi-agent collaboration
- [ ] v1.3.0 - Voice interface
- [ ] v2.0.0 - Plugin marketplace

## 📄 License

MIT License - see LICENSE file

## 🙏 Credits

Built with inspiration from AutoGPT, LangChain, and OpenClaw.

---

**Made with ❤️ by Mundai**
