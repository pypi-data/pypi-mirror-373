"""
Base agent implementation following the stub.md specification.

This module provides the core BaseAgent class that all agents must inherit from,
implementing the interface specified in stub.md with proper typing and functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Callable, Type, TYPE_CHECKING
from collections.abc import AsyncGenerator
from datetime import datetime

from pydantic import BaseModel
 

from ..messages import Message, UserMessage, SystemMessage
from ..types import AgentResponse, AgentEvent, Usage, AgentConfig
from ..tools import BaseTool, FunctionTool
from ..memory import BaseMemory
from ..llm import BaseChatCompletionClient
from .._cancellation_token import CancellationToken


class AgentCallback(ABC):
    """
    Abstract base class for agent lifecycle callbacks.
    
    Enables logging, metrics collection, debugging, and custom behavior injection.
    """
    
    async def before_tool_call(self, request: Any) -> None:
        """Called before tool execution."""
        pass
    
    async def after_tool_call(self, request: Any, result: Any) -> None:
        """Called after tool execution."""
        pass
    
    async def before_model_call(self, messages: List[Message]) -> None:
        """Called before LLM API call."""
        pass
    
    async def after_model_call(self, result: Any) -> None:
        """Called after LLM responds."""
        pass


class BaseAgent(ABC):
    """
    Abstract base class defining the core agent interface.
    
    All agents in the picoagents framework must inherit from this base class
    and implement its abstract methods, following the stub.md specification.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        instructions: str,
        model_client: BaseChatCompletionClient,
        tools: Optional[List[Union[BaseTool, Callable]]] = None,
        memory: Optional[BaseMemory] = None,
        message_history: Optional[List[Message]] = None,
        callback: Optional[AgentCallback] = None,
        max_iterations: int = 10,
        output_format: Optional[Type[BaseModel]] = None,
        **kwargs: Any
    ):
        """
        Initialize the base agent following stub.md specification.
        
        Args:
            name: Unique identifier for the agent
            description: External-facing description for orchestrators/other agents
            instructions: Internal system prompt/role definition for LLM calls
            model_client: Abstraction for LLM API calls
            tools: Available tools for the agent
            memory: Persistent storage for agent state
            message_history: Conversation context
            callback: Optional callback for lifecycle hooks
            max_iterations: Maximum tool call iterations to prevent loops
            output_format: Optional Pydantic model for structured output
            **kwargs: Additional configuration
        """
        self.name = name
        self.description = description
        self.instructions = instructions
        self.model_client = model_client
        self.tools = self._process_tools(tools or [])
        self.memory = memory
        self.message_history = message_history or []
        self.callback = callback
        self.max_iterations = max_iterations
        self.output_format = output_format
        
        # Validate configuration
        self._validate_configuration()
    
    def _validate_configuration(self) -> None:
        """Validate agent configuration."""
        if not self.name or not isinstance(self.name, str):
            raise AgentConfigurationError("Agent name must be a non-empty string")
        
        if not self.description:
            raise AgentConfigurationError("Agent description cannot be empty")
        
        if not self.instructions:
            raise AgentConfigurationError("Agent instructions cannot be empty")
        
        if self.model_client is None:
            raise AgentConfigurationError("Model client is required")
    
    def _process_tools(self, tools: List[Union[BaseTool, Callable]]) -> List[BaseTool]:
        """
        Convert mixed tool types to BaseTool instances.
        
        Args:
            tools: List of BaseTool instances or callable functions
            
        Returns:
            List of BaseTool instances
        """
        processed = []
        for tool in tools:
            if isinstance(tool, BaseTool):
                processed.append(tool)
            elif callable(tool):
                processed.append(FunctionTool(tool))
            else:
                raise AgentConfigurationError(f"Invalid tool type: {type(tool)}. Must be BaseTool or callable.")
        return processed
    
    def _find_tool(self, name: str) -> Optional[BaseTool]:
        """
        Find tool by name.
        
        Args:
            name: Tool name to search for
            
        Returns:
            Tool instance or None if not found
        """
        return next((tool for tool in self.tools if tool.name == name), None)
    
    def _get_tools_for_llm(self) -> List[Dict[str, Any]]:
        """
        Convert tools to OpenAI function calling format.
        
        Returns:
            List of tools in OpenAI function format
        """
        return [tool.to_llm_format() for tool in self.tools]
    
    @abstractmethod
    async def run(self, task: Union[str, UserMessage, List[Message]], cancellation_token: Optional[CancellationToken] = None) -> AgentResponse:
        """
        Execute the agent's main reasoning and action loop.
        
        Args:
            task: The task or query for the agent to address
            cancellation_token: Optional token for cancelling execution
            
        Returns:
            AgentResponse containing messages and usage statistics
            
        Raises:
            AgentError: If the agent encounters an error during execution
            asyncio.CancelledError: If execution is cancelled
        """
        pass
    
    @abstractmethod
    def run_stream(self, task: Union[str, UserMessage, List[Message]], cancellation_token: Optional[CancellationToken] = None, verbose: bool = False) -> AsyncGenerator[Union[Message, AgentEvent, AgentResponse], None]:
        """
        Execute the agent with streaming output.
        
        Args:
            task: The task or query for the agent to address
            cancellation_token: Optional token for cancelling execution
            verbose: If True, emit agent events; if False, only emit messages and response
            
        Yields:
            Messages, events (if verbose=True), and final AgentResponse with usage stats
            
        Raises:
            AgentError: If the agent encounters an error during execution
            asyncio.CancelledError: If execution is cancelled
        """
        pass
    
    def _convert_task_to_messages(self, task: Union[str, UserMessage, List[Message]]) -> List[Message]:
        """
        Convert task input to proper message format.
        
        Args:
            task: Task in various formats
            
        Returns:
            List of messages
        """
        if isinstance(task, str):
            return [UserMessage(content=task, source="user")]
        elif isinstance(task, UserMessage):
            return [task]
        elif isinstance(task, list):
            return task
        else:
            raise AgentExecutionError(f"Unsupported task type: {type(task)}")
    
    async def _prepare_llm_messages(self, task_messages: List[Message]) -> List[Message]:
        """
        Prepare messages for LLM call including system instructions, memory context, and history.
        
        Args:
            task_messages: Messages from the current task
            
        Returns:
            Complete list of messages for LLM
        """
        messages = []
        
        # Add system message with instructions
        system_content = self.instructions
        
        # Add memory context if available
        if self.memory:
            try:
                # Get relevant context from memory based on current task
                current_task = task_messages[0].content if task_messages else ""
                context = await self.memory.get_context(max_items=5)
                if context:
                    system_content += "\n\nRelevant context from memory:\n" + "\n".join(context)
            except Exception:
                # Don't fail if memory access fails
                pass
        
        messages.append(SystemMessage(content=system_content, source="system"))
        
        # Add message history
        messages.extend(self.message_history)
        
        # Add current task messages
        messages.extend(task_messages)
        
        return messages
    
    async def reset(self) -> None:
        """
        Reset the agent to a clean state.
        
        Clears conversation history and temporary state while preserving
        core configuration.
        """
        self.message_history.clear()
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the agent for debugging and coordination.
        
        Returns:
            Dictionary containing agent metadata
        """
        return {
            "name": self.name,
            "description": self.description,
            "type": self.__class__.__name__,
            "model": getattr(self.model_client, 'model', 'unknown'),
            "tools_count": len(self.tools),
            "has_memory": self.memory is not None,
            "has_callback": self.callback is not None,
            "message_history_length": len(self.message_history)
        }
    
    def get_conversation_data(self) -> Dict[str, Any]:
        """
        Get current conversation data for application-managed memory storage.
        
        Returns:
            Dictionary containing conversation context that applications can use
            to decide what to store in memory
        """
        from ..messages import UserMessage, AssistantMessage, ToolMessage
        
        user_messages = [msg for msg in self.message_history if isinstance(msg, UserMessage)]
        assistant_messages = [msg for msg in self.message_history if isinstance(msg, AssistantMessage)]
        tool_messages = [msg for msg in self.message_history if isinstance(msg, ToolMessage)]
        
        return {
            "agent_name": self.name,
            "total_messages": len(self.message_history),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages), 
            "tool_messages": len(tool_messages),
            "tools_used": list(set([msg.tool_name for msg in tool_messages if msg.success])),
            "last_user_message": user_messages[-1].content if user_messages else None,
            "last_assistant_message": assistant_messages[-1].content if assistant_messages else None,
            "conversation_history": [
                {
                    "type": type(msg).__name__,
                    "content": msg.content[:200] + "..." if len(msg.content) > 200 else msg.content,
                    "timestamp": getattr(msg, 'timestamp', None)
                }
                for msg in self.message_history
            ]
        }
    
    def to_config(self) -> AgentConfig:
        """
        Convert agent to serializable configuration.
        
        Returns:
            AgentConfig with current agent settings
        """
        return AgentConfig(
            name=self.name,
            description=self.description,
            instructions=self.instructions,
            model=getattr(self.model_client, 'model', 'unknown'),
            max_iterations=self.max_iterations
        )
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(name='{self.name}')"
    
    def __repr__(self) -> str:
        """Detailed string representation of the agent."""
        return f"{self.__class__.__name__}(name='{self.name}', description='{self.description[:50]}...')"


class AgentError(Exception):
    """Base exception class for agent-related errors."""
    
    def __init__(self, message: str, agent_name: Optional[str] = None):
        self.agent_name = agent_name
        super().__init__(message)
    
    def __str__(self) -> str:
        if self.agent_name:
            return f"Agent '{self.agent_name}': {super().__str__()}"
        return super().__str__()


class AgentExecutionError(AgentError):
    """Raised when an agent encounters an error during task execution."""
    pass


class AgentConfigurationError(AgentError):
    """Raised when an agent is misconfigured."""
    pass


class AgentToolError(AgentError):
    """Raised when an agent's tool execution fails."""
    pass


class AgentMemoryError(AgentError):
    """Raised when agent memory operations fail."""
    pass


class AgentTimeoutError(AgentError):
    """Raised when agent execution times out."""
    pass