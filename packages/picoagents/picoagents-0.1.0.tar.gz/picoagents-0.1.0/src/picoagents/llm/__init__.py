"""
LLM client implementations for picoagents framework.

Provides unified interface for different language model providers
with standardized response formats and error handling.
"""

from ._base import (
    BaseChatCompletionClient,
    BaseChatCompletionError,
    RateLimitError,
    AuthenticationError,
    InvalidRequestError
)
from ._openai import OpenAIChatCompletionClient

__all__ = [
    "BaseChatCompletionClient",
    "BaseChatCompletionError",
    "RateLimitError", 
    "AuthenticationError",
    "InvalidRequestError",
    "OpenAIChatCompletionClient"
]