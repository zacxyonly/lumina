"""Audit logging and execution tracing for Lumina.

Provides comprehensive logging of agent actions for debugging,
compliance, and replay functionality.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class EventType(Enum):
    """Types of audit events."""
    
    RUN_START = "run_start"
    RUN_END = "run_end"
    PLAN_CREATED = "plan_created"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    TOOL_ERROR = "tool_error"
    LLM_REQUEST = "llm_request"
    LLM_RESPONSE = "llm_response"
    PERMISSION_CHECK = "permission_check"
    PERMISSION_DENIED = "permission_denied"
    USER_CONFIRMATION = "user_confirmation"
    MEMORY_UPDATE = "memory_update"
    ERROR = "error"
    STATE_CHANGE = "state_change"


@dataclass
class AuditEvent:
    """Single audit event."""
    
    timestamp: str
    event_type: EventType
    run_id: str
    iteration: int
    data: Dict[str, Any]
    
    # Optional fields
    tool_name: Optional[str] = None
    scope: Optional[str] = None
    success: Optional[bool] = None
    error: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type.value,
            "run_id": self.run_id,
            "iteration": self.iteration,
            "tool_name": self.tool_name,
            "scope": self.scope,
            "success": self.success,
            "error": self.error,
            "data": self.data,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditEvent":
        """Create from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            event_type=EventType(data["event_type"]),
            run_id=data["run_id"],
            iteration=data["iteration"],
            data=data.get("data", {}),
            tool_name=data.get("tool_name"),
            scope=data.get("scope"),
            success=data.get("success"),
            error=data.get("error"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class RunTrace:
    """Complete trace of an agent run."""
    
    run_id: str
    started_at: str
    ended_at: Optional[str] = None
    
    # Input
    task: str
    context: Optional[str] = None
    
    # Configuration snapshot
    config: Dict[str, Any] = field(default_factory=dict)
    policy: Dict[str, Any] = field(default_factory=dict)
    
    # Execution trace
    events: List[AuditEvent] = field(default_factory=list)
    
    # State snapshots
    working_state: Dict[str, Any] = field(default_factory=dict)
    memory_snapshot: Dict[str, Any] = field(default_factory=dict)
    
    # Results
    final_answer: Optional[str] = None
    success: bool = False
    error: Optional[str] = None
    
    # Metrics
    total_iterations: int = 0
    total_tool_calls: int = 0
    total_llm_calls: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    duration_seconds: float = 0.0
    
    def add_event(self, event: AuditEvent) -> None:
        """Add event to trace."""
        self.events.append(event)
        
        # Update metrics
        if event.event_type == EventType.TOOL_CALL:
            self.total_tool_calls += 1
        elif event.event_type == EventType.LLM_REQUEST:
            self.total_llm_calls += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "run_id": self.run_id,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "task": self.task,
            "context": self.context,
            "config": self.config,
            "policy": self.policy,
            "events": [e.to_dict() for e in self.events],
            "working_state": self.working_state,
            "memory_snapshot": self.memory_snapshot,
            "final_answer": self.final_answer,
            "success": self.success,
            "error": self.error,
            "metrics": {
                "total_iterations": self.total_iterations,
                "total_tool_calls": self.total_tool_calls,
                "total_llm_calls": self.total_llm_calls,
                "total_tokens": self.total_tokens,
                "total_cost": self.total_cost,
                "duration_seconds": self.duration_seconds,
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RunTrace":
        """Create from dictionary."""
        trace = cls(
            run_id=data["run_id"],
            started_at=data["started_at"],
            ended_at=data.get("ended_at"),
            task=data["task"],
            context=data.get("context"),
            config=data.get("config", {}),
            policy=data.get("policy", {}),
            working_state=data.get("working_state", {}),
            memory_snapshot=data.get("memory_snapshot", {}),
            final_answer=data.get("final_answer"),
            success=data.get("success", False),
            error=data.get("error"),
        )
        
        # Restore events
        trace.events = [
            AuditEvent.from_dict(e) for e in data.get("events", [])
        ]
        
        # Restore metrics
        metrics = data.get("metrics", {})
        trace.total_iterations = metrics.get("total_iterations", 0)
        trace.total_tool_calls = metrics.get("total_tool_calls", 0)
        trace.total_llm_calls = metrics.get("total_llm_calls", 0)
        trace.total_tokens = metrics.get("total_tokens", 0)
        trace.total_cost = metrics.get("total_cost", 0.0)
        trace.duration_seconds = metrics.get("duration_seconds", 0.0)
        
        return trace
    
    def get_digest(self) -> str:
        """Get SHA256 digest of trace for integrity verification."""
        trace_json = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(trace_json.encode()).hexdigest()


class AuditLogger:
    """Audit logger for agent execution."""
    
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_trace: Optional[RunTrace] = None
        self.traces: Dict[str, RunTrace] = {}
    
    def start_run(
        self,
        run_id: str,
        task: str,
        context: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        policy: Optional[Dict[str, Any]] = None,
    ) -> RunTrace:
        """Start a new run trace."""
        trace = RunTrace(
            run_id=run_id,
            started_at=datetime.now().isoformat(),
            task=task,
            context=context,
            config=config or {},
            policy=policy or {},
        )
        
        self.current_trace = trace
        self.traces[run_id] = trace
        
        # Log start event
        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_type=EventType.RUN_START,
            run_id=run_id,
            iteration=0,
            data={"task": task, "context": context}
        )
        trace.add_event(event)
        
        return trace
    
    def end_run(
        self,
        run_id: str,
        final_answer: Optional[str] = None,
        success: bool = True,
        error: Optional[str] = None,
        duration_seconds: float = 0.0,
    ) -> None:
        """End a run trace."""
        if run_id not in self.traces:
            return
        
        trace = self.traces[run_id]
        trace.ended_at = datetime.now().isoformat()
        trace.final_answer = final_answer
        trace.success = success
        trace.error = error
        trace.duration_seconds = duration_seconds
        
        # Log end event
        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_type=EventType.RUN_END,
            run_id=run_id,
            iteration=trace.total_iterations,
            data={
                "success": success,
                "error": error,
                "duration_seconds": duration_seconds,
            }
        )
        trace.add_event(event)
        
        # Save trace
        self.save_trace(trace)
        
        if run_id == getattr(self.current_trace, "run_id", None):
            self.current_trace = None
    
    def log_event(
        self,
        event_type: EventType,
        run_id: str,
        iteration: int,
        data: Dict[str, Any],
        **kwargs
    ) -> None:
        """Log an audit event."""
        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            run_id=run_id,
            iteration=iteration,
            data=data,
            **kwargs
        )
        
        if run_id in self.traces:
            self.traces[run_id].add_event(event)
    
    def log_tool_call(
        self,
        run_id: str,
        iteration: int,
        tool_name: str,
        params: Dict[str, Any],
        scope: Optional[str] = None,
    ) -> None:
        """Log tool call."""
        self.log_event(
            EventType.TOOL_CALL,
            run_id,
            iteration,
            {"tool": tool_name, "params": params},
            tool_name=tool_name,
            scope=scope
        )
    
    def log_tool_result(
        self,
        run_id: str,
        iteration: int,
        tool_name: str,
        result: Dict[str, Any],
        success: bool = True,
    ) -> None:
        """Log tool result."""
        self.log_event(
            EventType.TOOL_RESULT,
            run_id,
            iteration,
            {"tool": tool_name, "result": result},
            tool_name=tool_name,
            success=success
        )
    
    def log_llm_request(
        self,
        run_id: str,
        iteration: int,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float,
    ) -> None:
        """Log LLM request."""
        self.log_event(
            EventType.LLM_REQUEST,
            run_id,
            iteration,
            {
                "model": model,
                "temperature": temperature,
                "message_count": len(messages),
                "last_message": messages[-1] if messages else None,
            }
        )
    
    def log_llm_response(
        self,
        run_id: str,
        iteration: int,
        content: str,
        tokens: int = 0,
        cost: float = 0.0,
    ) -> None:
        """Log LLM response."""
        self.log_event(
            EventType.LLM_RESPONSE,
            run_id,
            iteration,
            {
                "content_length": len(content),
                "tokens": tokens,
                "cost": cost,
            }
        )
        
        # Update trace metrics
        if run_id in self.traces:
            trace = self.traces[run_id]
            trace.total_tokens += tokens
            trace.total_cost += cost
    
    def log_permission_check(
        self,
        run_id: str,
        iteration: int,
        scope: str,
        granted: bool,
        level: str,
    ) -> None:
        """Log permission check."""
        event_type = EventType.PERMISSION_DENIED if not granted else EventType.PERMISSION_CHECK
        self.log_event(
            event_type,
            run_id,
            iteration,
            {"scope": scope, "granted": granted, "level": level},
            scope=scope,
            success=granted
        )
    
    def save_trace(self, trace: RunTrace) -> None:
        """Save trace to disk."""
        filename = f"trace_{trace.run_id}.json"
        filepath = self.log_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(trace.to_dict(), f, indent=2)
    
    def load_trace(self, run_id: str) -> Optional[RunTrace]:
        """Load trace from disk."""
        filename = f"trace_{run_id}.json"
        filepath = self.log_dir / filename
        
        if not filepath.exists():
            return None
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        return RunTrace.from_dict(data)
    
    def list_traces(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent traces."""
        trace_files = sorted(
            self.log_dir.glob("trace_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        traces = []
        for filepath in trace_files[:limit]:
            with open(filepath, 'r') as f:
                data = json.load(f)
                traces.append({
                    "run_id": data["run_id"],
                    "task": data["task"],
                    "started_at": data["started_at"],
                    "success": data.get("success", False),
                    "duration": data.get("metrics", {}).get("duration_seconds", 0),
                })
        
        return traces
    
    def get_run_summary(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of a run."""
        trace = self.load_trace(run_id)
        if not trace:
            return None
        
        return {
            "run_id": trace.run_id,
            "task": trace.task,
            "success": trace.success,
            "error": trace.error,
            "metrics": {
                "iterations": trace.total_iterations,
                "tool_calls": trace.total_tool_calls,
                "llm_calls": trace.total_llm_calls,
                "tokens": trace.total_tokens,
                "cost": trace.total_cost,
                "duration": trace.duration_seconds,
            },
            "events_count": len(trace.events),
        }
