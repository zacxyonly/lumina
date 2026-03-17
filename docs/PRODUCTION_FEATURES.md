# Lumina Production Features

This document covers the production-grade features that distinguish Lumina from typical agent frameworks.

## Overview

Lumina is built on the principle of **controlled autonomy** - powerful enough to be useful, safe enough to be trusted. These features ensure reliability, safety, and observability in production use.

---

## 1. Permission System

### Granular Permission Model

Every tool execution goes through a permission check with multiple levels:

```python
from lumina.core.permissions import (
    PermissionPolicy,
    PermissionLevel,
    PermissionScope,
    PermissionManager
)

# Create custom policy
policy = PermissionPolicy(
    name="my_policy",
    description="Custom policy for production use",
    default_level=PermissionLevel.CONFIRM
)

# Set specific permissions
policy.scopes = {
    PermissionScope.FILE_READ: PermissionLevel.AUTO_SAFE,
    PermissionScope.FILE_WRITE: PermissionLevel.CONFIRM,
    PermissionScope.SHELL_EXEC: PermissionLevel.DENIED,
}

# Path restrictions
policy.allowed_write_paths = {Path("/safe/directory")}
policy.blocked_domains = {"malicious.com"}
```

### Permission Levels

- **DENIED**: Action completely blocked
- **READ_ONLY**: Can read but not modify
- **CONFIRM**: Requires user confirmation
- **AUTO_SAFE**: Auto-run if marked safe
- **AUTO_ALL**: Full automation (use with caution)

### Built-in Policies

```python
from lumina.core.permissions import (
    POLICY_OBSERVER,    # Read-only mode
    POLICY_SAFE_AUTO,   # Safe operations auto, dangerous confirm
    POLICY_FULL_AUTO,   # Full automation
    POLICY_STRICT,      # Confirm everything
)

agent = Lumina(policy=POLICY_SAFE_AUTO)
```

### Resource Limits

```python
policy.max_file_size_mb = 10
policy.max_network_calls_per_run = 50
policy.max_shell_commands_per_run = 10
```

---

## 2. Audit Logging & Tracing

### Complete Execution Traces

Every agent run creates a complete, replayable trace:

```python
from lumina.core.audit import AuditLogger

audit = AuditLogger(log_dir=Path("./audit"))

# Traces are automatically created
result = await agent.run("Create a report")

# Load trace for analysis
trace = audit.load_trace(agent.session_id)

print(f"Task: {trace.task}")
print(f"Success: {trace.success}")
print(f"Iterations: {trace.total_iterations}")
print(f"Tool calls: {trace.total_tool_calls}")
print(f"Cost: ${trace.total_cost:.4f}")
```

### Event Types Tracked

- Run start/end
- Plan creation
- Tool calls and results
- LLM requests and responses
- Permission checks
- User confirmations
- Memory updates
- Errors and state changes

### Trace Contents

Each trace includes:

```python
{
    "run_id": "abc123",
    "task": "User's task",
    "config": {...},          # Configuration snapshot
    "policy": {...},          # Permission policy snapshot
    "events": [...],          # All events chronologically
    "working_state": {...},   # Final state
    "memory_snapshot": {...}, # Memory at completion
    "metrics": {
        "iterations": 5,
        "tool_calls": 8,
        "tokens": 1234,
        "cost": 0.0234,
        "duration": 45.2
    }
}
```

### Replay Capability

```python
# Load and analyze past run
trace = audit.load_trace("run_abc123")

# See exactly what happened
for event in trace.events:
    if event.event_type == EventType.TOOL_CALL:
        print(f"Called {event.tool_name} with {event.data}")
```

---

## 3. Tool Contracts

### Strict Schema Validation

Every tool has a contract that defines exact behavior:

