"""Evaluation system for Lumina agent framework.

Provides internal benchmarking and quality metrics
to track framework performance over time.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import json
import statistics


@dataclass
class EvaluationTask:
    """Single evaluation task."""
    
    task_id: str
    description: str
    expected_outcome: str
    category: str = "general"
    difficulty: str = "medium"  # easy, medium, hard
    
    # Success criteria
    required_tools: List[str] = field(default_factory=list)
    max_iterations: int = 10
    max_tokens: int = 5000
    
    # Metadata
    tags: List[str] = field(default_factory=list)


@dataclass
class EvaluationResult:
    """Result of running evaluation task."""
    
    task_id: str
    timestamp: str
    
    # Execution metrics
    success: bool
    iterations_used: int
    tokens_used: int
    tools_called: int
    duration_seconds: float
    cost_usd: float = 0.0
    
    # Quality metrics
    correct_tool_selection: bool = True
    error_recovery_count: int = 0
    hallucination_detected: bool = False
    unsafe_action_blocked: int = 0
    
    # Output
    final_answer: str = ""
    error_message: Optional[str] = None
    
    # Trace reference
    trace_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "timestamp": self.timestamp,
            "success": self.success,
            "iterations_used": self.iterations_used,
            "tokens_used": self.tokens_used,
            "tools_called": self.tools_called,
            "duration_seconds": self.duration_seconds,
            "cost_usd": self.cost_usd,
            "correct_tool_selection": self.correct_tool_selection,
            "error_recovery_count": self.error_recovery_count,
            "hallucination_detected": self.hallucination_detected,
            "unsafe_action_blocked": self.unsafe_action_blocked,
            "final_answer": self.final_answer[:200],  # Truncate
            "error_message": self.error_message,
            "trace_id": self.trace_id,
        }


@dataclass
class BenchmarkReport:
    """Aggregate benchmark report."""
    
    run_id: str
    timestamp: str
    version: str
    
    # Task results
    results: List[EvaluationResult] = field(default_factory=list)
    
    # Aggregate metrics
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    
    # Performance metrics
    avg_iterations: float = 0.0
    avg_tokens: float = 0.0
    avg_duration: float = 0.0
    total_cost: float = 0.0
    
    # Quality metrics
    task_success_rate: float = 0.0
    tool_accuracy_rate: float = 0.0
    error_recovery_rate: float = 0.0
    safety_block_rate: float = 0.0
    
    def calculate_metrics(self) -> None:
        """Calculate aggregate metrics from results."""
        if not self.results:
            return
        
        self.total_tasks = len(self.results)
        self.successful_tasks = sum(1 for r in self.results if r.success)
        self.failed_tasks = self.total_tasks - self.successful_tasks
        
        # Success rate
        self.task_success_rate = (self.successful_tasks / self.total_tasks) * 100
        
        # Average metrics (only for successful tasks)
        successful = [r for r in self.results if r.success]
        if successful:
            self.avg_iterations = statistics.mean(r.iterations_used for r in successful)
            self.avg_tokens = statistics.mean(r.tokens_used for r in successful)
            self.avg_duration = statistics.mean(r.duration_seconds for r in successful)
            self.total_cost = sum(r.cost_usd for r in successful)
        
        # Tool accuracy
        correct_tools = sum(1 for r in self.results if r.correct_tool_selection)
        self.tool_accuracy_rate = (correct_tools / self.total_tasks) * 100
        
        # Error recovery (tasks that recovered from errors)
        recovered = sum(1 for r in self.results if r.error_recovery_count > 0 and r.success)
        had_errors = sum(1 for r in self.results if r.error_recovery_count > 0)
        self.error_recovery_rate = (recovered / had_errors * 100) if had_errors > 0 else 100.0
        
        # Safety blocks
        total_blocks = sum(r.unsafe_action_blocked for r in self.results)
        self.safety_block_rate = total_blocks / self.total_tasks if self.total_tasks > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "version": self.version,
            "summary": {
                "total_tasks": self.total_tasks,
                "successful": self.successful_tasks,
                "failed": self.failed_tasks,
                "success_rate": f"{self.task_success_rate:.1f}%",
            },
            "performance": {
                "avg_iterations": round(self.avg_iterations, 2),
                "avg_tokens": round(self.avg_tokens, 0),
                "avg_duration_seconds": round(self.avg_duration, 2),
                "total_cost_usd": round(self.total_cost, 4),
            },
            "quality": {
                "tool_accuracy_rate": f"{self.tool_accuracy_rate:.1f}%",
                "error_recovery_rate": f"{self.error_recovery_rate:.1f}%",
                "safety_blocks_per_task": round(self.safety_block_rate, 2),
            },
            "results": [r.to_dict() for r in self.results]
        }


class Evaluator:
    """Evaluation system for agent performance."""
    
    def __init__(self, eval_dir: Path, version: str = "1.0.0"):
        self.eval_dir = eval_dir
        self.version = version
        self.eval_dir.mkdir(parents=True, exist_ok=True)
        
        # Load task suite
        self.tasks: Dict[str, EvaluationTask] = {}
        self._load_default_tasks()
    
    def _load_default_tasks(self) -> None:
        """Load default evaluation tasks."""
        # File operations
        self.add_task(EvaluationTask(
            task_id="file_read_basic",
            description="Read a text file and summarize its contents",
            expected_outcome="File contents read and summarized",
            category="file_ops",
            difficulty="easy",
            required_tools=["read_file"],
            max_iterations=3,
        ))
        
        self.add_task(EvaluationTask(
            task_id="file_write_basic",
            description="Create a new file with specific content",
            expected_outcome="File created with correct content",
            category="file_ops",
            difficulty="easy",
            required_tools=["write_file"],
            max_iterations=3,
        ))
        
        # Multi-step tasks
        self.add_task(EvaluationTask(
            task_id="file_search_and_modify",
            description="Find all Python files and add docstrings to those missing them",
            expected_outcome="Python files identified and modified",
            category="multi_step",
            difficulty="hard",
            required_tools=["search_files", "read_file", "write_file"],
            max_iterations=15,
        ))
        
        # Error recovery
        self.add_task(EvaluationTask(
            task_id="recover_from_missing_file",
            description="Read a file, if it doesn't exist, create it with default content",
            expected_outcome="File read or created appropriately",
            category="error_handling",
            difficulty="medium",
            required_tools=["read_file", "write_file"],
            max_iterations=5,
        ))
        
        # Planning tasks
        self.add_task(EvaluationTask(
            task_id="organize_project_structure",
            description="Analyze directory and suggest project structure improvements",
            expected_outcome="Analysis complete with actionable suggestions",
            category="planning",
            difficulty="medium",
            required_tools=["list_directory"],
            max_iterations=8,
        ))
    
    def add_task(self, task: EvaluationTask) -> None:
        """Add evaluation task to suite."""
        self.tasks[task.task_id] = task
    
    def load_tasks_from_file(self, filepath: Path) -> None:
        """Load tasks from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        for task_data in data.get("tasks", []):
            task = EvaluationTask(**task_data)
            self.add_task(task)
    
    async def evaluate_task(
        self,
        agent,
        task_id: str,
    ) -> EvaluationResult:
        """Evaluate agent on a single task.
        
        Args:
            agent: Lumina agent instance
            task_id: Task identifier
        
        Returns:
            Evaluation result
        """
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        start_time = datetime.now()
        
        try:
            # Reset agent
            agent.reset()
            
            # Run task
            result = await agent.run(
                task=task.description,
                max_iterations=task.max_iterations
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Create evaluation result
            eval_result = EvaluationResult(
                task_id=task_id,
                timestamp=datetime.now().isoformat(),
                success=True,  # Heuristic: task completed without critical error
                iterations_used=agent.iteration_count,
                tokens_used=0,  # Would need to track from agent
                tools_called=len([e for e in agent.messages if hasattr(e, 'tool_calls') and e.tool_calls]),
                duration_seconds=duration,
                final_answer=result[:500],
                trace_id=agent.session_id,
            )
            
            return eval_result
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            
            return EvaluationResult(
                task_id=task_id,
                timestamp=datetime.now().isoformat(),
                success=False,
                iterations_used=agent.iteration_count if hasattr(agent, 'iteration_count') else 0,
                tokens_used=0,
                tools_called=0,
                duration_seconds=duration,
                error_message=str(e),
            )
    
    async def run_benchmark(
        self,
        agent,
        task_ids: Optional[List[str]] = None,
    ) -> BenchmarkReport:
        """Run full benchmark suite.
        
        Args:
            agent: Lumina agent instance
            task_ids: Specific tasks to run (None = all tasks)
        
        Returns:
            Benchmark report
        """
        import uuid
        
        run_id = str(uuid.uuid4())[:8]
        report = BenchmarkReport(
            run_id=run_id,
            timestamp=datetime.now().isoformat(),
            version=self.version,
        )
        
        # Determine tasks to run
        tasks_to_run = task_ids or list(self.tasks.keys())
        
        # Run each task
        for task_id in tasks_to_run:
            print(f"Evaluating task: {task_id}")
            result = await self.evaluate_task(agent, task_id)
            report.results.append(result)
        
        # Calculate metrics
        report.calculate_metrics()
        
        # Save report
        self.save_report(report)
        
        return report
    
    def save_report(self, report: BenchmarkReport) -> None:
        """Save benchmark report."""
        filename = f"benchmark_{report.run_id}_{report.timestamp[:10]}.json"
        filepath = self.eval_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
    
    def load_report(self, run_id: str) -> Optional[BenchmarkReport]:
        """Load benchmark report by run ID."""
        for filepath in self.eval_dir.glob(f"benchmark_{run_id}_*.json"):
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            report = BenchmarkReport(
                run_id=data["run_id"],
                timestamp=data["timestamp"],
                version=data["version"],
            )
            
            # Restore results
            for result_data in data.get("results", []):
                result = EvaluationResult(**result_data)
                report.results.append(result)
            
            report.calculate_metrics()
            return report
        
        return None
    
    def compare_reports(
        self,
        baseline_id: str,
        current_id: str
    ) -> Dict[str, Any]:
        """Compare two benchmark reports.
        
        Returns:
            Comparison dictionary with deltas
        """
        baseline = self.load_report(baseline_id)
        current = self.load_report(current_id)
        
        if not baseline or not current:
            raise ValueError("One or both reports not found")
        
        return {
            "baseline": baseline_id,
            "current": current_id,
            "success_rate_delta": current.task_success_rate - baseline.task_success_rate,
            "avg_iterations_delta": current.avg_iterations - baseline.avg_iterations,
            "avg_tokens_delta": current.avg_tokens - baseline.avg_tokens,
            "cost_delta": current.total_cost - baseline.total_cost,
            "tool_accuracy_delta": current.tool_accuracy_rate - baseline.tool_accuracy_rate,
        }
