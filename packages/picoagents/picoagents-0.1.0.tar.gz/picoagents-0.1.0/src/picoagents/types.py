"""
Core data types and models for the picoagents framework using Pydantic.

This module defines all the structured types used throughout the framework
for type safety and data validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from .messages import Message


class Usage(BaseModel):
    """Structured execution statistics and resource consumption."""
    
    duration_ms: int = Field(..., description="Total execution time in milliseconds")
    llm_calls: int = Field(default=0, description="Number of LLM API calls made")
    tokens_input: int = Field(default=0, description="Total input tokens consumed")
    tokens_output: int = Field(default=0, description="Total output tokens generated")
    tool_calls: int = Field(default=0, description="Number of tool executions")
    memory_operations: int = Field(default=0, description="Number of memory read/write operations")
    cost_estimate: Optional[float] = Field(default=None, description="Estimated cost in USD")
    
    def __add__(self, other: 'Usage') -> 'Usage':
        """Aggregate usage statistics from multiple sources."""
        return Usage(
            duration_ms=max(self.duration_ms, other.duration_ms),  # Max for parallel execution
            llm_calls=self.llm_calls + other.llm_calls,
            tokens_input=self.tokens_input + other.tokens_input,
            tokens_output=self.tokens_output + other.tokens_output,
            tool_calls=self.tool_calls + other.tool_calls,
            memory_operations=self.memory_operations + other.memory_operations,
            cost_estimate=(self.cost_estimate or 0) + (other.cost_estimate or 0) or None
        )
    
    class Config:
        frozen = True


class ToolResult(BaseModel):
    """Standardized tool execution result."""
    
    success: bool = Field(..., description="Whether tool execution succeeded")
    result: Any = Field(..., description="The actual result data")
    error: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution time, etc.")
    
    class Config:
        frozen = True


class AgentResponse(BaseModel):
    """Final result from agent.run() containing complete interaction sequence."""
    
    messages: List[Message] = Field(..., description="Complete sequence of LLM interactions")
    usage: Usage = Field(..., description="Execution statistics and resource consumption")
    source: str = Field(..., description="Source agent that generated this response")
    
    class Config:
        frozen = True

    @property
    def final_content(self) -> str:
        """Get the content of the last message, truncated for display."""
        if self.messages:
            content = self.messages[-1].content
            return content[:50] + "..." if len(content) > 50 else content
        return "No messages"

    def __str__(self) -> str:
        """Returns a user-friendly string representation with key metrics."""
        # Format duration
        duration_s = self.usage.duration_ms / 1000
        
        # Format tokens
        tokens_in = f"{self.usage.tokens_input/1000:.1f}k" if self.usage.tokens_input >= 1000 else str(self.usage.tokens_input)
        tokens_out = f"{self.usage.tokens_output/1000:.1f}k" if self.usage.tokens_output >= 1000 else str(self.usage.tokens_output)
        
        # Format cost if available
        cost_str = f", cost: ${self.usage.cost_estimate:.4f}" if self.usage.cost_estimate else ""
        
        return f"{self.source}: {self.final_content} | duration: {duration_s:.1f}s, tokens: in:{tokens_in}, out:{tokens_out}{cost_str}"

    def __repr__(self) -> str:
        """Returns an unambiguous, developer-friendly representation."""
        return f"AgentResponse(source='{self.source}', messages={len(self.messages)}, usage={self.usage})"


class ChatCompletionResult(BaseModel):
    """Standardized LLM response from BaseChatCompletionClient."""
    
    message: 'AssistantMessage' = Field(..., description="The LLM's response")
    usage: Usage = Field(..., description="Token consumption and timing metrics")
    model: str = Field(..., description="Actual model used for the request")
    finish_reason: str = Field(..., description="Completion status: stop, tool_calls, length, error")
    structured_output: Optional[BaseModel] = Field(default=None, description="Parsed structured output when output_format is specified")
    
    class Config:
        frozen = True


class ChatCompletionChunk(BaseModel):
    """Streaming response chunk from BaseChatCompletionClient."""
    
    content: str = Field(..., description="Partial text content from stream")
    is_complete: bool = Field(..., description="Whether this is the final chunk")
    tool_call_chunk: Optional[Dict[str, Any]] = Field(None, description="Partial tool call data")
    
    class Config:
        frozen = True


# Base event class for streaming
class BaseEvent(BaseModel):
    """Abstract base class for all agent events."""
    
    timestamp: datetime = Field(default_factory=datetime.now, description="When the event occurred")
    source: str = Field(..., description="Source of the event (agent name, system, orchestrator, etc.)")
    event_type: str = Field(..., description="Type of event")
    
    class Config:
        frozen = True

    def __str__(self) -> str:
        """Returns a user-friendly string representation."""
        time_str = self.timestamp.strftime("%H:%M:%S")
        return f"{self.source} event: {self.event_type} | {time_str}"

    def __repr__(self) -> str:
        """Returns an unambiguous, developer-friendly representation."""
        class_name = self.__class__.__name__
        return f"{class_name}(event_type='{self.event_type}', source='{self.source}', timestamp='{self.timestamp}')"


# Execution Events
class TaskStartEvent(BaseEvent):
    """Event emitted when task processing begins."""
    
    event_type: str = Field(default="task_start", description="Event type identifier")
    task: str = Field(..., description="The task being started")


class TaskCompleteEvent(BaseEvent):
    """Event emitted when task processing ends."""
    
    event_type: str = Field(default="task_complete", description="Event type identifier")
    result: str = Field(..., description="The final task result")


class ModelCallEvent(BaseEvent):
    """Event emitted when LLM API call is initiated."""
    
    event_type: str = Field(default="model_call", description="Event type identifier")
    input_messages: List[Message] = Field(..., description="Messages sent to the model")
    model: str = Field(..., description="Model being called")


class ModelResponseEvent(BaseEvent):
    """Event emitted when LLM response is received."""
    
    event_type: str = Field(default="model_response", description="Event type identifier")
    response: str = Field(..., description="The model's response")
    has_tool_calls: bool = Field(default=False, description="Whether response contains tool calls")


class ModelStreamChunkEvent(BaseEvent):
    """Event emitted for each streaming chunk from LLM."""
    
    event_type: str = Field(default="model_stream_chunk", description="Event type identifier")
    chunk: str = Field(..., description="Incremental text chunk")
    is_final: bool = Field(default=False, description="Whether this is the final chunk")


# Tool Events
class ToolCallEvent(BaseEvent):
    """Event emitted when tool execution begins."""
    
    event_type: str = Field(default="tool_call", description="Event type identifier")
    tool_name: str = Field(..., description="Name of the tool being called")
    parameters: Dict[str, Any] = Field(..., description="Parameters passed to the tool")
    call_id: str = Field(..., description="Unique identifier for this tool call")


class ToolCallResponseEvent(BaseEvent):
    """Event emitted when tool execution completes."""
    
    event_type: str = Field(default="tool_call_response", description="Event type identifier")
    call_id: str = Field(..., description="Unique identifier for this tool call")
    result: Optional[ToolResult] = Field(default=None, description="Tool execution result")


class ToolValidationEvent(BaseEvent):
    """Event emitted after parameter validation."""
    
    event_type: str = Field(default="tool_validation", description="Event type identifier")
    tool_name: str = Field(..., description="Name of the tool being validated")
    is_valid: bool = Field(..., description="Whether parameters are valid")
    errors: Optional[List[str]] = Field(None, description="Validation error messages")


# Memory Events
class MemoryUpdateEvent(BaseEvent):
    """Event emitted when memory state changes."""
    
    event_type: str = Field(default="memory_update", description="Event type identifier")
    operation: str = Field(..., description="Type of memory operation: add, update, delete")
    content_summary: str = Field(..., description="Summary of what was stored/updated")


class MemoryRetrievalEvent(BaseEvent):
    """Event emitted when memory content is accessed."""
    
    event_type: str = Field(default="memory_retrieval", description="Event type identifier")
    query: str = Field(..., description="Query used to retrieve memories")
    results_count: int = Field(..., description="Number of memories retrieved")


# Error Events
class ErrorEvent(BaseEvent):
    """Event emitted for recoverable errors."""
    
    event_type: str = Field(default="error", description="Event type identifier")
    error_message: str = Field(..., description="Description of the error")
    error_type: str = Field(..., description="Type/category of error")
    is_recoverable: bool = Field(default=True, description="Whether error can be recovered from")


class FatalErrorEvent(BaseEvent):
    """Event emitted for unrecoverable errors that terminate execution."""
    
    event_type: str = Field(default="fatal_error", description="Event type identifier")
    error_message: str = Field(..., description="Description of the fatal error")
    error_type: str = Field(..., description="Type/category of error")
    is_recoverable: bool = Field(default=False, description="Always false for fatal errors")


# Union type for all events
AgentEvent = Union[
    TaskStartEvent, TaskCompleteEvent, ModelCallEvent, ModelResponseEvent, ModelStreamChunkEvent,
    ToolCallEvent, ToolCallResponseEvent, ToolValidationEvent,
    MemoryUpdateEvent, MemoryRetrievalEvent,
    ErrorEvent, FatalErrorEvent
]


# Orchestration Types
class StopMessage(BaseModel):
    """Information about why orchestration stopped."""
    
    content: str = Field(..., description="Human-readable reason for stopping")
    source: str = Field(..., description="What caused the stop (termination condition name)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional stop details")
    
    class Config:
        frozen = True


class OrchestrationResponse(BaseModel):
    """Final result from orchestrator execution."""
    
    messages: List[Message] = Field(..., description="Complete conversation/execution history")
    final_result: str = Field(..., description="Summary result or final output")
    usage: Usage = Field(..., description="Aggregate resource consumption across all agents")
    stop_message: StopMessage = Field(..., description="Termination details")
    pattern_metadata: Dict[str, Any] = Field(default_factory=dict, description="Pattern-specific execution data")
    
    @property
    def truncated_result(self) -> str:
        """Get the final result, truncated for display."""
        if len(self.final_result) > 80:
            return self.final_result[:80] + "..."
        return self.final_result
    
    def __str__(self) -> str:
        """Returns a user-friendly string representation with key metrics."""
        # Format duration
        duration_s = self.usage.duration_ms / 1000
        
        # Format tokens
        tokens_in = f"{self.usage.tokens_input/1000:.1f}k" if self.usage.tokens_input >= 1000 else str(self.usage.tokens_input)
        tokens_out = f"{self.usage.tokens_output/1000:.1f}k" if self.usage.tokens_output >= 1000 else str(self.usage.tokens_output)
        
        # Format cost if available
        cost_str = f", cost: ${self.usage.cost_estimate:.4f}" if self.usage.cost_estimate else ""
        
        # Get pattern name from metadata
        pattern = self.pattern_metadata.get("pattern", "Unknown")
        
        return f"🏁 {pattern}: {self.truncated_result} | duration: {duration_s:.1f}s, tokens: in:{tokens_in}, out:{tokens_out}, calls: {self.usage.llm_calls} {cost_str}. Stop reason: {self.stop_message.content}"
    
    def __repr__(self) -> str:
        """Returns an unambiguous, developer-friendly representation."""
        pattern = self.pattern_metadata.get("pattern", "Unknown")
        iterations = self.pattern_metadata.get("iterations_completed", 0)
        return f"OrchestrationResponse(pattern='{pattern}', messages={len(self.messages)}, iterations={iterations}, usage={self.usage}, stop='{self.stop_message.source}')"
    
    class Config:
        frozen = True


# Orchestration Events for Streaming
class OrchestrationStartEvent(BaseEvent):
    """Event emitted when orchestration begins."""
    
    event_type: str = Field(default="orchestration_start", description="Event type identifier")
    task: str = Field(..., description="The task being orchestrated")
    pattern: str = Field(..., description="Orchestration pattern being used")


class OrchestrationCompleteEvent(BaseEvent):
    """Event emitted when orchestration ends."""
    
    event_type: str = Field(default="orchestration_complete", description="Event type identifier")
    result: str = Field(..., description="Final orchestration result")
    stop_reason: str = Field(..., description="Why orchestration stopped")


class AgentSelectionEvent(BaseEvent):
    """Event emitted when an agent is selected for execution."""
    
    event_type: str = Field(default="agent_selection", description="Event type identifier")
    selected_agent: str = Field(..., description="Name of selected agent")
    selection_reason: Optional[str] = Field(None, description="Why this agent was selected")


class AgentExecutionStartEvent(BaseEvent):
    """Event emitted when agent execution begins."""
    
    event_type: str = Field(default="agent_execution_start", description="Event type identifier")
    executing_agent: str = Field(..., description="Name of executing agent")
    context_size: int = Field(..., description="Number of messages in context")


class AgentExecutionCompleteEvent(BaseEvent):
    """Event emitted when agent execution completes."""
    
    event_type: str = Field(default="agent_execution_complete", description="Event type identifier")
    executing_agent: str = Field(..., description="Name of executed agent")
    success: bool = Field(..., description="Whether execution succeeded")
    message_count: int = Field(..., description="Number of messages produced")


# Union type for orchestration events
OrchestrationEvent = Union[
    OrchestrationStartEvent, OrchestrationCompleteEvent, AgentSelectionEvent,
    AgentExecutionStartEvent, AgentExecutionCompleteEvent
]


# Configuration Types
class AgentConfig(BaseModel):
    """Serializable agent configuration."""
    
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description for orchestrators")
    instructions: str = Field(..., description="Internal system prompt")
    model: str = Field(..., description="LLM model to use")
    max_iterations: int = Field(default=10, description="Maximum tool call iterations")
    timeout_seconds: int = Field(default=300, description="Maximum execution time")
    
    class Config:
        frozen = True


class ToolConfig(BaseModel):
    """Tool-specific settings and permissions."""
    
    name: str = Field(..., description="Tool name")
    enabled: bool = Field(default=True, description="Whether tool is enabled")
    timeout_seconds: int = Field(default=30, description="Tool execution timeout")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    permissions: Dict[str, Any] = Field(default_factory=dict, description="Tool-specific permissions")
    
    class Config:
        frozen = True


class MemoryConfig(BaseModel):
    """Memory backend and retention settings."""
    
    backend_type: str = Field(..., description="Memory backend: list, file, vector")
    max_memories: int = Field(default=1000, description="Maximum memories to retain")
    retention_days: int = Field(default=30, description="How long to keep memories")
    similarity_threshold: float = Field(default=0.7, description="Similarity threshold for retrieval")
    
    class Config:
        frozen = True


# Fix forward reference
from .messages import AssistantMessage
ChatCompletionResult.model_rebuild()