```python
from lumina.core.contracts import ToolContract, SideEffect, RetryPolicy

contract = ToolContract(
    name="write_file",
    description="Write content to file",
    version="1.0.0",
    
    # Input schema with validation
    input_schema={
        "path": {
            "type": "string",
            "required": True,
            "minLength": 1,
            "maxLength": 1000,
        },
        "content": {
            "type": "string",
            "required": True,
        }
    },
    
    # Output schema
    output_schema={
        "status": {"type": "string", "required": True},
        "bytes_written": {"type": "integer", "required": True},
    },
    
    # Behavior guarantees
    side_effects=SideEffect.WRITE,
    idempotent=False,
    deterministic=True,
    dangerous=True,
    requires_confirmation=True,
    
    # Execution settings
    timeout_seconds=30.0,
    retry_policy=RetryPolicy(
        max_attempts=1,  # Don't retry writes
        retry_on_error=False
    ),
    
    # Permission
    permission_scope="tool.file.write",
)
```

### Automatic Validation

```python
# Input validation
is_valid, error = contract.validate_input(params)

# Output validation
is_valid, error = contract.validate_output(result)
```

### Retry Policies

```python
retry_policy = RetryPolicy(
    max_attempts=3,
    initial_delay=1.0,
    max_delay=30.0,
    exponential_base=2.0,
    retry_on_timeout=True,
    retry_on_error=True,
)
```

### Side Effect Classification

- **NONE**: Pure function
- **READ**: Reads external state
- **WRITE**: Modifies external state
- **DELETE**: Deletes data
- **NETWORK**: Network communication
- **DANGEROUS**: Potentially harmful

---

## 4. State Management

### Transparent State Tracking

```python
from lumina.core.state import StateManager, ExecutionPhase

state_manager = StateManager()

# State is always accessible
print(state_manager.working_state.get_summary())
```

### State Components

**Working State:**
```python
state = agent.state_manager.working_state

print(f"Phase: {state.phase}")
print(f"Iteration: {state.iteration}")
print(f"Tokens used: {state.tokens_used}")
print(f"Tools called: {state.tools_called}")
```

**Plan:**
```python
plan = state.current_plan

print(f"Goal: {plan.goal}")
print(f"Progress: {plan.progress_percentage()}%")

current_step = plan.get_current_step()
print(f"Current: {current_step.description}")
```

**Decision Log:**
```python
# See what agent decided and why
for decision in state.decisions:
    print(f"{decision['decision']}: {decision['reasoning']}")
```

### State Snapshots

```python
# Take snapshot
snapshot = state_manager.snapshot()

# Restore later
state_manager.restore_snapshot(index=-1)
```

### Export/Import

```python
# Export for debugging
state_manager.export_state("debug_state.json")

# Import for replay
state_manager.import_state("debug_state.json")
```

---

## 5. Evaluation System

### Internal Benchmarking

```python
from lumina.core.evaluator import Evaluator

evaluator = Evaluator(eval_dir=Path("./evals"), version="1.0.0")

# Run benchmark suite
report = await evaluator.run_benchmark(agent)

print(f"Success rate: {report.task_success_rate}%")
print(f"Avg iterations: {report.avg_iterations}")
print(f"Tool accuracy: {report.tool_accuracy_rate}%")
```

### Metrics Tracked

**Performance:**
- Task success rate
- Average iterations per task
- Average tokens per task
- Total cost
- Duration

**Quality:**
- Correct tool selection rate
- Error recovery rate
- Hallucination detection
- Unsafe actions blocked

### Custom Evaluation Tasks

```python
from lumina.core.evaluator import EvaluationTask

task = EvaluationTask(
    task_id="custom_task_1",
    description="Analyze codebase and suggest improvements",
    expected_outcome="Analysis with actionable suggestions",
    category="code_analysis",
    difficulty="hard",
    required_tools=["read_file", "list_directory"],
    max_iterations=15,
)

evaluator.add_task(task)
```

### Compare Versions

```python
# Run baseline
baseline_report = await evaluator.run_benchmark(agent_v1)

# After changes
current_report = await evaluator.run_benchmark(agent_v2)

# Compare
comparison = evaluator.compare_reports(
    baseline_report.run_id,
    current_report.run_id
)

print(f"Success rate delta: {comparison['success_rate_delta']:+.1f}%")
print(f"Cost delta: ${comparison['cost_delta']:+.4f}")
```

---

## 6. Recovery & Error Handling

### Multi-Level Recovery

