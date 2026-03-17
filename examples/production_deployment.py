"""Production deployment example for Lumina.

Demonstrates how to deploy Lumina with proper security,
monitoring, and error handling for production use.
"""

import asyncio
from pathlib import Path
from typing import Optional
from lumina import Lumina
from lumina.core.permissions import (
    PermissionPolicy,
    PermissionLevel,
    PermissionScope,
    PermissionManager,
)
from lumina.core.audit import AuditLogger
from lumina.core.evaluator import Evaluator
from lumina.utils.config import LuminaConfig


async def confirmation_handler(action: str, context: dict) -> bool:
    """Production confirmation handler with logging."""
    print(f"\n{'='*60}")
    print(f"⚠️  CONFIRMATION REQUIRED")
    print(f"{'='*60}")
    print(f"Action: {action}")
    
    if "contract" in context:
        contract = context["contract"]
        print(f"Tool: {contract.name}")
        print(f"Dangerous: {contract.dangerous}")
        print(f"Side Effects: {contract.side_effects.value}")
    
    print(f"{'='*60}\n")
    
    # In production, this would:
    # - Log to audit system
    # - Send notification to admin
    # - Wait for approval via API/webhook
    # - Enforce approval timeout
    
    response = input("Approve? (yes/no): ")
    approved = response.lower() in ['yes', 'y']
    
    # Log decision
    print(f"\n{'APPROVED' if approved else 'DENIED'}\n")
    
    return approved


def create_production_policy() -> PermissionPolicy:
    """Create production permission policy."""
    policy = PermissionPolicy(
        name="production",
        description="Production policy with safety controls",
        default_level=PermissionLevel.CONFIRM,
    )
    
    # Safe operations can auto-run
    policy.scopes = {
        PermissionScope.FILE_READ: PermissionLevel.AUTO_SAFE,
        PermissionScope.WEB_BROWSE: PermissionLevel.AUTO_SAFE,
        PermissionScope.DB_READ: PermissionLevel.AUTO_SAFE,
        
        # Writing requires confirmation
        PermissionScope.FILE_WRITE: PermissionLevel.CONFIRM,
        PermissionScope.FILE_DELETE: PermissionLevel.CONFIRM,
        PermissionScope.DB_WRITE: PermissionLevel.CONFIRM,
        
        # Dangerous operations denied
        PermissionScope.SHELL_EXEC: PermissionLevel.DENIED,
        PermissionScope.CREDENTIAL_WRITE: PermissionLevel.DENIED,
    }
    
    # Path restrictions
    policy.allowed_write_paths = {
        Path("./output"),
        Path("./reports"),
        Path("./temp"),
    }
    
    # Network restrictions
    policy.allowed_domains = {
        "api.openai.com",
        "api.anthropic.com",
        "trusted-service.com",
    }
    
    policy.blocked_domains = {
        "malicious.com",
        "untrusted.net",
    }
    
    # Resource limits
    policy.max_file_size_mb = 50
    policy.max_network_calls_per_run = 100
    policy.max_shell_commands_per_run = 0  # Disabled
    
    return policy


async def run_with_monitoring(
    agent: Lumina,
    task: str,
    max_cost: float = 1.0,
) -> Optional[str]:
    """Run task with cost monitoring and safety checks."""
    
    print(f"\n{'='*60}")
    print(f"🚀 STARTING TASK")
    print(f"{'='*60}")
    print(f"Task: {task}")
    print(f"Max Cost: ${max_cost:.2f}")
    print(f"Policy: {agent.permission_manager.policy.name}")
    print(f"{'='*60}\n")
    
    try:
        # Run task
        result = await agent.run(task)
        
        # Get trace
        trace = agent.audit_logger.load_trace(agent.session_id)
        
        print(f"\n{'='*60}")
        print(f"✅ TASK COMPLETED")
        print(f"{'='*60}")
        print(f"Success: {trace.success}")
        print(f"Iterations: {trace.total_iterations}")
        print(f"Tool Calls: {trace.total_tool_calls}")
        print(f"Tokens: {trace.total_tokens}")
        print(f"Cost: ${trace.total_cost:.4f}")
        print(f"Duration: {trace.duration_seconds:.2f}s")
        print(f"{'='*60}\n")
        
        # Cost check
        if trace.total_cost > max_cost:
            print(f"⚠️  WARNING: Cost exceeded budget (${trace.total_cost:.4f} > ${max_cost:.2f})")
        
        return result
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ TASK FAILED")
        print(f"{'='*60}")
        print(f"Error: {str(e)}")
        print(f"{'='*60}\n")
        
        # Log to monitoring system
        # send_to_monitoring_system(error=str(e), task=task)
        
        return None


