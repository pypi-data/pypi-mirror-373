"""
Picoagents Framework

A lightweight, type-safe framework for building AI agents with LLMs.
Supports tool calling, memory, streaming, and multi-agent orchestration.
"""

# Core message types
from .messages import (
    Message,
    SystemMessage,
    UserMessage,
    AssistantMessage,
    ToolMessage,
    MultiModalMessage,
    ToolCallRequest
)

# Core data types
from .types import (
    Usage,
    ToolResult,
    AgentResponse,
    ChatCompletionResult,
    ChatCompletionChunk,
    AgentEvent,
    AgentConfig,
    ToolConfig,
    MemoryConfig,
    StopMessage,
    OrchestrationResponse,
    OrchestrationEvent
)

# Cancellation support
from ._cancellation_token import CancellationToken

# Agent implementations
from .agents import (
    BaseAgent,
    Agent,
    AgentError,
    AgentExecutionError,
    AgentConfigurationError,
    AgentToolError
)

# Tool system
from .tools import (
    BaseTool,
    FunctionTool
)

# Memory system
from .memory import (
    BaseMemory,
    MemoryItem,
    ListMemory,
    FileMemory
)

# LLM clients
from .llm import (
    BaseChatCompletionClient,
    BaseChatCompletionError,
    RateLimitError,
    AuthenticationError,
    InvalidRequestError,
    OpenAIChatCompletionClient
)

# Orchestration patterns
from .orchestration import (
    BaseOrchestrator,
    RoundRobinOrchestrator,
    BaseTermination,
    MaxMessageTermination,
    TextMentionTermination,
    TokenUsageTermination,
    TimeoutTermination,
    HandoffTermination,
    ExternalTermination,
    CancellationTermination,
    FunctionCallTermination,
    CompositeTermination
)

__version__ = "0.1.0"

__all__ = [
    # Messages
    "Message",
    "SystemMessage", 
    "UserMessage",
    "AssistantMessage",
    "ToolMessage",
    "MultiModalMessage",
    "ToolCallRequest",
    
    # Types
    "Usage",
    "ToolResult",
    "AgentResponse",
    "ChatCompletionResult",
    "ChatCompletionChunk", 
    "AgentEvent",
    "AgentConfig",
    "ToolConfig",
    "MemoryConfig",
    "StopMessage",
    "OrchestrationResponse",
    "OrchestrationEvent",
    
    # Cancellation
    "CancellationToken",
    
    # Agents
    "BaseAgent",
    "Agent",
    "AgentError",
    "AgentExecutionError",
    "AgentConfigurationError",
    "AgentToolError",
    
    # Tools
    "BaseTool",
    "FunctionTool",
    
    # Memory
    "BaseMemory",
    "MemoryItem",
    "ListMemory", 
    "FileMemory",
    
    # LLM
    "BaseChatCompletionClient",
    "BaseChatCompletionError",
    "RateLimitError",
    "AuthenticationError",
    "InvalidRequestError",
    "OpenAIChatCompletionClient",
    
    # Orchestration
    "BaseOrchestrator",
    "RoundRobinOrchestrator",
    "BaseTermination",
    "MaxMessageTermination",
    "TextMentionTermination",
    "TokenUsageTermination",
    "TimeoutTermination",
    "HandoffTermination",
    "ExternalTermination",
    "CancellationTermination",
    "FunctionCallTermination",
    "CompositeTermination",
]
