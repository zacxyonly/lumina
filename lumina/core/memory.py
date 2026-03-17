"""Memory management system for Lumina."""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from lumina.core.llm import Message


@dataclass
class MemoryEntry:
    """Single memory entry."""
    timestamp: str
    content: str
    type: str  # conversation, fact, task, observation
    metadata: Dict[str, Any]
    importance: int = 5  # 1-10 scale
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        """Create from dictionary."""
        return cls(**data)


class Memory:
    """Memory management for agent."""
    
    def __init__(self, memory_dir: Path, max_short_term: int = 20):
        self.memory_dir = memory_dir
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_short_term = max_short_term
        
        # In-memory stores
        self.short_term: List[MemoryEntry] = []  # Recent conversation
        self.working: List[MemoryEntry] = []     # Current task context
        
        # File-based stores
        self.long_term_file = memory_dir / "long_term.json"
        self.conversations_file = memory_dir / "conversations.json"
        
        self._load_long_term()
    
    def _load_long_term(self) -> None:
        """Load long-term memory from disk."""
        if self.long_term_file.exists():
            with open(self.long_term_file, 'r') as f:
                self.long_term_data = json.load(f)
        else:
            self.long_term_data = {
                "facts": [],
                "learnings": [],
                "preferences": {}
            }
    
    def _save_long_term(self) -> None:
        """Save long-term memory to disk."""
        with open(self.long_term_file, 'w') as f:
            json.dump(self.long_term_data, f, indent=2)
    
    def add_short_term(self, content: str, type: str = "conversation", **metadata) -> None:
        """Add to short-term memory."""
        entry = MemoryEntry(
            timestamp=datetime.now().isoformat(),
            content=content,
            type=type,
            metadata=metadata
        )
        
        self.short_term.append(entry)
        
        # Trim if exceeds max
        if len(self.short_term) > self.max_short_term:
            # Move oldest to long-term if important
            old_entry = self.short_term.pop(0)
            if old_entry.importance >= 7:
                self._archive_to_long_term(old_entry)
    
    def add_working(self, content: str, **metadata) -> None:
        """Add to working memory (current task)."""
        entry = MemoryEntry(
            timestamp=datetime.now().isoformat(),
            content=content,
            type="task",
            metadata=metadata
        )
        self.working.append(entry)
    
    def clear_working(self) -> None:
        """Clear working memory."""
        self.working = []
    
    def add_fact(self, fact: str, category: str = "general") -> None:
        """Add fact to long-term memory."""
        self.long_term_data["facts"].append({
            "fact": fact,
            "category": category,
            "timestamp": datetime.now().isoformat()
        })
        self._save_long_term()
    
    def add_learning(self, learning: str, context: str = "") -> None:
        """Add learning to long-term memory."""
        self.long_term_data["learnings"].append({
            "learning": learning,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
        self._save_long_term()
    
    def set_preference(self, key: str, value: Any) -> None:
        """Set user preference."""
        self.long_term_data["preferences"][key] = value
        self._save_long_term()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference."""
        return self.long_term_data["preferences"].get(key, default)
    
    def _archive_to_long_term(self, entry: MemoryEntry) -> None:
        """Archive entry to long-term storage."""
        # Save to conversations file
        conversations = []
        if self.conversations_file.exists():
            with open(self.conversations_file, 'r') as f:
                conversations = json.load(f)
        
        conversations.append(entry.to_dict())
        
        with open(self.conversations_file, 'w') as f:
            json.dump(conversations, f, indent=2)
    
    def get_context_messages(self, max_messages: int = 10) -> List[Message]:
        """Get recent context as messages."""
        messages = []
        
        # Add recent short-term memory
        for entry in self.short_term[-max_messages:]:
            if entry.type == "conversation":
                role = entry.metadata.get("role", "user")
                messages.append(Message(role=role, content=entry.content))
        
        return messages
    
    def get_relevant_context(self, query: str, max_results: int = 5) -> List[str]:
        """Get relevant context for a query (simple keyword matching)."""
        relevant = []
        query_lower = query.lower()
        
        # Search short-term
        for entry in reversed(self.short_term):
            if any(word in entry.content.lower() for word in query_lower.split()):
                relevant.append(entry.content)
                if len(relevant) >= max_results:
                    return relevant
        
        # Search facts
        for fact in self.long_term_data["facts"]:
            if any(word in fact["fact"].lower() for word in query_lower.split()):
                relevant.append(fact["fact"])
                if len(relevant) >= max_results:
                    return relevant
        
        return relevant
    
    def save_conversation(self, messages: List[Message], session_id: str) -> None:
        """Save full conversation."""
        conversation = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "messages": [{"role": m.role, "content": m.content} for m in messages]
        }
        
        conversations = []
        if self.conversations_file.exists():
            with open(self.conversations_file, 'r') as f:
                conversations = json.load(f)
        
        conversations.append(conversation)
        
        with open(self.conversations_file, 'w') as f:
            json.dump(conversations, f, indent=2)
    
    def cleanup_old_memories(self, days: int = 30) -> None:
        """Remove memories older than specified days."""
        cutoff = datetime.now() - timedelta(days=days)
        
        if self.conversations_file.exists():
            with open(self.conversations_file, 'r') as f:
                conversations = json.load(f)
            
            filtered = [
                c for c in conversations
                if datetime.fromisoformat(c["timestamp"]) > cutoff
            ]
            
            with open(self.conversations_file, 'w') as f:
                json.dump(filtered, f, indent=2)
