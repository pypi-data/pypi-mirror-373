"""
Test the new simplified tool wrapping functionality.
"""

import asyncio
import pytest
from typing import List, Dict, Any, Optional, Type, AsyncGenerator
from pydantic import BaseModel

from picoagents import Agent, FunctionTool, BaseTool
from picoagents.llm import BaseChatCompletionClient
from picoagents.messages import AssistantMessage
from picoagents.types import ChatCompletionResult, Usage, ToolResult


class MockChatCompletionClient(BaseChatCompletionClient):
    """Mock client for testing."""
    
    async def create(
        self, 
        messages: List[Any], 
        tools: Optional[List[Dict[str, Any]]] = None,
        output_format: Optional[Type[BaseModel]] = None,
        **kwargs: Any
    ) -> ChatCompletionResult:
        return ChatCompletionResult(
            message=AssistantMessage(content="Test response", source="mock"),
            usage=Usage(duration_ms=100, llm_calls=1, tokens_input=10, tokens_output=5, tool_calls=0, memory_operations=0),
            model="test-model",
            finish_reason="stop"
        )
    
    async def create_stream(
        self, 
        messages: List[Any], 
        tools: Optional[List[Dict[str, Any]]] = None,
        output_format: Optional[Type[BaseModel]] = None,
        **kwargs: Any
    ) -> AsyncGenerator[Any, None]:
        from picoagents.types import ChatCompletionChunk
        yield ChatCompletionChunk(content="Test response", is_complete=True, tool_call_chunk=None)


def simple_function(text: str) -> str:
    """A simple test function."""
    return f"Processed: {text}"


def math_function(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


class CustomTool(BaseTool):
    """A custom tool for testing."""
    
    def __init__(self):
        super().__init__("custom_tool", "A custom tool for testing")
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Message to process"}
            },
            "required": ["message"]
        }
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        return ToolResult(
            success=True,
            result=f"Custom tool processed: {parameters.get('message', '')}",
            error=None,
            metadata={"tool_name": self.name}
        )


@pytest.mark.asyncio
async def test_function_auto_wrapping():
    """Test that functions are automatically wrapped as FunctionTool."""
    client = MockChatCompletionClient(model="test")
    
    agent = Agent(
        name="test-agent",
        description="Test agent",
        instructions="You are helpful",
        model_client=client,
        tools=[simple_function]  # Function should be auto-wrapped
    )
    
    # Check that the function was wrapped
    assert len(agent.tools) == 1
    assert isinstance(agent.tools[0], FunctionTool)
    assert agent.tools[0].name == "simple_function"
    assert agent.tools[0].func == simple_function
    
    print("✅ Function auto-wrapping test passed!")


@pytest.mark.asyncio
async def test_mixed_tool_types():
    """Test mixing functions, FunctionTool instances, and custom BaseTool instances."""
    client = MockChatCompletionClient(model="test")
    
    custom_tool = CustomTool()
    explicit_function_tool = FunctionTool(math_function, description="Math calculator")
    
    agent = Agent(
        name="mixed-agent",
        description="Agent with mixed tools",
        instructions="You are helpful",
        model_client=client,
        tools=[
            simple_function,        # Raw function -> auto-wrapped
            explicit_function_tool, # Explicit FunctionTool -> used directly  
            custom_tool            # Custom BaseTool -> used directly
        ]
    )
    
    # Check all tools are present
    assert len(agent.tools) == 3
    
    # Check types
    assert isinstance(agent.tools[0], FunctionTool)  # Auto-wrapped
    assert isinstance(agent.tools[1], FunctionTool)  # Explicit FunctionTool
    assert isinstance(agent.tools[2], CustomTool)    # Custom BaseTool
    
    # Check names
    tool_names = [tool.name for tool in agent.tools]
    assert "simple_function" in tool_names
    assert "math_function" in tool_names
    assert "custom_tool" in tool_names
    
    print("✅ Mixed tool types test passed!")


@pytest.mark.asyncio
async def test_tool_finding():
    """Test that tools can be found by name."""
    client = MockChatCompletionClient(model="test")
    
    agent = Agent(
        name="finder-agent",
        description="Test agent",
        instructions="You are helpful",
        model_client=client,
        tools=[simple_function, math_function]
    )
    
    # Test finding existing tools
    tool1 = agent._find_tool("simple_function")
    assert tool1 is not None
    assert tool1.name == "simple_function"
    
    tool2 = agent._find_tool("math_function")
    assert tool2 is not None
    assert tool2.name == "math_function"
    
    # Test finding non-existent tool
    tool3 = agent._find_tool("nonexistent_tool")
    assert tool3 is None
    
    print("✅ Tool finding test passed!")


@pytest.mark.asyncio
async def test_tools_for_llm():
    """Test converting tools to OpenAI format."""
    client = MockChatCompletionClient(model="test")
    
    agent = Agent(
        name="llm-agent",
        description="Test agent",
        instructions="You are helpful",
        model_client=client,
        tools=[simple_function]
    )
    
    llm_tools = agent._get_tools_for_llm()
    
    # Should have one tool
    assert len(llm_tools) == 1
    
    # Check OpenAI format
    tool_def = llm_tools[0]
    assert tool_def["type"] == "function"
    assert "function" in tool_def
    assert tool_def["function"]["name"] == "simple_function"
    assert "description" in tool_def["function"]
    assert "parameters" in tool_def["function"]
    
    print("✅ Tools for LLM conversion test passed!")


@pytest.mark.asyncio
async def test_invalid_tool_type():
    """Test that invalid tool types raise errors."""
    client = MockChatCompletionClient(model="test")
    
    try:
        agent = Agent(
            name="error-agent",
            description="Test agent",
            instructions="You are helpful", 
            model_client=client,
            tools=["not_a_tool_or_function"]  # type: ignore
        )
        assert False, "Should have raised an error for invalid tool type"
    except Exception as e:
        assert "Invalid tool type" in str(e)
        print("✅ Invalid tool type error test passed!")


async def main():
    """Run all tests."""
    print("=== Testing Simplified Tool Management ===\n")
    
    await test_function_auto_wrapping()
    await test_mixed_tool_types()
    await test_tool_finding()
    await test_tools_for_llm()
    await test_invalid_tool_type()
    
    print("\n🎉 All tool management tests passed!")


if __name__ == "__main__":
    asyncio.run(main())