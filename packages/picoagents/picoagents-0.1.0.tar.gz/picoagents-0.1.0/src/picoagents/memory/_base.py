"""
Abstract memory implementations for agent state persistence.

This module defines the memory interfaces and implementations that allow
agents to maintain context and learn from past interactions.
"""

import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class MemoryItem(BaseModel):
    """Individual memory item stored in agent memory."""
    
    content: str = Field(..., description="The memory content")
    timestamp: datetime = Field(default_factory=datetime.now, description="When memory was stored")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional memory metadata")
    importance: float = Field(default=1.0, description="Memory importance score (0.0-1.0)")
    
    class Config:
        frozen = True


class BaseMemory(ABC):
    """
    Abstract base class for agent memory implementations.
    
    Provides persistent storage and retrieval for agent context,
    enabling agents to maintain continuity across conversations.
    """
    
    def __init__(self, max_memories: int = 1000):
        """
        Initialize memory with maximum capacity.
        
        Args:
            max_memories: Maximum number of memories to retain
        """
        self.max_memories = max_memories
    
    @abstractmethod
    async def add(self, content: Union[str, Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Store new content in memory.
        
        Args:
            content: Content to store (text or structured data)
            metadata: Additional context about the memory
        """
        pass
    
    @abstractmethod
    async def query(self, query: str, limit: int = 10) -> List[str]:
        """
        Retrieve relevant memories based on query.
        
        Args:
            query: Search query for retrieving memories
            limit: Maximum number of memories to return
            
        Returns:
            List of relevant memory contents
        """
        pass
    
    @abstractmethod
    async def get_context(self, max_items: int = 10) -> List[str]:
        """
        Get recent/relevant context for LLM prompt.
        
        Args:
            max_items: Maximum number of context items
            
        Returns:
            List of context strings for LLM
        """
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Remove all stored memories."""
        pass
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Returns:
            Dictionary with memory usage statistics
        """
        return {
            "max_memories": self.max_memories,
            "implementation": self.__class__.__name__
        }


class ListMemory(BaseMemory):
    """
    Simple in-memory list storage for development and testing.
    
    Stores memories in a Python list with basic text search capabilities.
    This implementation does not persist between sessions.
    """
    
    def __init__(self, max_memories: int = 1000):
        super().__init__(max_memories)
        self.memories: List[MemoryItem] = []
    
    async def add(self, content: Union[str, Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> None:
        """Store new content in memory list."""
        if isinstance(content, dict):
            content_str = json.dumps(content)
        else:
            content_str = str(content)
        
        memory = MemoryItem(
            content=content_str,
            metadata=metadata or {}
        )
        
        self.memories.append(memory)
        
        # Remove oldest memories if we exceed capacity
        if len(self.memories) > self.max_memories:
            self.memories = self.memories[-self.max_memories:]
    
    async def query(self, query: str, limit: int = 10) -> List[str]:
        """Retrieve memories using simple text matching."""
        query_lower = query.lower()
        matching_memories = []
        
        for memory in reversed(self.memories):  # Most recent first
            if query_lower in memory.content.lower():
                matching_memories.append(memory.content)
                if len(matching_memories) >= limit:
                    break
        
        return matching_memories
    
    async def get_context(self, max_items: int = 10) -> List[str]:
        """Get most recent memories as context."""
        recent_memories = self.memories[-max_items:] if self.memories else []
        return [memory.content for memory in recent_memories]
    
    async def clear(self) -> None:
        """Clear all memories."""
        self.memories.clear()
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        base_stats = await super().get_stats()
        return {
            **base_stats,
            "current_memories": len(self.memories),
            "is_persistent": False
        }


class FileMemory(BaseMemory):
    """
    File-based persistent storage with text search.
    
    Stores memories in a JSON file for persistence between sessions.
    Provides basic text search capabilities.
    """
    
    def __init__(self, file_path: str, max_memories: int = 1000):
        super().__init__(max_memories)
        self.file_path = file_path
        self.memories: List[MemoryItem] = []
        self._load_memories()
    
    def _load_memories(self) -> None:
        """Load memories from file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    memories_data = json.load(f)
                    self.memories = [
                        MemoryItem(**memory_data) 
                        for memory_data in memories_data
                    ]
            except Exception:
                # If file is corrupted, start fresh
                self.memories = []
    
    def _save_memories(self) -> None:
        """Save memories to file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                memories_data = [memory.model_dump() for memory in self.memories]
                json.dump(memories_data, f, indent=2, default=str)
        except Exception:
            # Silently handle save errors to avoid breaking agent execution
            pass
    
    async def add(self, content: Union[str, Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> None:
        """Store new content in file memory."""
        if isinstance(content, dict):
            content_str = json.dumps(content)
        else:
            content_str = str(content)
        
        memory = MemoryItem(
            content=content_str,
            metadata=metadata or {}
        )
        
        self.memories.append(memory)
        
        # Remove oldest memories if we exceed capacity
        if len(self.memories) > self.max_memories:
            self.memories = self.memories[-self.max_memories:]
        
        self._save_memories()
    
    async def query(self, query: str, limit: int = 10) -> List[str]:
        """Retrieve memories using text matching."""
        query_lower = query.lower()
        matching_memories = []
        
        for memory in reversed(self.memories):  # Most recent first
            if query_lower in memory.content.lower():
                matching_memories.append(memory.content)
                if len(matching_memories) >= limit:
                    break
        
        return matching_memories
    
    async def get_context(self, max_items: int = 10) -> List[str]:
        """Get most recent memories as context."""
        recent_memories = self.memories[-max_items:] if self.memories else []
        return [memory.content for memory in recent_memories]
    
    async def clear(self) -> None:
        """Clear all memories and remove file."""
        self.memories.clear()
        if os.path.exists(self.file_path):
            try:
                os.remove(self.file_path)
            except Exception:
                pass
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        base_stats = await super().get_stats()
        return {
            **base_stats,
            "current_memories": len(self.memories),
            "file_path": self.file_path,
            "is_persistent": True
        }