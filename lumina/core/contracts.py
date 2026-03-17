"""Enhanced tool system with strict contracts and validation.

Provides schema validation, retry policies, and safety guarantees
for tool execution.
"""

from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import time


class SideEffect(Enum):
    """Side effect classification for tools."""
    
    NONE = "none"              # Pure function, no side effects
    READ = "read"              # Reads external state
    WRITE = "write"            # Modifies external state
    DELETE = "delete"          # Deletes external data
    NETWORK = "network"        # Network communication
    DANGEROUS = "dangerous"    # Potentially harmful


@dataclass
class RetryPolicy:
    """Retry policy for tool execution."""
    
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0
    retry_on_timeout: bool = True
    retry_on_error: bool = True
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt."""
        delay = self.initial_delay * (self.exponential_base ** attempt)
        return min(delay, self.max_delay)


@dataclass
class ToolContract:
    """Contract specification for a tool.
    
    Defines strict input/output schemas, behavior guarantees,
    and operational requirements.
    """
    
    # Identity
    name: str
    description: str
    version: str = "1.0.0"
    
    # Schema definitions
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    
    # Behavior
    side_effects: SideEffect = SideEffect.NONE
    idempotent: bool = False
    deterministic: bool = True
    
    # Safety
    requires_confirmation: bool = False
    dangerous: bool = False
    
    # Execution
    timeout_seconds: float = 30.0
    retry_policy: Optional[RetryPolicy] = None
    
    # Permission scope
    permission_scope: Optional[str] = None
    
    # Fallback
    fallback_tool: Optional[str] = None
    
    # Documentation
    examples: list = field(default_factory=list)
    error_codes: Dict[str, str] = field(default_factory=dict)
    
    def validate_input(self, params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate input parameters against schema.
        
        Returns:
            (is_valid, error_message)
        """
        for param_name, param_spec in self.input_schema.items():
            # Check required parameters
            if param_spec.get("required", False) and param_name not in params:
                return False, f"Missing required parameter: {param_name}"
            
            # Type validation
            if param_name in params:
                expected_type = param_spec.get("type")
                actual_value = params[param_name]
                
                if not self._validate_type(actual_value, expected_type):
                    return False, f"Parameter '{param_name}' has invalid type. Expected {expected_type}"
                
                # Enum validation
                if "enum" in param_spec:
                    if actual_value not in param_spec["enum"]:
                        return False, f"Parameter '{param_name}' must be one of {param_spec['enum']}"
                
                # Range validation for numbers
                if expected_type in ["number", "integer"]:
                    if "minimum" in param_spec and actual_value < param_spec["minimum"]:
                        return False, f"Parameter '{param_name}' must be >= {param_spec['minimum']}"
                    if "maximum" in param_spec and actual_value > param_spec["maximum"]:
                        return False, f"Parameter '{param_name}' must be <= {param_spec['maximum']}"
                
                # Length validation for strings
                if expected_type == "string":
                    if "minLength" in param_spec and len(actual_value) < param_spec["minLength"]:
                        return False, f"Parameter '{param_name}' must be at least {param_spec['minLength']} characters"
                    if "maxLength" in param_spec and len(actual_value) > param_spec["maxLength"]:
                        return False, f"Parameter '{param_name}' must be at most {param_spec['maxLength']} characters"
        
        return True, None
    
    def validate_output(self, result: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate output against schema.
        
        Returns:
            (is_valid, error_message)
        """
        # Check required fields
        for field_name, field_spec in self.output_schema.items():
            if field_spec.get("required", False) and field_name not in result:
                return False, f"Missing required output field: {field_name}"
            
            # Type validation
            if field_name in result:
                expected_type = field_spec.get("type")
                actual_value = result[field_name]
                
                if not self._validate_type(actual_value, expected_type):
                    return False, f"Output field '{field_name}' has invalid type"
        
        return True, None
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value type."""
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        
        if expected_type not in type_map:
            return True  # Unknown type, skip validation
        
        expected = type_map[expected_type]
        return isinstance(value, expected)


class ToolExecutor:
    """Execute tools with contract enforcement and error handling."""
    
    def __init__(self):
        self.execution_stats: Dict[str, Dict[str, int]] = {}
    
    async def execute_with_contract(
        self,
        tool_func: Callable,
        contract: ToolContract,
        params: Dict[str, Any],
        confirmation_handler: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """Execute tool with full contract enforcement.
        
        Args:
            tool_func: Async function to execute
            contract: Tool contract
            params: Input parameters
            confirmation_handler: Optional confirmation callback
        
        Returns:
            Tool execution result
        """
        tool_name = contract.name
        
        # Initialize stats
        if tool_name not in self.execution_stats:
            self.execution_stats[tool_name] = {
                "total_calls": 0,
                "successful": 0,
                "failed": 0,
                "retries": 0,
            }
        
        stats = self.execution_stats[tool_name]
        stats["total_calls"] += 1
        
        # Validate input
        is_valid, error = contract.validate_input(params)
        if not is_valid:
            stats["failed"] += 1
            return {
                "status": "error",
                "error": f"Input validation failed: {error}",
                "error_code": "INVALID_INPUT"
            }
        
        # Check confirmation requirement
        if contract.requires_confirmation and confirmation_handler:
            action_desc = f"Execute {contract.name} with params: {params}"
            confirmed = await confirmation_handler(action_desc, {"contract": contract})
            if not confirmed:
                stats["failed"] += 1
                return {
                    "status": "error",
                    "error": "User denied confirmation",
                    "error_code": "CONFIRMATION_DENIED"
                }
        
        # Execute with retry policy
        retry_policy = contract.retry_policy or RetryPolicy(max_attempts=1)
        
        for attempt in range(retry_policy.max_attempts):
            try:
                # Execute with timeout
                result = await asyncio.wait_for(
                    tool_func(**params),
                    timeout=contract.timeout_seconds
                )
                
                # Validate output
                if isinstance(result, dict):
                    is_valid, error = contract.validate_output(result)
                    if not is_valid:
                        if attempt < retry_policy.max_attempts - 1:
                            stats["retries"] += 1
                            await asyncio.sleep(retry_policy.get_delay(attempt))
                            continue
                        
                        stats["failed"] += 1
                        return {
                            "status": "error",
                            "error": f"Output validation failed: {error}",
                            "error_code": "INVALID_OUTPUT"
                        }
                
                # Success
                stats["successful"] += 1
                return result
                
            except asyncio.TimeoutError:
                if attempt < retry_policy.max_attempts - 1 and retry_policy.retry_on_timeout:
                    stats["retries"] += 1
                    await asyncio.sleep(retry_policy.get_delay(attempt))
                    continue
                
                stats["failed"] += 1
                return {
                    "status": "error",
                    "error": f"Tool execution timeout after {contract.timeout_seconds}s",
                    "error_code": "TIMEOUT"
                }
                
            except Exception as e:
                if attempt < retry_policy.max_attempts - 1 and retry_policy.retry_on_error:
                    stats["retries"] += 1
                    await asyncio.sleep(retry_policy.get_delay(attempt))
                    continue
                
                stats["failed"] += 1
                return {
                    "status": "error",
                    "error": str(e),
                    "error_code": "EXECUTION_ERROR"
                }
        
        # Should not reach here
        stats["failed"] += 1
        return {
            "status": "error",
            "error": "Max retry attempts exceeded",
            "error_code": "MAX_RETRIES"
        }
    
    def get_stats(self, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """Get execution statistics.
        
        Args:
            tool_name: Specific tool name, or None for all tools
        
        Returns:
            Statistics dictionary
        """
        if tool_name:
            return self.execution_stats.get(tool_name, {})
        return self.execution_stats


# Example contract definitions

FILE_READ_CONTRACT = ToolContract(
    name="read_file",
    description="Read contents of a file",
    input_schema={
        "path": {
            "type": "string",
            "required": True,
            "description": "File path to read",
            "minLength": 1,
            "maxLength": 1000,
        }
    },
    output_schema={
        "status": {"type": "string", "required": True},
        "content": {"type": "string", "required": False},
        "size": {"type": "integer", "required": False},
    },
    side_effects=SideEffect.READ,
    idempotent=True,
    deterministic=True,
    timeout_seconds=10.0,
    retry_policy=RetryPolicy(max_attempts=2),
    permission_scope="tool.file.read",
)

FILE_WRITE_CONTRACT = ToolContract(
    name="write_file",
    description="Write content to a file",
    input_schema={
        "path": {
            "type": "string",
            "required": True,
            "description": "File path to write",
        },
        "content": {
            "type": "string",
            "required": True,
            "description": "Content to write",
        },
        "mode": {
            "type": "string",
            "required": False,
            "enum": ["write", "append"],
            "description": "Write mode",
        }
    },
    output_schema={
        "status": {"type": "string", "required": True},
        "bytes_written": {"type": "integer", "required": False},
    },
    side_effects=SideEffect.WRITE,
    idempotent=False,
    requires_confirmation=True,
    dangerous=True,
    timeout_seconds=30.0,
    retry_policy=RetryPolicy(max_attempts=1),  # Don't retry writes
    permission_scope="tool.file.write",
)
