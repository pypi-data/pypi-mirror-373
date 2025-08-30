"""
OpenAI BaseChatCompletionClient implementation.

This module provides integration with OpenAI's API using the official
openai>=1.100.2 client library.
"""

import json
import time
from typing import List, Dict, Optional, Any, AsyncGenerator, Type, TYPE_CHECKING
 
from pydantic import BaseModel

try:
    from openai import AsyncOpenAI
    from openai.types.chat import ChatCompletion, ChatCompletionChunk as OpenAIChatCompletionChunk
    from openai.types.chat.chat_completion import Choice
    from openai.types.chat.chat_completion_chunk import Choice as ChunkChoice
    from openai.types.completion_usage import CompletionUsage
    from openai import APIError, RateLimitError as OpenAIRateLimitError, AuthenticationError as OpenAIAuthError
except ImportError:
    raise ImportError("OpenAI library not installed. Please install with: pip install openai>=1.100.2")

from ._base import BaseChatCompletionClient, BaseChatCompletionError, RateLimitError, AuthenticationError, InvalidRequestError
from ..messages import Message, AssistantMessage, ToolCallRequest
from ..types import ChatCompletionResult, ChatCompletionChunk, Usage


class OpenAIChatCompletionClient(BaseChatCompletionClient):
    """
    OpenAI implementation of BaseChatCompletionClient.
    
    Supports GPT-4, GPT-3.5-turbo, and other OpenAI models with
    function calling capabilities.
    """
    
    def __init__(
        self, 
        model: str = "gpt-4o-mini", 
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        organization: Optional[str] = None,
        **kwargs: Any
    ):
        """
        Initialize OpenAI client.
        
        Args:
            model: OpenAI model name. For structured output, use "gpt-4o-mini" or "gpt-4o-2024-08-06"+
            api_key: OpenAI API key (will use OPENAI_API_KEY env var if not provided)
            base_url: Custom base URL for API calls
            organization: OpenAI organization ID
            **kwargs: Additional OpenAI client configuration
        """
        super().__init__(model, api_key, **kwargs)
        
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            organization=organization,
            **kwargs
        )
    
    async def create(
        self, 
        messages: List[Message], 
        tools: Optional[List[Dict[str, Any]]] = None,
        output_format: Optional[Type[BaseModel]] = None,
        **kwargs: Any
    ) -> ChatCompletionResult:
        """
        Make a single OpenAI API call.
        
        Args:
            messages: List of messages to send
            tools: Optional function definitions for tool calling
            output_format: Optional Pydantic model for structured output
            **kwargs: Additional OpenAI parameters (temperature, max_tokens, etc.)
            
        Returns:
            Standardized chat completion result
        """
        try:
            start_time = time.time()
            
            # Convert messages to OpenAI format
            api_messages = self._convert_messages_to_api_format(messages)
            
            # Prepare request parameters
            request_params = {
                "model": self.model,
                "messages": api_messages,
                **kwargs
            }
            
            # Add tools if provided
            if tools:
                request_params["tools"] = tools
                request_params["tool_choice"] = "auto"
            
            # Add structured output if requested
            if output_format:
                try:
                    # Convert Pydantic model to JSON schema for OpenAI
                    schema = output_format.model_json_schema()
                    
                    # Ensure OpenAI Structured Outputs compatibility
                    schema = self._make_schema_compatible(schema)
                    
                    # Format according to OpenAI documentation
                    request_params["response_format"] = {
                        "type": "json_schema",
                        "json_schema": {
                            "name": schema.get("title", output_format.__name__),
                            "description": schema.get("description", f"Structured output for {output_format.__name__}"),
                            "strict": True,
                            "schema": schema
                        }
                    }
                except Exception as e:
                    # If schema conversion fails, continue without structured output
                    print(f"Warning: Failed to convert {output_format.__name__} to JSON schema: {e}")
                    pass
            
            # Make API call
            response: ChatCompletion = await self.client.chat.completions.create(**request_params)
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Extract the assistant message
            choice: Choice = response.choices[0]
            assistant_content = choice.message.content or ""
            
            # Handle tool calls if present
            tool_calls = []
            if choice.message.tool_calls:
                for tc in choice.message.tool_calls:
                    tool_calls.append(ToolCallRequest(
                        tool_name=tc.function.name,
                        parameters=json.loads(tc.function.arguments) if tc.function.arguments else {},
                        call_id=tc.id
                    ))
            
            assistant_message = AssistantMessage(
                content=assistant_content,
                source="llm",  # Temporary source, will be overwritten by agent
                tool_calls=tool_calls if tool_calls else None
            )
            
            # Parse structured output if requested
            structured_output = None
            if output_format and assistant_content:
                try:
                    # Try to parse the JSON content using the provided Pydantic model
                    structured_output = output_format.model_validate_json(assistant_content)
                except Exception as e:
                    # If parsing fails, log warning but continue with text response
                    print(f"Warning: Failed to parse structured output: {e}")
                    pass
            
            # Create usage statistics
            usage_data = response.usage
            usage = Usage(
                duration_ms=duration_ms,
                llm_calls=1,
                tokens_input=usage_data.prompt_tokens if usage_data else 0,
                tokens_output=usage_data.completion_tokens if usage_data else 0,
                tool_calls=len(tool_calls),
                cost_estimate=self._estimate_cost(usage_data) if usage_data else None
            )
            
            return ChatCompletionResult(
                message=assistant_message,
                usage=usage,
                model=response.model,
                finish_reason=choice.finish_reason or "stop",
                structured_output=structured_output
            )
            
        except OpenAIAuthError as e:
            raise AuthenticationError(f"OpenAI authentication failed: {str(e)}")
        except OpenAIRateLimitError as e:
            raise RateLimitError(f"OpenAI rate limit exceeded: {str(e)}")
        except APIError as e:
            raise BaseChatCompletionError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            raise BaseChatCompletionError(f"Unexpected error: {str(e)}")
    
    async def create_stream(
        self, 
        messages: List[Message], 
        tools: Optional[List[Dict[str, Any]]] = None,
        output_format: Optional[Type[BaseModel]] = None,
        **kwargs: Any
    ) -> AsyncGenerator[ChatCompletionChunk, None]:
        """
        Make a streaming OpenAI API call.
        
        Args:
            messages: List of messages to send
            tools: Optional function definitions for tool calling
            output_format: Optional Pydantic model for structured output (Note: streaming structured output not fully supported yet)
            **kwargs: Additional OpenAI parameters
            
        Yields:
            ChatCompletionChunk objects with incremental response data
        """
        try:
            # Note: Streaming structured output is not fully implemented yet
            if output_format:
                print("Warning: Structured output is not yet supported in streaming mode")
            
            # Convert messages to OpenAI format
            api_messages = self._convert_messages_to_api_format(messages)
            
            # Prepare request parameters
            request_params = {
                "model": self.model,
                "messages": api_messages,
                "stream": True,
                **kwargs
            }
            
            # Add tools if provided
            if tools:
                request_params["tools"] = tools
                request_params["tool_choice"] = "auto"
            
            # Make streaming API call
            stream = await self.client.chat.completions.create(**request_params)
            
            accumulated_content = ""
            tool_call_chunks = {}
            
            async for chunk in stream:
                chunk_choice: ChunkChoice = chunk.choices[0]
                delta = chunk_choice.delta
                
                # Handle content chunks
                if delta.content:
                    accumulated_content += delta.content
                    yield ChatCompletionChunk(
                        content=delta.content,
                        is_complete=False,
                        tool_call_chunk=None
                    )
                
                # Handle tool call chunks
                if delta.tool_calls:
                    for tc_delta in delta.tool_calls:
                        call_id = tc_delta.id
                        if call_id not in tool_call_chunks:
                            tool_call_chunks[call_id] = {
                                "id": call_id,
                                "function": {"name": "", "arguments": ""}
                            }
                        
                        if tc_delta.function:
                            if tc_delta.function.name:
                                tool_call_chunks[call_id]["function"]["name"] = tc_delta.function.name
                            if tc_delta.function.arguments:
                                tool_call_chunks[call_id]["function"]["arguments"] += tc_delta.function.arguments
                        
                        yield ChatCompletionChunk(
                            content="",
                            is_complete=False,
                            tool_call_chunk=tool_call_chunks[call_id]
                        )
                
                # Check if stream is complete
                if chunk_choice.finish_reason:
                    yield ChatCompletionChunk(
                        content="",
                        is_complete=True,
                        tool_call_chunk=None
                    )
                    break
            
        except OpenAIAuthError as e:
            raise AuthenticationError(f"OpenAI authentication failed: {str(e)}")
        except OpenAIRateLimitError as e:
            raise RateLimitError(f"OpenAI rate limit exceeded: {str(e)}")
        except APIError as e:
            raise BaseChatCompletionError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            raise BaseChatCompletionError(f"Unexpected error: {str(e)}")
    
    def _estimate_cost(self, usage: CompletionUsage) -> float:
        """
        Estimate the cost of the API call based on token usage.
        
        Note: These are approximate rates and may not reflect current pricing.
        
        Args:
            usage: OpenAI usage object
            
        Returns:
            Estimated cost in USD
        """
        # Approximate pricing (as of 2024, rates may vary)
        pricing = {
            "gpt-4": {"input": 0.03 / 1000, "output": 0.06 / 1000},
            "gpt-4-turbo": {"input": 0.01 / 1000, "output": 0.03 / 1000},
            "gpt-3.5-turbo": {"input": 0.0005 / 1000, "output": 0.0015 / 1000},
        }
        
        model_pricing = pricing.get(self.model, pricing["gpt-4"])  # Default to GPT-4 pricing
        
        input_cost = usage.prompt_tokens * model_pricing["input"]
        output_cost = usage.completion_tokens * model_pricing["output"]
        
        return input_cost + output_cost
    
    def _make_schema_compatible(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modify schema to be compatible with OpenAI Structured Outputs requirements.
        
        Args:
            schema: The JSON schema to make compatible
            
        Returns:
            Modified schema with OpenAI compatibility fixes
        """
        # Make a copy to avoid modifying the original
        compatible_schema = schema.copy()
        
        # Ensure additionalProperties is False (required by OpenAI)
        if compatible_schema.get("type") == "object":
            compatible_schema["additionalProperties"] = False
            
            # Recursively apply to nested objects
            properties = compatible_schema.get("properties", {})
            for prop_name, prop_schema in properties.items():
                if isinstance(prop_schema, dict):
                    compatible_schema["properties"][prop_name] = self._make_schema_compatible(prop_schema)
        
        # Handle arrays with object items
        if compatible_schema.get("type") == "array":
            items = compatible_schema.get("items")
            if isinstance(items, dict):
                compatible_schema["items"] = self._make_schema_compatible(items)
        
        return compatible_schema