async def run_evaluation(agent: Lumina) -> None:
    """Run evaluation suite before production deployment."""
    
    print(f"\n{'='*60}")
    print(f"🧪 RUNNING EVALUATION SUITE")
    print(f"{'='*60}\n")
    
    evaluator = Evaluator(
        eval_dir=Path("./evaluations"),
        version="1.0.0"
    )
    
    # Run benchmark
    report = await evaluator.run_benchmark(agent)
    
    print(f"\n{'='*60}")
    print(f"📊 EVALUATION REPORT")
    print(f"{'='*60}")
    print(f"Tasks Run: {report.total_tasks}")
    print(f"Success Rate: {report.task_success_rate:.1f}%")
    print(f"Avg Iterations: {report.avg_iterations:.1f}")
    print(f"Avg Tokens: {report.avg_tokens:.0f}")
    print(f"Tool Accuracy: {report.tool_accuracy_rate:.1f}%")
    print(f"Error Recovery: {report.error_recovery_rate:.1f}%")
    print(f"Total Cost: ${report.total_cost:.4f}")
    print(f"{'='*60}\n")
    
    # Deployment gate
    if report.task_success_rate < 80:
        raise ValueError(
            f"Success rate too low for production: {report.task_success_rate:.1f}%"
        )
    
    if report.tool_accuracy_rate < 90:
        raise ValueError(
            f"Tool accuracy too low: {report.tool_accuracy_rate:.1f}%"
        )
    
    print("✅ Evaluation passed - safe for production\n")


async def main():
    """Production deployment example."""
    
    # Configuration
    config = LuminaConfig(
        provider="openai",
        model="gpt-4-turbo-preview",
        temperature=0.3,  # Lower for more deterministic
        max_iterations=15,
        verbose=True,
        debug=False,  # Disable in production
    )
    
    # Create production policy
    policy = create_production_policy()
    
    # Initialize audit logger
    audit_logger = AuditLogger(log_dir=Path("./production_logs"))
    
    # Create agent
    agent = Lumina(
        config=config,
        enable_memory=True,
    )
    
    # Set permission policy
    agent.permission_manager = PermissionManager(policy)
    agent.permission_manager.set_confirmation_handler(confirmation_handler)
    
    # Set audit logger
    agent.audit_logger = audit_logger
    
    # Run evaluation before production use
    await run_evaluation(agent)
    
    # Example production tasks
    tasks = [
        "Analyze the current directory structure and create a report",
        "List all Python files and count lines of code",
        "Search for TODO comments in the codebase",
    ]
    
    for task in tasks:
        result = await run_with_monitoring(
            agent=agent,
            task=task,
            max_cost=0.50  # $0.50 budget per task
        )
        
        if result:
            print(f"Result preview: {result[:200]}...\n")
        
        # Reset agent between tasks
        agent.reset()
    
    # Generate summary report
    print(f"\n{'='*60}")
    print(f"📋 SESSION SUMMARY")
    print(f"{'='*60}")
    
    traces = audit_logger.list_traces(limit=10)
    total_cost = sum(
        audit_logger.load_trace(t["run_id"]).total_cost
        for t in traces
    )
    
    print(f"Total Tasks: {len(traces)}")
    print(f"Total Cost: ${total_cost:.4f}")
    print(f"Average Cost: ${total_cost/len(traces):.4f}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
