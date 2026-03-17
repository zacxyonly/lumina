"""Structured logging system for Lumina."""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme


# Custom theme for Lumina
LUMINA_THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "agent": "bold magenta",
    "tool": "bold blue",
    "thinking": "dim cyan italic",
})

console = Console(theme=LUMINA_THEME)


class LuminaLogger:
    """Custom logger for Lumina with rich formatting."""
    
    def __init__(
        self,
        name: str = "lumina",
        level: int = logging.INFO,
        log_file: Optional[Path] = None,
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers.clear()
        
        # Rich console handler
        console_handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            markup=True,
        )
        console_handler.setLevel(level)
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def info(self, msg: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(msg, extra=kwargs)
    
    def warning(self, msg: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(msg, extra=kwargs)
    
    def error(self, msg: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(msg, extra=kwargs)
    
    def debug(self, msg: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(msg, extra=kwargs)
    
    def success(self, msg: str) -> None:
        """Log success message."""
        console.print(f"✓ {msg}", style="success")
    
    def agent_action(self, action: str, detail: str = "") -> None:
        """Log agent action."""
        msg = f"🤖 Agent: {action}"
        if detail:
            msg += f" - {detail}"
        console.print(msg, style="agent")
    
    def tool_call(self, tool: str, params: str = "") -> None:
        """Log tool call."""
        msg = f"🔧 Tool: {tool}"
        if params:
            msg += f" ({params})"
        console.print(msg, style="tool")
    
    def thinking(self, msg: str) -> None:
        """Log thinking process."""
        console.print(f"💭 {msg}", style="thinking")


# Global logger instance
_logger: Optional[LuminaLogger] = None


def get_logger(
    name: str = "lumina",
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
) -> LuminaLogger:
    """Get or create global logger instance."""
    global _logger
    if _logger is None:
        _logger = LuminaLogger(name, level, log_file)
    return _logger


def setup_logging(verbose: bool = False, log_file: Optional[Path] = None) -> LuminaLogger:
    """Setup logging with specified verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    return get_logger(level=level, log_file=log_file)
