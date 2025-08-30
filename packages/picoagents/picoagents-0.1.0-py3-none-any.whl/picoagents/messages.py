"""
Core message types for agent communication using Pydantic models.

This module defines the structured message types that agents use to communicate
with each other and with LLMs, following the OpenAI API format.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field


class BaseMessage(BaseModel):
    """Base class for all message types."""
    
    content: str = Field(..., description="The message content")
    source: str = Field(..., description="Source of the message (agent name, system, user, etc.)")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the message was created")
    
    class Config:
        frozen = True

    def __str__(self) -> str:
        """Returns a user-friendly string representation."""
        time_str = self.timestamp.strftime("%H:%M:%S")
        return f"{self.source}: {self.content} | {time_str}"

    def __repr__(self) -> str:
        """Returns an unambiguous, developer-friendly representation."""
        class_name = self.__class__.__name__
        return f"{class_name}(source='{self.source}', content='{self.content[:50]}...', timestamp='{self.timestamp}')"


class SystemMessage(BaseMessage):
    """System message containing instructions/role definition for the agent."""
    
    role: Literal["system"] = Field(default="system", description="Message role")


class UserMessage(BaseMessage):
    """User message containing input from human or external system."""
    
    role: Literal["user"] = Field(default="user", description="Message role")
    name: Optional[str] = Field(default=None, description="Optional name of the user")


class ToolCallRequest(BaseModel):
    """Structured representation of an LLM's tool call request."""
    
    tool_name: str = Field(..., description="Name of the tool to call")
    parameters: Dict[str, Any] = Field(..., description="Arguments for the tool")
    call_id: str = Field(..., description="Unique identifier for this call")
    
    class Config:
        frozen = True


class AssistantMessage(BaseMessage):
    """Assistant message containing response from the agent/LLM."""
    
    role: Literal["assistant"] = Field(default="assistant", description="Message role")
    tool_calls: Optional[List[ToolCallRequest]] = Field(default=None, description="Tool calls made by the assistant")
    structured_content: Optional[BaseModel] = Field(default=None, description="Structured data when output_format is used")


class ToolMessage(BaseMessage):
    """Tool message containing result from tool execution."""
    
    role: Literal["tool"] = Field(default="tool", description="Message role")
    tool_call_id: str = Field(..., description="ID of the tool call this is responding to")
    tool_name: str = Field(..., description="Name of the tool that was executed")
    success: bool = Field(..., description="Whether tool execution succeeded")
    error: Optional[str] = Field(None, description="Error message if failed")


class MultiModalMessage(BaseMessage):
    """Message supporting multiple content types (text, images, audio, etc.)."""
    
    role: Literal["user", "assistant"] = Field(..., description="Message role")
    content_type: Literal["text", "image", "audio", "video"] = Field(default="text", description="Type of content")
    media_url: Optional[str] = Field(None, description="URL to media content if applicable")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional content metadata")


# Union type for all message types
Message = Union[SystemMessage, UserMessage, AssistantMessage, ToolMessage, MultiModalMessage]