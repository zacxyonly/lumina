"""State management for transparent agent execution.

Provides structured state tracking that's human-readable
and debuggable.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import json


class ExecutionPhase(Enum):
    """Current phase of agent execution."""
    
    INITIALIZING = "initializing"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING_CONFIRMATION = "waiting_confirmation"
    RECOVERING = "recovering"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PlanStep:
    """Single step in agent's plan."""
    
    step_id: int
    description: str
    tool: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    completed: bool = False
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def mark_completed(self, result: Dict[str, Any]) -> None:
        """Mark step as completed."""
        self.completed = True
        self.result = result
    
    def mark_failed(self, error: str) -> None:
        """Mark step as failed."""
        self.completed = True
        self.error = error


@dataclass
class Plan:
    """Agent's execution plan."""
    
    goal: str
    steps: List[PlanStep] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    reasoning: str = ""
    
    def add_step(
        self,
        description: str,
        tool: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> PlanStep:
        """Add step to plan."""
        step = PlanStep(
            step_id=len(self.steps),
            description=description,
            tool=tool,
            params=params or {}
        )
        self.steps.append(step)
        return step
    
    def get_current_step(self) -> Optional[PlanStep]:
        """Get current incomplete step."""
        for step in self.steps:
            if not step.completed:
                return step
        return None
    
    def get_completed_steps(self) -> List[PlanStep]:
        """Get all completed steps."""
        return [s for s in self.steps if s.completed and not s.error]
    
    def get_failed_steps(self) -> List[PlanStep]:
        """Get all failed steps."""
        return [s for s in self.steps if s.error is not None]
    
    def progress_percentage(self) -> float:
        """Get completion percentage."""
        if not self.steps:
            return 0.0
        completed = len([s for s in self.steps if s.completed])
        return (completed / len(self.steps)) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "goal": self.goal,
            "created_at": self.created_at,
            "reasoning": self.reasoning,
            "steps": [s.to_dict() for s in self.steps],
            "progress": self.progress_percentage(),
        }


@dataclass
class WorkingState:
    """Current working state of the agent."""
    
    phase: ExecutionPhase = ExecutionPhase.INITIALIZING
    current_plan: Optional[Plan] = None
    iteration: int = 0
    
    # Context accumulation
    observations: List[str] = field(default_factory=list)
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    tool_results: List[Dict[str, Any]] = field(default_factory=list)
    
    # Error tracking
    last_error: Optional[str] = None
    error_count: int = 0
    recovery_attempts: int = 0
    
    # Resource tracking
    tokens_used: int = 0
    tools_called: int = 0
    
    def add_observation(self, observation: str) -> None:
        """Add observation to state."""
        self.observations.append({
            "iteration": self.iteration,
            "timestamp": datetime.now().isoformat(),
            "content": observation,
        })
    
    def add_decision(self, decision: str, reasoning: str = "") -> None:
        """Record a decision made by agent."""
        self.decisions.append({
            "iteration": self.iteration,
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "reasoning": reasoning,
        })
    
    def add_tool_result(
        self,
        tool_name: str,
        result: Dict[str, Any],
        success: bool = True
    ) -> None:
        """Record tool execution result."""
        self.tool_results.append({
            "iteration": self.iteration,
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "result": result,
            "success": success,
        })
        self.tools_called += 1
    
    def set_error(self, error: str) -> None:
        """Record error in state."""
        self.last_error = error
        self.error_count += 1
    
    def clear_error(self) -> None:
        """Clear error state."""
        self.last_error = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "phase": self.phase.value,
            "iteration": self.iteration,
            "current_plan": self.current_plan.to_dict() if self.current_plan else None,
            "observations": self.observations[-10:],  # Last 10
            "decisions": self.decisions[-10:],        # Last 10
            "tool_results": self.tool_results[-10:],  # Last 10
            "last_error": self.last_error,
            "error_count": self.error_count,
            "recovery_attempts": self.recovery_attempts,
            "resources": {
                "tokens_used": self.tokens_used,
                "tools_called": self.tools_called,
            }
        }
    
    def get_summary(self) -> str:
        """Get human-readable summary of state."""
        summary = [
            f"Phase: {self.phase.value}",
            f"Iteration: {self.iteration}",
        ]
        
        if self.current_plan:
            summary.append(f"Plan: {self.current_plan.goal}")
            summary.append(f"Progress: {self.current_plan.progress_percentage():.0f}%")
            current_step = self.current_plan.get_current_step()
            if current_step:
                summary.append(f"Current step: {current_step.description}")
        
        if self.last_error:
            summary.append(f"Last error: {self.last_error}")
        
        summary.append(f"Tools called: {self.tools_called}")
        summary.append(f"Tokens used: {self.tokens_used}")
        
        return "\n".join(summary)


class StateManager:
    """Manage agent state across execution."""
    
    def __init__(self):
        self.working_state = WorkingState()
        self.state_history: List[Dict[str, Any]] = []
    
    def snapshot(self) -> Dict[str, Any]:
        """Take snapshot of current state."""
        snapshot = self.working_state.to_dict()
        snapshot["snapshot_time"] = datetime.now().isoformat()
        self.state_history.append(snapshot)
        return snapshot
    
    def restore_snapshot(self, index: int = -1) -> None:
        """Restore state from snapshot.
        
        Args:
            index: Index in history (-1 for latest)
        """
        if not self.state_history:
            return
        
        snapshot = self.state_history[index]
        
        # Restore basic state
        self.working_state.phase = ExecutionPhase(snapshot["phase"])
        self.working_state.iteration = snapshot["iteration"]
        self.working_state.last_error = snapshot.get("last_error")
        self.working_state.error_count = snapshot.get("error_count", 0)
        self.working_state.recovery_attempts = snapshot.get("recovery_attempts", 0)
        
        # Restore plan if exists
        plan_data = snapshot.get("current_plan")
        if plan_data:
            plan = Plan(
                goal=plan_data["goal"],
                created_at=plan_data["created_at"],
                reasoning=plan_data.get("reasoning", "")
            )
            for step_data in plan_data["steps"]:
                step = plan.add_step(
                    description=step_data["description"],
                    tool=step_data.get("tool"),
                    params=step_data.get("params", {})
                )
                step.completed = step_data["completed"]
                step.result = step_data.get("result")
                step.error = step_data.get("error")
            
            self.working_state.current_plan = plan
    
    def get_state_diff(self, from_iteration: int) -> Dict[str, Any]:
        """Get state changes since iteration.
        
        Args:
            from_iteration: Starting iteration number
        
        Returns:
            Dictionary of changes
        """
        current = self.working_state
        
        new_observations = [
            obs for obs in current.observations
            if obs["iteration"] > from_iteration
        ]
        new_decisions = [
            dec for dec in current.decisions
            if dec["iteration"] > from_iteration
        ]
        new_results = [
            res for res in current.tool_results
            if res["iteration"] > from_iteration
        ]
        
        return {
            "from_iteration": from_iteration,
            "to_iteration": current.iteration,
            "new_observations": new_observations,
            "new_decisions": new_decisions,
            "new_tool_results": new_results,
        }
    
    def export_state(self, filepath: str) -> None:
        """Export current state to file."""
        with open(filepath, 'w') as f:
            json.dump(self.working_state.to_dict(), f, indent=2)
    
    def import_state(self, filepath: str) -> None:
        """Import state from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Basic restoration - you'd want more robust deserialization
        self.working_state.phase = ExecutionPhase(data["phase"])
        self.working_state.iteration = data["iteration"]
        self.working_state.last_error = data.get("last_error")
