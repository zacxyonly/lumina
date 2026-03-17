"""Permission and security system for Lumina.

This module implements a granular permission model for controlling
agent actions and tool execution.
"""

from enum import Enum
from typing import Set, Dict, Optional, List, Callable, Any
from dataclasses import dataclass, field
from pathlib import Path
import json


class PermissionLevel(Enum):
    """Permission levels for tool execution."""
    
    DENIED = "denied"              # Action blocked
    READ_ONLY = "read_only"        # Can read but not modify
    CONFIRM = "confirm"             # Requires user confirmation
    AUTO_SAFE = "auto_safe"        # Auto-run if marked safe
    AUTO_ALL = "auto_all"          # Full automation


class PermissionScope(Enum):
    """Permission scopes for different capabilities."""
    
    # File operations
    FILE_READ = "tool.file.read"
    FILE_WRITE = "tool.file.write"
    FILE_DELETE = "tool.file.delete"
    
    # Network operations
    WEB_BROWSE = "tool.web.browse"
    WEB_DOWNLOAD = "tool.web.download"
    HTTP_POST = "tool.http.post"
    
    # Communication
    EMAIL_READ = "tool.email.read"
    EMAIL_SEND = "tool.email.send"
    SLACK_READ = "tool.slack.read"
    SLACK_SEND = "tool.slack.send"
    
    # System operations
    SHELL_EXEC = "tool.shell.exec"
    PROCESS_SPAWN = "tool.process.spawn"
    ENV_READ = "tool.env.read"
    ENV_WRITE = "tool.env.write"
    
    # Data operations
    DB_READ = "tool.db.read"
    DB_WRITE = "tool.db.write"
    API_CALL = "tool.api.call"
    
    # Sensitive operations
    CREDENTIAL_READ = "tool.credential.read"
    CREDENTIAL_WRITE = "tool.credential.write"


