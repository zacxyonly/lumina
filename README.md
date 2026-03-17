<div align="center">

# 🌟 Lumina

### Production-Grade AI Agent Framework Built for Controlled Autonomy

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/zacxyonly/lumina/releases)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Lumina** (Latin for *"light"*) is a lightweight, secure, and production-ready autonomous AI agent framework. Unlike hobby projects, Lumina is designed from the ground up for **safe deployment** with comprehensive permission systems, audit logging, and observability.

> *"A framework built for reliability, not just demos."*

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Examples](#-examples)

</div>

---

## ✨ Core Philosophy

<table>
<tr>
<td width="50%">

### 🎯 Controlled Autonomy

Powerful enough to be useful, safe enough to be trusted.

**What makes Lumina different:**
- Not just another LLM wrapper
- Production-first design
- Safety built-in, not bolted-on
- Observable and debuggable
- Battle-tested patterns

</td>
<td width="50%">

### 🛡️ Production-Ready

Built for real-world deployment.

**Core principles:**
- Permission-first architecture
- Complete audit trails
- Schema-driven validation
- Multi-level error recovery
- Quality tracking from day one

</td>
</tr>
</table>

---

## 🎯 Features

### 🔐 Production-Grade Security

<table>
<tr>
<td width="33%">

#### Permission System
- 5-level permission model
- 15+ granular scopes
- Path & domain restrictions
- Resource limits enforcement
- 4 built-in policies

</td>
<td width="33%">

#### Audit Logging
- Complete execution traces
- 14 event types tracked
- Replay capability
- Cost & token tracking
- SHA256 integrity verification

</td>
<td width="34%">

#### Tool Contracts
- Input/output validation
- Retry with exponential backoff
- Side-effect classification
- Timeout enforcement
- Idempotency hints

</td>
</tr>
</table>

### 🧠 Developer Experience

<table>
<tr>
<td width="50%">

#### Autonomous Agent System
- ✅ Self-directed task planning
- ✅ Automatic tool selection
- ✅ Multi-step execution
- ✅ Result synthesis
- ✅ Context awareness

</td>
<td width="50%">

#### State Management
- ✅ 7-phase execution tracking
- ✅ Plan with step progress
- ✅ Decision logging
- ✅ Human-readable summaries
- ✅ State snapshots & restore

</td>
</tr>
<tr>
<td width="50%">

#### Multi-Provider Support
- ✅ OpenAI (GPT-4, GPT-3.5)
- ✅ Anthropic (Claude 3.5)
- ✅ Easy provider integration
- ✅ Consistent API across providers

</td>
<td width="50%">

#### Quality Assurance
- ✅ Built-in benchmarking
- ✅ Quality metrics tracking
- ✅ Version comparison
- ✅ Custom evaluation tasks

</td>
</tr>
</table>

### 🔄 Reliability Features

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Error Recovery** | Multi-level retry with fallback | Resilient execution |
| **Confirmation Gates** | User approval for dangerous ops | Safe automation |
| **Dry Run Mode** | Test without side effects | Risk-free testing |
| **Cost Tracking** | Per-run budget enforcement | Prevent runaway costs |
| **Memory System** | 3-tier context management | Smarter responses |

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/zacxyonly/lumina.git
cd lumina

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and add your API key
```

### Your First Agent

```python
import asyncio
from lumina import Lumina
from lumina.core.permissions import POLICY_SAFE_AUTO

async def main():
    # Create agent with safe defaults
    agent = Lumina(policy=POLICY_SAFE_AUTO)
    
    # Run a task
    result = await agent.run("List all Python files in this directory")
    print(result)
    
    # Check what happened
    trace = agent.audit_logger.load_trace(agent.session_id)
    print(f"\n📊 Stats:")
    print(f"   Tools called: {trace.total_tool_calls}")
    print(f"   Cost: ${trace.total_cost:.4f}")
    print(f"   Duration: {trace.duration_seconds:.2f}s")

asyncio.run(main())
```

### CLI Usage

```bash
# Interactive mode
python -m lumina.cli

# Single command
python -m lumina.cli "Create a TODO list for my project"

# With specific policy
python -m lumina.cli --policy strict "Analyze codebase structure"

# Verbose mode
python -m lumina.cli --verbose "Your task here"
```

---

## 🏗️ Architecture

<div align="center">

```
┌─────────────────────────────────────────────────────────────┐
│                         LUMINA CORE                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Permission  │  │    Audit     │  │     Tool     │      │
│  │    System    │  │   Logging    │  │  Contracts   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    State     │  │  Evaluation  │  │     LLM      │      │
│  │  Management  │  │    System    │  │  Providers   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Agent Orchestrator                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

</div>

### Project Structure

```
lumina/
├── core/                     # 🔥 Core framework components
│   ├── agent.py             # Main agent orchestrator
│   ├── llm.py               # LLM provider abstraction
│   ├── memory.py            # 3-tier memory system
│   ├── permissions.py       # ⭐ Permission & security (350 LOC)
│   ├── audit.py             # ⭐ Audit logging & tracing (400 LOC)
│   ├── contracts.py         # ⭐ Tool contract enforcement (380 LOC)
│   ├── state.py             # ⭐ State management (320 LOC)
│   └── evaluator.py         # ⭐ Benchmarking system (420 LOC)
│
├── tools/                   # 🔧 Tool ecosystem
│   ├── base.py              # Tool base class & registry
│   ├── file.py              # File operations
│   └── calculator.py        # Mathematical operations
│
├── utils/                   # 🛠️ Utilities
│   ├── logger.py            # Structured logging
│   └── config.py            # Configuration management
│
└── cli.py                   # 💻 Command-line interface
```

### What Sets Lumina Apart

<table>
<tr>
<th width="30%">Feature</th>
<th width="35%">Typical Framework</th>
<th width="35%">Lumina</th>
</tr>
<tr>
<td><strong>Permissions</strong></td>
<td>❌ "Just run it"</td>
<td>✅ 5-level granular control</td>
</tr>
<tr>
<td><strong>Audit Trail</strong></td>
<td>❌ Basic logs</td>
<td>✅ Complete execution traces + replay</td>
</tr>
<tr>
<td><strong>Tool Safety</strong></td>
<td>❌ Hope it works</td>
<td>✅ Contract validation + retry</td>
</tr>
<tr>
<td><strong>State Visibility</strong></td>
<td>❌ Black box</td>
<td>✅ Human-readable state</td>
</tr>
<tr>
<td><strong>Error Recovery</strong></td>
<td>❌ Crash and restart</td>
<td>✅ Multi-level retry + fallback</td>
</tr>
<tr>
<td><strong>Quality Tracking</strong></td>
<td>❌ Manual testing</td>
<td>✅ Built-in benchmarking</td>
</tr>
<tr>
<td><strong>Confirmations</strong></td>
<td>❌ All or nothing</td>
<td>✅ Per-action approval gates</td>
</tr>
<tr>
<td><strong>Production Ready</strong></td>
<td>❌ Demo-first</td>
<td>✅ Production-first</td>
</tr>
</table>

---

## 💡 Examples

### Basic Agent Usage

```python
from lumina import Lumina

agent = Lumina()
result = await agent.run("Create a folder structure for a web project")
```

### With Permission Control

```python
from lumina.core.permissions import PermissionPolicy, PermissionLevel, PermissionScope

# Create custom policy
policy = PermissionPolicy(name="strict_policy")
policy.scopes = {
    PermissionScope.FILE_READ: PermissionLevel.AUTO_SAFE,
    PermissionScope.FILE_WRITE: PermissionLevel.CONFIRM,  # Ask before writing
    PermissionScope.SHELL_EXEC: PermissionLevel.DENIED,   # Block shell access
}

agent = Lumina(policy=policy)
```

### With Audit Trail

```python
# Run task
result = await agent.run("Analyze Python files and create report")

# Review execution
trace = agent.audit_logger.load_trace(agent.session_id)

print(f"Task: {trace.task}")
print(f"Success: {trace.success}")
print(f"Iterations: {trace.total_iterations}")
print(f"Cost: ${trace.total_cost:.4f}")

# Replay specific events
for event in trace.events:
    if event.event_type == EventType.TOOL_CALL:
        print(f"Called: {event.tool_name} with {event.data}")
```

### Custom Tool with Contract

```python
from lumina.tools.base import Tool, ToolParameter
from lumina.core.contracts import ToolContract, SideEffect, RetryPolicy

class WeatherTool(Tool):
    name = "get_weather"
    description = "Get weather for a city"
    parameters = [
        ToolParameter("city", "string", "City name", required=True)
    ]
    
    # Define contract
    contract = ToolContract(
        name="get_weather",
        input_schema={
            "city": {"type": "string", "required": True, "minLength": 2}
        },
        output_schema={
            "temperature": {"type": "number", "required": True},
            "condition": {"type": "string", "required": True}
        },
        side_effects=SideEffect.NETWORK,
        timeout_seconds=10.0,
        retry_policy=RetryPolicy(max_attempts=3)
    )
    
    async def execute(self, city: str, **kwargs):
        # Your implementation
        return {
            "status": "success",
            "temperature": 22,
            "condition": "sunny"
        }

# Use custom tool
agent = Lumina(tools=[WeatherTool()])
result = await agent.run("What's the weather in Jakarta?")
```

### Evaluation & Benchmarking

```python
from lumina.core.evaluator import Evaluator

evaluator = Evaluator(eval_dir=Path("./evals"))

# Run benchmark
report = await evaluator.run_benchmark(agent)

print(f"Success Rate: {report.task_success_rate}%")
print(f"Tool Accuracy: {report.tool_accuracy_rate}%")
print(f"Avg Cost: ${report.total_cost/report.total_tasks:.4f}")

# Compare versions
comparison = evaluator.compare_reports(baseline_id, current_id)
print(f"Improvement: {comparison['success_rate_delta']:+.1f}%")
```

### Production Deployment

```python
from lumina.core.permissions import POLICY_SAFE_AUTO

# Production configuration
config = LuminaConfig(
    provider="openai",
    model="gpt-4-turbo-preview",
    temperature=0.3,
    max_iterations=15,
    verbose=False
)

# Create production agent
agent = Lumina(
    config=config,
    policy=POLICY_SAFE_AUTO,
    enable_memory=True
)

# Set confirmation handler
async def confirm_handler(action: str, context: dict) -> bool:
    # Send to approval system
    return await approval_system.request_approval(action)

agent.permission_manager.set_confirmation_handler(confirm_handler)

# Run with monitoring
result = await agent.run("Process customer data")

# Log to monitoring
monitoring.log({
    "task": "process_data",
    "success": trace.success,
    "cost": trace.total_cost,
    "duration": trace.duration_seconds
})
```

More examples in [`examples/`](examples/) directory.

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file:

```env
# LLM Provider
LUMINA_PROVIDER=openai
LUMINA_MODEL=gpt-4-turbo-preview

# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Agent Settings
LUMINA_MAX_ITERATIONS=10
LUMINA_TEMPERATURE=0.7
LUMINA_VERBOSE=true

# Memory & Security
LUMINA_ENABLE_MEMORY=true
LUMINA_ALLOW_CODE_EXEC=false
```

### Programmatic Configuration

```python
from lumina.utils.config import LuminaConfig

config = LuminaConfig(
    provider="openai",
    model="gpt-4-turbo-preview",
    temperature=0.7,
    max_iterations=10,
    verbose=True,
    enable_memory=True
)

agent = Lumina(config=config)
```

### Permission Policies

```python
from lumina.core.permissions import (
    POLICY_OBSERVER,    # Read-only mode
    POLICY_SAFE_AUTO,   # Safe auto, dangerous confirm
    POLICY_FULL_AUTO,   # Full automation (use with caution)
    POLICY_STRICT,      # Confirm everything
)

agent = Lumina(policy=POLICY_SAFE_AUTO)
```

---

## 📚 Documentation

<table>
<tr>
<td width="50%">

### 📖 Core Documentation
- [**Production Features**](docs/PRODUCTION_FEATURES.md) - Complete production guide
- [**API Reference**](docs/API.md) - Full API documentation
- [**Quick Start Guide**](QUICKSTART.md) - Get started in 5 minutes
- [**Architecture Overview**](STRUCTURE.md) - Project structure

</td>
<td width="50%">

### 🎯 Developer Guides
- [**Contributing Guide**](CONTRIBUTING.md) - How to contribute
- [**Git Workflow**](GIT_GUIDE.md) - Release process
- [**Changelog**](CHANGELOG.md) - Version history
- [**Release Notes**](RELEASE_NOTES.md) - v1.0.0 details

</td>
</tr>
</table>

### Key Concepts

<details>
<summary><strong>🔐 Permission System</strong></summary>

Control what your agent can do:

```python
policy = PermissionPolicy(name="custom")
policy.scopes = {
    PermissionScope.FILE_READ: PermissionLevel.AUTO_SAFE,
    PermissionScope.FILE_WRITE: PermissionLevel.CONFIRM,
    PermissionScope.SHELL_EXEC: PermissionLevel.DENIED,
}
policy.allowed_write_paths = {Path("./safe")}
```

</details>

<details>
<summary><strong>📋 Audit Logging</strong></summary>

Track everything your agent does:

```python
trace = agent.audit_logger.load_trace(run_id)
print(f"Events: {len(trace.events)}")
print(f"Cost: ${trace.total_cost:.4f}")

# Replay execution
for event in trace.events:
    print(f"{event.event_type}: {event.data}")
```

</details>

<details>
<summary><strong>📐 Tool Contracts</strong></summary>

Enforce strict tool behavior:

```python
contract = ToolContract(
    input_schema={...},
    output_schema={...},
    retry_policy=RetryPolicy(max_attempts=3),
    dangerous=True,
    timeout_seconds=30
)
```

</details>

<details>
<summary><strong>🧠 State Management</strong></summary>

Monitor agent execution state:

```python
state = agent.state_manager.working_state
print(state.get_summary())
# Shows: phase, iteration, plan, progress, errors
```

</details>

---

## 🛠️ Built-in Tools

| Tool | Description | Permission Scope |
|------|-------------|------------------|
| **read_file** | Read file contents | `FILE_READ` |
| **write_file** | Write to file | `FILE_WRITE` |
| **list_directory** | List directory contents | `FILE_READ` |
| **search_files** | Search files by pattern | `FILE_READ` |
| **calculator** | Mathematical operations | None (safe) |

### Creating Custom Tools

```python
from lumina.tools.base import Tool, ToolParameter

class MyTool(Tool):
    name = "my_tool"
    description = "What this tool does"
    parameters = [
        ToolParameter("input", "string", "Input parameter", required=True)
    ]
    
    async def execute(self, input: str, **kwargs):
        # Your implementation
        return {"status": "success", "result": "data"}

agent = Lumina(tools=[MyTool()])
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=lumina --cov-report=html

# Specific test
pytest tests/test_core.py -v

# Dry run mode (no side effects)
python -c "
from lumina import Lumina
agent = Lumina(dry_run=True)
await agent.run('Delete all files')  # Won't actually delete
"
```

---

## 🐳 Docker Support

```bash
# Build image
docker build -t lumina:latest .

# Run interactive
docker-compose run lumina

# Run specific task
docker run -it --env-file .env lumina python -m lumina.cli "Your task"
```

---

## 📊 Benchmarking

Track quality metrics over time:

```bash
# Run benchmark suite
python -c "
from lumina.core.evaluator import Evaluator
evaluator = Evaluator(eval_dir=Path('./evals'))
report = await evaluator.run_benchmark(agent)
print(f'Success Rate: {report.task_success_rate}%')
"

# Compare versions
python -c "
comparison = evaluator.compare_reports('v1.0.0', 'v1.1.0')
print(f'Improvement: {comparison[\"success_rate_delta\"]:+.1f}%')
"
```

---

## 🗺️ Roadmap

### v1.1.0 (Planned)
- [ ] Web GUI interface
- [ ] Additional tools (web browsing, code execution)
- [ ] Streaming responses in CLI
- [ ] Semantic memory search
- [ ] Google Gemini provider

### v1.2.0 (Planned)
- [ ] Multi-agent collaboration
- [ ] Agent workflows & pipelines
- [ ] Custom agent personas
- [ ] Voice interface support

### v2.0.0 (Future)
- [ ] Plugin marketplace
- [ ] Cloud deployment options
- [ ] Advanced observability dashboard
- [ ] Agent template library

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code style guidelines
- Testing requirements
- Pull request process
- How to add new tools
- How to add LLM providers

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with inspiration from:
- **AutoGPT** - Autonomous agent patterns
- **LangChain** - Tool abstraction concepts  
- **OpenClaw** - Comprehensive tool ecosystem

But designed for **production deployment** from day one.

---

## 📧 Support

- **Issues**: [Report bugs](https://github.com/zacxyonly/lumina/issues)
- **Discussions**: [Ask questions](https://github.com/zacxyonly/lumina/discussions)
- **Documentation**: [Read the docs](docs/)

---

<div align="center">

**Lumina v1.0.0** - *Built with ❤️ for production deployment*

[⬆ Back to Top](#-lumina)

</div>
