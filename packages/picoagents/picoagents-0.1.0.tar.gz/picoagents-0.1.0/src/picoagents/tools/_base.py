"""
Base tool classes and interfaces for the picoagents framework.

This module defines the abstract base classes and core functionality
for tools that agents can use to interact with the world.
"""

import inspect
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable, get_type_hints, Optional

from ..types import ToolResult


class BaseTool(ABC):
    """
    Abstract base class that all tools must implement.
    
    Defines the interface for tools that agents can use to perform actions
    beyond text generation (e.g., web search, file operations, API calls).
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize the base tool.
        
        Args:
            name: Unique tool identifier
            description: What the tool does (for LLM understanding)
        """
        self.name = name
        self.description = description
    
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """
        JSON schema defining expected inputs for this tool.
        
        Returns:
            JSON schema dictionary describing tool parameters
        """
        pass
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """
        Execute the tool with the given parameters.
        
        Args:
            parameters: Tool input parameters
            
        Returns:
            ToolResult containing execution outcome
        """
        pass
    
    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """
        Validate that the provided parameters match the tool's schema.
        
        Args:
            params: Parameters to validate
            
        Returns:
            True if parameters are valid, False otherwise
        """
        try:
            # Basic validation - subclasses can override for more sophisticated checks
            schema = self.parameters
            required_fields = schema.get("required", [])
            
            # Check required fields are present
            for field in required_fields:
                if field not in params:
                    return False
            
            # Check parameter types if specified in schema
            properties = schema.get("properties", {})
            for param_name, param_value in params.items():
                if param_name in properties:
                    expected_type = properties[param_name].get("type")
                    if expected_type and not self._check_type(param_value, expected_type):
                        return False
            
            return True
        except Exception:
            return False
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected JSON schema type."""
        type_mapping = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type is None:
            return True  # Unknown type, assume valid
        
        return isinstance(value, expected_python_type)
    
    def to_llm_format(self) -> Dict[str, Any]:
        """
        Convert tool to OpenAI function calling format.
        
        Returns:
            Dictionary in OpenAI function format
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', description='{self.description}')"


class FunctionTool(BaseTool):
    """
    Tool that wraps a Python function for use by agents.
    
    Automatically extracts function metadata (name, docstring, parameters)
    and provides parameter validation based on type hints.
    """
    
    def __init__(
        self, 
        func: Callable, 
        name: Optional[str] = None,
        description: Optional[str] = None
    ):
        """
        Create a tool from a Python function.
        
        Args:
            func: The function to wrap as a tool
            name: Optional custom name (defaults to function name)
            description: Optional custom description (defaults to function docstring)
        """
        self.func = func
        tool_name = name or func.__name__
        tool_description = description or func.__doc__ or f"Execute {func.__name__} function"
        
        super().__init__(tool_name, tool_description)
        
        # Extract function metadata
        self.signature = inspect.signature(func)
        self.type_hints = get_type_hints(func)
        self._parameters_schema = self._build_parameters_schema()
    
    @property
    def parameters(self) -> Dict[str, Any]:
        """Get JSON schema for function parameters."""
        return self._parameters_schema
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """
        Execute the wrapped function with validated parameters.
        
        Args:
            parameters: Function arguments
            
        Returns:
            ToolResult with function execution outcome
        """
        try:
            # Validate parameters before execution
            if not self.validate_parameters(parameters):
                return ToolResult(
                    success=False,
                    result=None,
                    error="Invalid parameters provided",
                    metadata={"tool_name": self.name}
                )
            
            # Execute function
            if inspect.iscoroutinefunction(self.func):
                result = await self.func(**parameters)
            else:
                result = self.func(**parameters)
            
            return ToolResult(
                success=True,
                result=result,
                error=None,
                metadata={"tool_name": self.name}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=str(e),
                metadata={"tool_name": self.name, "exception_type": type(e).__name__}
            )
    
    def _build_parameters_schema(self) -> Dict[str, Any]:
        """
        Build JSON schema from function signature and type hints.
        
        Returns:
            JSON schema dictionary
        """
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for param_name, param in self.signature.parameters.items():
            # Skip 'self' parameter
            if param_name == "self":
                continue
            
            # Determine parameter type
            param_type = self.type_hints.get(param_name)
            json_type = self._python_type_to_json_type(param_type)
            
            property_schema = {"type": json_type}
            
            # Add description from annotation if available
            if hasattr(param, "annotation") and hasattr(param.annotation, "__doc__"):
                property_schema["description"] = param.annotation.__doc__
            
            schema["properties"][param_name] = property_schema
            
            # Add to required if no default value
            if param.default == inspect.Parameter.empty:
                schema["required"].append(param_name)
        
        return schema
    
    def _python_type_to_json_type(self, python_type: Any) -> str:
        """
        Convert Python type hints to JSON schema types.
        
        Args:
            python_type: Python type annotation
            
        Returns:
            JSON schema type string
        """
        if python_type is None or python_type == type(None):
            return "null"
        elif python_type == str:
            return "string"
        elif python_type == int:
            return "integer"
        elif python_type == float:
            return "number"
        elif python_type == bool:
            return "boolean"
        elif python_type == list or (hasattr(python_type, "__origin__") and python_type.__origin__ == list):
            return "array"
        elif python_type == dict or (hasattr(python_type, "__origin__") and python_type.__origin__ == dict):
            return "object"
        else:
            # For Union types, complex types, etc., default to string
            return "string"


# ToolRegistry removed - agents now manage tools directly using lists