@dataclass
class PermissionPolicy:
    """Permission policy for agent execution."""
    
    name: str
    description: str
    default_level: PermissionLevel = PermissionLevel.CONFIRM
    scopes: Dict[PermissionScope, PermissionLevel] = field(default_factory=dict)
    
    # Path restrictions
    allowed_read_paths: Set[Path] = field(default_factory=set)
    allowed_write_paths: Set[Path] = field(default_factory=set)
    
    # Network restrictions
    allowed_domains: Set[str] = field(default_factory=set)
    blocked_domains: Set[str] = field(default_factory=set)
    
    # Resource limits
    max_file_size_mb: int = 10
    max_network_calls_per_run: int = 50
    max_shell_commands_per_run: int = 10
    
    def check_permission(
        self,
        scope: PermissionScope,
        context: Optional[Dict[str, Any]] = None
    ) -> PermissionLevel:
        """Check permission for a scope with optional context.
        
        Args:
            scope: Permission scope to check
            context: Additional context (e.g., file path, domain)
        
        Returns:
            Permission level granted
        """
        # Get base permission
        level = self.scopes.get(scope, self.default_level)
        
        # Apply context-based restrictions
        if context:
            if scope == PermissionScope.FILE_READ:
                path = context.get("path")
                if path and not self._is_path_allowed(path, self.allowed_read_paths):
                    return PermissionLevel.DENIED
            
            elif scope == PermissionScope.FILE_WRITE:
                path = context.get("path")
                if path and not self._is_path_allowed(path, self.allowed_write_paths):
                    return PermissionLevel.DENIED
            
            elif scope in [PermissionScope.WEB_BROWSE, PermissionScope.HTTP_POST]:
                domain = context.get("domain")
                if domain:
                    if domain in self.blocked_domains:
                        return PermissionLevel.DENIED
                    if self.allowed_domains and domain not in self.allowed_domains:
                        return PermissionLevel.DENIED
        
        return level
    
    def _is_path_allowed(self, path: str, allowed_paths: Set[Path]) -> bool:
        """Check if path is within allowed directories."""
        if not allowed_paths:
            return True  # No restrictions
        
        path_obj = Path(path).resolve()
        for allowed in allowed_paths:
            try:
                path_obj.relative_to(allowed.resolve())
                return True
            except ValueError:
                continue
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize policy to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "default_level": self.default_level.value,
            "scopes": {
                scope.value: level.value
                for scope, level in self.scopes.items()
            },
            "allowed_read_paths": [str(p) for p in self.allowed_read_paths],
            "allowed_write_paths": [str(p) for p in self.allowed_write_paths],
            "allowed_domains": list(self.allowed_domains),
            "blocked_domains": list(self.blocked_domains),
            "max_file_size_mb": self.max_file_size_mb,
            "max_network_calls_per_run": self.max_network_calls_per_run,
            "max_shell_commands_per_run": self.max_shell_commands_per_run,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PermissionPolicy":
        """Deserialize policy from dictionary."""
        policy = cls(
            name=data["name"],
            description=data["description"],
            default_level=PermissionLevel(data.get("default_level", "confirm"))
        )
        
        # Parse scopes
        for scope_str, level_str in data.get("scopes", {}).items():
            try:
                scope = PermissionScope(scope_str)
                level = PermissionLevel(level_str)
                policy.scopes[scope] = level
            except ValueError:
                continue
        
        # Parse paths
        policy.allowed_read_paths = {
            Path(p) for p in data.get("allowed_read_paths", [])
        }
        policy.allowed_write_paths = {
            Path(p) for p in data.get("allowed_write_paths", [])
        }
        
        # Parse domains
        policy.allowed_domains = set(data.get("allowed_domains", []))
        policy.blocked_domains = set(data.get("blocked_domains", []))
        
        # Parse limits
        policy.max_file_size_mb = data.get("max_file_size_mb", 10)
        policy.max_network_calls_per_run = data.get("max_network_calls_per_run", 50)
        policy.max_shell_commands_per_run = data.get("max_shell_commands_per_run", 10)
        
        return policy
    
    def save(self, path: Path) -> None:
        """Save policy to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: Path) -> "PermissionPolicy":
        """Load policy from JSON file."""
        with open(path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


# Built-in policies

POLICY_OBSERVER = PermissionPolicy(
    name="observer",
    description="Read-only mode - no modifications allowed",
    default_level=PermissionLevel.DENIED,
    scopes={
        PermissionScope.FILE_READ: PermissionLevel.AUTO_SAFE,
        PermissionScope.WEB_BROWSE: PermissionLevel.AUTO_SAFE,
        PermissionScope.DB_READ: PermissionLevel.AUTO_SAFE,
        PermissionScope.EMAIL_READ: PermissionLevel.AUTO_SAFE,
        PermissionScope.SLACK_READ: PermissionLevel.AUTO_SAFE,
    }
)

POLICY_SAFE_AUTO = PermissionPolicy(
    name="safe_auto",
    description="Auto-run safe operations, confirm dangerous ones",
    default_level=PermissionLevel.CONFIRM,
    scopes={
        PermissionScope.FILE_READ: PermissionLevel.AUTO_SAFE,
        PermissionScope.WEB_BROWSE: PermissionLevel.AUTO_SAFE,
        PermissionScope.FILE_WRITE: PermissionLevel.CONFIRM,
        PermissionScope.FILE_DELETE: PermissionLevel.CONFIRM,
        PermissionScope.EMAIL_SEND: PermissionLevel.CONFIRM,
        PermissionScope.SHELL_EXEC: PermissionLevel.DENIED,
    }
)

POLICY_FULL_AUTO = PermissionPolicy(
    name="full_auto",
    description="Full automation - use with caution",
    default_level=PermissionLevel.AUTO_ALL,
    scopes={
        PermissionScope.SHELL_EXEC: PermissionLevel.CONFIRM,
        PermissionScope.CREDENTIAL_WRITE: PermissionLevel.DENIED,
    }
)

POLICY_STRICT = PermissionPolicy(
    name="strict",
    description="Confirm every action",
    default_level=PermissionLevel.CONFIRM
)


class PermissionManager:
    """Manage permissions and enforce policies."""
    
    def __init__(self, policy: Optional[PermissionPolicy] = None):
        self.policy = policy or POLICY_SAFE_AUTO
        self.run_stats = {
            "network_calls": 0,
            "shell_commands": 0,
            "files_written": 0,
        }
        self.confirmation_handler: Optional[Callable] = None
    
    def set_confirmation_handler(self, handler: Callable) -> None:
        """Set handler for confirmation requests.
        
        Args:
            handler: Async function(action, context) -> bool
        """
        self.confirmation_handler = handler
    
    async def check_and_request(
        self,
        scope: PermissionScope,
        action_description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Check permission and request confirmation if needed.
        
        Args:
            scope: Permission scope
            action_description: Human-readable action description
            context: Additional context
        
        Returns:
            True if action is allowed, False otherwise
        """
        level = self.policy.check_permission(scope, context)
        
        if level == PermissionLevel.DENIED:
            return False
        
        if level in [PermissionLevel.AUTO_SAFE, PermissionLevel.AUTO_ALL]:
            return True
        
        if level == PermissionLevel.CONFIRM:
            if self.confirmation_handler:
                return await self.confirmation_handler(action_description, context)
            # Default: deny if no handler
            return False
        
        return False
    
    def check_resource_limits(self, resource_type: str) -> bool:
        """Check if resource limits are exceeded.
        
        Args:
            resource_type: Type of resource (network_calls, shell_commands, etc.)
        
        Returns:
            True if within limits, False otherwise
        """
        if resource_type == "network_calls":
            return self.run_stats["network_calls"] < self.policy.max_network_calls_per_run
        elif resource_type == "shell_commands":
            return self.run_stats["shell_commands"] < self.policy.max_shell_commands_per_run
        return True
    
    def increment_resource_usage(self, resource_type: str) -> None:
        """Increment resource usage counter."""
        if resource_type in self.run_stats:
            self.run_stats[resource_type] += 1
    
    def reset_run_stats(self) -> None:
        """Reset per-run statistics."""
        self.run_stats = {
            "network_calls": 0,
            "shell_commands": 0,
            "files_written": 0,
        }