```python
# Agent automatically:
# 1. Retries with backoff (per tool contract)
# 2. Tries fallback tools
# 3. Replans if needed
# 4. Escalates to user confirmation
# 5. Can rollback if safe to do so
```

### Error State Tracking

```python
state = agent.state_manager.working_state

print(f"Last error: {state.last_error}")
print(f"Error count: {state.error_count}")
print(f"Recovery attempts: {state.recovery_attempts}")
```

---

## 7. Confirmation Gates

### User Approval for Dangerous Actions

```python
async def my_confirmation_handler(action: str, context: dict) -> bool:
    """Custom confirmation handler."""
    print(f"Agent wants to: {action}")
    print(f"Context: {context}")
    
    response = input("Allow? (y/n): ")
    return response.lower() == 'y'

# Set handler
agent.permission_manager.set_confirmation_handler(my_confirmation_handler)
```

### Execution Modes

```python
# Observe only - no actions
agent = Lumina(policy=POLICY_OBSERVER)

# Plan only - create plan but don't execute
result = await agent.plan_only("Build a web scraper")

# Confirm each action
agent = Lumina(policy=POLICY_STRICT)

# Auto safe operations only
agent = Lumina(policy=POLICY_SAFE_AUTO)

# Full automation (use carefully!)
agent = Lumina(policy=POLICY_FULL_AUTO)
```

---

## 8. Dry Run Mode

### Test Without Side Effects

```python
from lumina import Lumina

agent = Lumina(dry_run=True)

# Tool calls are logged but not executed
result = await agent.run("Delete all temp files")

# Check what would have happened
trace = agent.audit_logger.load_trace(agent.session_id)
for event in trace.events:
    if event.event_type == EventType.TOOL_CALL:
        print(f"Would call: {event.tool_name}")
```

---

## 9. Cost Tracking

### Token and Cost Monitoring

```python
# Automatic tracking in trace
trace = agent.audit_logger.load_trace(run_id)

print(f"Tokens: {trace.total_tokens}")
print(f"Cost: ${trace.total_cost:.4f}")

# Set budget limits
agent = Lumina(max_cost_per_run=0.50)  # Stop at $0.50
```

---

## 10. Deterministic Mode

### Reproducible Execution

```python
# Set seed for deterministic LLM sampling
agent = Lumina(
    config=LuminaConfig(
        temperature=0.0,  # Deterministic
        seed=42,          # Fixed seed
    )
)

# Same task = same result (for testing)
result1 = await agent.run("List files in current directory")
agent.reset()
result2 = await agent.run("List files in current directory")

assert result1 == result2
```

---

## Best Practices

### 1. Start with Strict Policy

```python
# Start restrictive, relax as needed
agent = Lumina(policy=POLICY_STRICT)
```

### 2. Enable Audit Logging

```python
# Always enable for production
agent = Lumina(
    audit_logger=AuditLogger(log_dir=Path("./production_logs"))
)
```

### 3. Set Resource Limits

```python
policy.max_network_calls_per_run = 100
policy.max_file_size_mb = 50
config.max_iterations = 20
```

### 4. Use Tool Contracts

```python
# Define strict contracts for all tools
# Validate input/output
# Set appropriate retry policies
```

### 5. Regular Benchmarking

```python
# Run evals before deploying
report = await evaluator.run_benchmark(agent)

if report.task_success_rate < 80:
    raise ValueError("Success rate too low for deployment")
```

### 6. Monitor State

```python
# Regularly check state
if state.error_count > 5:
    agent.reset()  # Too many errors, restart
```

---

## Production Checklist

Before deploying an agent:

- [ ] Permission policy configured
- [ ] Audit logging enabled
- [ ] Tool contracts defined with schemas
- [ ] Retry policies set appropriately
- [ ] Confirmation handler implemented
- [ ] Resource limits configured
- [ ] Evaluation suite passing
- [ ] State monitoring in place
- [ ] Error recovery tested
- [ ] Cost budgets set
- [ ] Dry run mode tested
- [ ] Deterministic mode verified (for testing)

---

These features make Lumina production-grade from day one, not as an afterthought.
