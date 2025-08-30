"""
Concrete Agent implementation following the stub.md specification.

This module implements a full-featured agent that can reason using LLMs,
act through tools, maintain memory, and communicate with other agents.
"""

import time
import asyncio
from typing import List, Union, Optional
from collections.abc import AsyncGenerator

from ._base import BaseAgent
from ..messages import Message, UserMessage, AssistantMessage, ToolMessage, ToolCallRequest
from ..types import AgentResponse, AgentEvent, Usage
from ..types import (
    TaskStartEvent, TaskCompleteEvent, ModelCallEvent, ModelResponseEvent,
    ToolCallEvent, ToolCallResponseEvent, ErrorEvent
)
from .._cancellation_token import CancellationToken


class Agent(BaseAgent):
    """
    A concrete agent implementation following stub.md specification.
    
    This implementation demonstrates:
    - Integration with generative AI models for reasoning
    - Tool calling and execution for acting
    - Memory management for adaptation  
    - Message history for communication
    - Streaming support with events
    """
    
    async def run(self, task: Union[str, UserMessage, List[Message]], cancellation_token: Optional[CancellationToken] = None) -> AgentResponse:
        """
        Execute the agent's main reasoning and action loop.
        
        This method internally uses run_stream() and filters for messages only,
        as specified in stub.md.
        
        Args:
            task: The task or query for the agent to address
            cancellation_token: Optional token for cancelling execution
            
        Returns:
            AgentResponse containing messages and usage statistics
        """
        final_response = None
        start_time = time.time()
        
        try:
            async for item in self.run_stream(task, cancellation_token):
                # Capture the final AgentResponse 
                if isinstance(item, AgentResponse):
                    final_response = item
            
            # Return the final response from the stream, or create fallback
            if final_response:
                return final_response
            else:
                # Fallback if no AgentResponse was yielded
                duration_ms = int((time.time() - start_time) * 1000)
                return AgentResponse(
                    source=self.name,
                    messages=[],
                    usage=Usage(duration_ms=duration_ms)
                )
            
        except asyncio.CancelledError:
            # Re-raise cancellation for proper handling
            raise
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            usage_stats = Usage(duration_ms=duration_ms)
            
            # Return error response
            error_message = AssistantMessage(content=f"Error: {str(e)}", source=self.name)
            return AgentResponse(
                source=self.name,
                messages=[error_message], usage=usage_stats)
    
    async def run_stream(self, task: Union[str, UserMessage, List[Message]], cancellation_token: Optional[CancellationToken] = None, verbose: bool = False) -> AsyncGenerator[Union[Message, AgentEvent, AgentResponse], None]:
        """
        Execute the agent with streaming output.
        
        Yields both Messages (for UI/conversation), Events (for debugging/observability),
        and final AgentResponse (for usage statistics).
        
        Args:
            task: The task or query for the agent to address
            cancellation_token: Optional token for cancelling execution
            
        Yields:
            Messages and events during execution
        """
        start_time = time.time()
        messages_yielded = []
        llm_calls = 0
        tokens_input = 0
        tokens_output = 0
        
        try:
            # Check for cancellation at the start
            if cancellation_token and cancellation_token.is_cancelled():
                raise asyncio.CancelledError()
            
            # 1. Convert task to message format
            task_messages = self._convert_task_to_messages(task)
            
            # Yield the initial user message
            user_message = task_messages[0]
            yield user_message
            messages_yielded.append(user_message)
            
            # Emit task start event
            if verbose:
                yield TaskStartEvent(
                    source=self.name,
                    task=user_message.content
                )
            
            # 2. Prepare messages for LLM including system instructions, memory, history
            llm_messages = await self._prepare_llm_messages(task_messages)
            
            # Call callback if available
            if self.callback:
                await self.callback.before_model_call(llm_messages)
            
            # 3. Make initial LLM call
            if verbose:
                yield ModelCallEvent(
                    source=self.name,
                    input_messages=llm_messages,
                    model=getattr(self.model_client, 'model', 'unknown')
                )
            
            # Initialize assistant_message to avoid unbound variable
            assistant_message = AssistantMessage(content="Task completed", source=self.name)
            
            iteration = 0
            while iteration < self.max_iterations:
                try:
                    # Check for cancellation at the start of each iteration
                    if cancellation_token and cancellation_token.is_cancelled():
                        raise asyncio.CancelledError()
                    
                    # Get tools for LLM if available
                    tools = self._get_tools_for_llm() if self.tools else None
                    
                    # Create and link LLM call task for cancellation
                    llm_task = asyncio.create_task(
                        self.model_client.create(llm_messages, tools=tools, output_format=self.output_format)
                    )
                    if cancellation_token:
                        cancellation_token.link_future(llm_task)
                    
                    # Make LLM API call
                    completion_result = await llm_task
                    original_message = completion_result.message
                    
                    # Always create new AssistantMessage with source
                    assistant_message = AssistantMessage(
                        content=original_message.content,
                        source=self.name,
                        tool_calls=original_message.tool_calls,
                        structured_content=completion_result.structured_output if completion_result.structured_output else None
                    )
                    
                    llm_calls += 1
                    
                    # Track token usage if available
                    if hasattr(completion_result, 'usage'):
                        tokens_input += getattr(completion_result.usage, 'tokens_input', 0)
                        tokens_output += getattr(completion_result.usage, 'tokens_output', 0)
                    
                    # Yield the assistant response
                    yield assistant_message
                    messages_yielded.append(assistant_message)
                    
                    # Emit model response event
                    if verbose:
                        yield ModelResponseEvent(
                            source=self.name,
                            response=assistant_message.content,
                            has_tool_calls=assistant_message.tool_calls is not None
                        )
                    
                    # Add assistant message to history
                    self.message_history.append(assistant_message)
                    llm_messages.append(assistant_message)
                    
                    # Call callback if available
                    if self.callback:
                        await self.callback.after_model_call(completion_result)
                    
                    # 4. Handle tool calls if present
                    if assistant_message.tool_calls:
                        for tool_call in assistant_message.tool_calls:
                            async for item in self._execute_tool_call(tool_call, llm_messages, cancellation_token):
                                yield item
                                # Track messages for final response
                                if isinstance(item, (UserMessage, AssistantMessage, ToolMessage)):
                                    messages_yielded.append(item)
                        
                        # Continue loop for next LLM call after tool execution
                        iteration += 1
                        continue
                    
                    # No tool calls, we're done
                    break
                        
                except asyncio.CancelledError:
                    # Re-raise cancellation for proper handling
                    raise
                except Exception as e:
                    error_event = ErrorEvent(
                        source=self.name,
                        error_message=str(e),
                        error_type=type(e).__name__
                    )
                    yield error_event
                    
                    # Yield error message
                    error_message = AssistantMessage(content=f"I encountered an error: {str(e)}", source=self.name)
                    yield error_message
                    messages_yielded.append(error_message)
                    break
            
            # Emit task completion event
            if verbose:
                yield TaskCompleteEvent(
                    source=self.name,
                    result=assistant_message.content
                )
            
            # Yield final AgentResponse with complete conversation and usage stats
            duration_ms = int((time.time() - start_time) * 1000)
            tool_calls = sum(1 for msg in messages_yielded if isinstance(msg, ToolMessage))
            
            final_response = AgentResponse(
                source=self.name,
                messages=messages_yielded,
                usage=Usage(
                    duration_ms=duration_ms,
                    llm_calls=llm_calls,
                    tokens_input=tokens_input,
                    tokens_output=tokens_output,
                    tool_calls=tool_calls
                )
            )
            yield final_response
            
        except asyncio.CancelledError:
            # Handle cancellation gracefully
            yield ErrorEvent(
                source=self.name,
                error_message="Agent execution was cancelled",
                error_type="CancelledError",
                is_recoverable=False
            )
            
            # Yield final cancellation message
            cancel_message = AssistantMessage(content="Agent execution was cancelled", source=self.name)
            yield cancel_message
            messages_yielded.append(cancel_message)
            
            # Yield final AgentResponse for cancelled execution
            duration_ms = int((time.time() - start_time) * 1000)
            tool_calls = sum(1 for msg in messages_yielded if isinstance(msg, ToolMessage))
            
            cancel_response = AgentResponse(
                source=self.name,
                messages=messages_yielded,
                usage=Usage(
                    duration_ms=duration_ms,
                    llm_calls=llm_calls,
                    tokens_input=tokens_input,
                    tokens_output=tokens_output,
                    tool_calls=tool_calls
                )
            )
            yield cancel_response
            
            # Re-raise the cancellation
            raise
            
        except Exception as e:
            # Emit fatal error event
            yield ErrorEvent(
                source=self.name,
                error_message=str(e),
                error_type=type(e).__name__,
                is_recoverable=False
            )
            
            # Yield final error message
            error_message = AssistantMessage(content=f"Fatal error: {str(e)}", source=self.name)
            yield error_message
            messages_yielded.append(error_message)
            
            # Yield final AgentResponse even for errors
            duration_ms = int((time.time() - start_time) * 1000)
            tool_calls = sum(1 for msg in messages_yielded if isinstance(msg, ToolMessage))
            
            error_response = AgentResponse(
                source=self.name,
                messages=messages_yielded,
                usage=Usage(
                    duration_ms=duration_ms,
                    llm_calls=llm_calls,
                    tokens_input=tokens_input,
                    tokens_output=tokens_output,
                    tool_calls=tool_calls
                )
            )
            yield error_response
    
    async def _execute_tool_call(self, tool_call: ToolCallRequest, llm_messages: List[Message], cancellation_token: Optional[CancellationToken] = None) -> AsyncGenerator[Union[Message, AgentEvent], None]:
        """
        Execute a single tool call and yield events and result message.
        
        Args:
            tool_call: The tool call to execute
            llm_messages: Current message history for context
            cancellation_token: Optional token for cancelling execution
            
        Yields:
            Events and the final ToolMessage
        """
        # Check for cancellation before tool execution
        if cancellation_token and cancellation_token.is_cancelled():
            raise asyncio.CancelledError()
        
        # Emit tool call event
        tool_event = ToolCallEvent(
            source=self.name,
            tool_name=tool_call.tool_name,
            parameters=tool_call.parameters,
            call_id=tool_call.call_id
        )
        yield tool_event
        
        try:
            # Call callback if available
            if self.callback:
                await self.callback.before_tool_call(tool_call)
            
            # Find and execute the tool
            tool = self._find_tool(tool_call.tool_name)
            if tool is None:
                error_msg = f"Tool '{tool_call.tool_name}' not found"
                result = ToolMessage(
                    content=error_msg,
                    source=self.name,
                    tool_call_id=tool_call.call_id,
                    tool_name=tool_call.tool_name,
                    success=False,
                    error=error_msg
                )
                tool_result = None
            else:
                # Execute the tool with cancellation support
                tool_task = asyncio.create_task(tool.execute(tool_call.parameters))
                if cancellation_token:
                    cancellation_token.link_future(tool_task)
                
                tool_result = await tool_task
                
                result = ToolMessage(
                    content=str(tool_result.result) if tool_result.success else f"Error: {tool_result.error}",
                    source=self.name,
                    tool_call_id=tool_call.call_id,
                    tool_name=tool_call.tool_name,
                    success=tool_result.success,
                    error=tool_result.error
                )
                
                # Call callback if available
                if self.callback:
                    await self.callback.after_tool_call(tool_call, tool_result)
            
            # Emit tool response event (with proper None handling)
            tool_response_event = ToolCallResponseEvent(
                source=self.name,
                call_id=tool_call.call_id,
                result=tool_result  # May be None, but that's okay
            )
            yield tool_response_event
            
            # Add tool result to message history
            self.message_history.append(result)
            llm_messages.append(result)
            
            # Yield the final result message
            yield result
            
        except asyncio.CancelledError:
            # Handle tool cancellation
            error_msg = "Tool execution was cancelled"
            error_result = ToolMessage(
                content=error_msg,
                source=self.name,
                tool_call_id=tool_call.call_id,
                tool_name=tool_call.tool_name,
                success=False,
                error=error_msg
            )
            
            # Add error result to message history
            self.message_history.append(error_result)
            llm_messages.append(error_result)
            
            # Yield the error result
            yield error_result
            
            # Re-raise cancellation
            raise
            
        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            error_result = ToolMessage(
                content=error_msg,
                source=self.name,
                tool_call_id=tool_call.call_id,
                tool_name=tool_call.tool_name,
                success=False,
                error=error_msg
            )
            
            # Add error result to message history
            self.message_history.append(error_result)
            llm_messages.append(error_result)
            
            # Yield the error result
            yield error_result