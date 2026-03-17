"""
Lumina - Lightweight AI Agent Framework

A simple, powerful, and extensible autonomous AI agent system.
"""

__version__ = "1.0.0"
__author__ = "Mundai"
__license__ = "MIT"

from lumina.core.agent import Lumina
from lumina.core.llm import LLMProvider
from lumina.tools.base import Tool

__all__ = ["Lumina", "LLMProvider", "Tool"]
