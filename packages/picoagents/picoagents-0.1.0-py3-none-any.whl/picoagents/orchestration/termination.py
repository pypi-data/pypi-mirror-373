"""
Termination conditions for orchestration patterns.

This module provides various termination conditions that determine when
orchestration should stop, following the PRD specification.
"""

import time
import asyncio
from abc import ABC, abstractmethod
from typing import List, Optional, Callable, Union, Any, Dict, Sequence

from ..messages import Message, ToolMessage, AssistantMessage
from ..types import StopMessage, Usage
from .._cancellation_token import CancellationToken


class BaseTermination(ABC):
    """Abstract base class for all termination conditions."""
    
    def __init__(self) -> None:
        self._met = False
        self._reason = ""
        self._metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def check(self, new_messages: Sequence[Message]) -> Optional[StopMessage]:
        """
        Check termination on delta messages.
        
        Args:
            new_messages: New messages since last check
            
        Returns:
            StopMessage if termination is met, None otherwise
        """
        pass
    
    def is_met(self) -> bool:
        """Current termination state."""
        return self._met
    
    def reset(self) -> None:
        """Reset for next orchestration run."""
        self._met = False
        self._reason = ""
        self._metadata = {}
    
    def get_reason(self) -> str:
        """Why termination occurred."""
        return self._reason
    
    def get_metadata(self) -> Dict[str, Any]:
        """Additional termination metadata."""
        return self._metadata.copy()
    
    def _set_termination(self, reason: str, metadata: Optional[Dict[str, Any]] = None) -> StopMessage:
        """Helper to set termination state and return StopMessage."""
        self._met = True
        self._reason = reason
        self._metadata = metadata or {}
        
        return StopMessage(
            content=reason,
            source=self.__class__.__name__,
            metadata=self._metadata
        )
    
    def __or__(self, other: 'BaseTermination') -> 'CompositeTermination':
        """Implement OR logic with | operator."""
        return CompositeTermination([self, other], mode="any")
    
    def __and__(self, other: 'BaseTermination') -> 'CompositeTermination':
        """Implement AND logic with & operator."""
        return CompositeTermination([self, other], mode="all")


class MaxMessageTermination(BaseTermination):
    """Terminates when maximum messages is reached."""
    
    def __init__(self, max_messages: int):
        super().__init__()
        self.max_messages = max_messages
        self.message_count = 0
    
    def check(self, new_messages: Sequence[Message]) -> Optional[StopMessage]:
        """Check if message limit is exceeded."""
        self.message_count += len(new_messages)
        
        if self.message_count >= self.max_messages:
            return self._set_termination(
                f"Maximum messages reached ({self.message_count}/{self.max_messages})",
                {"message_count": self.message_count, "max_messages": self.max_messages}
            )
        
        return None
    
    def reset(self) -> None:
        """Reset message counter."""
        super().reset()
        self.message_count = 0


class TextMentionTermination(BaseTermination):
    """Terminates when specific text is mentioned."""
    
    def __init__(self, text: str, case_sensitive: bool = False):
        super().__init__()
        self.text = text
        self.case_sensitive = case_sensitive
        self.search_text = text if case_sensitive else text.lower()
    
    def check(self, new_messages: Sequence[Message]) -> Optional[StopMessage]:
        """Check if termination text is found in any new message."""
        for message in new_messages:
            content = message.content if self.case_sensitive else message.content.lower()
            
            if self.search_text in content:
                return self._set_termination(
                    f"Text mention found: '{self.text}'",
                    {"text": self.text, "case_sensitive": self.case_sensitive, "found_in": type(message).__name__}
                )
        
        return None


class TokenUsageTermination(BaseTermination):
    """Terminates when token usage exceeds limit."""
    
    def __init__(self, max_tokens: int):
        super().__init__()
        self.max_tokens = max_tokens
        self.total_tokens = 0
    
    def check(self, new_messages: Sequence[Message]) -> Optional[StopMessage]:
        """Check token usage (approximate based on content length)."""
        # Simple token estimation: ~4 characters per token
        new_tokens = sum(len(msg.content) // 4 for msg in new_messages)
        self.total_tokens += new_tokens
        
        if self.total_tokens >= self.max_tokens:
            return self._set_termination(
                f"Token limit exceeded ({self.total_tokens}/{self.max_tokens})",
                {"total_tokens": self.total_tokens, "max_tokens": self.max_tokens}
            )
        
        return None
    
    def reset(self) -> None:
        """Reset token counter."""
        super().reset()
        self.total_tokens = 0


class TimeoutTermination(BaseTermination):
    """Terminates when time limit is exceeded."""
    
    def __init__(self, max_duration_seconds: Union[int, float]):
        super().__init__()
        self.max_duration_seconds = max_duration_seconds
        self.start_time: Optional[float] = None
    
    def check(self, new_messages: Sequence[Message]) -> Optional[StopMessage]:
        """Check if time limit is exceeded."""
        if self.start_time is None:
            self.start_time = time.time()
        
        elapsed = time.time() - self.start_time
        
        if elapsed >= self.max_duration_seconds:
            return self._set_termination(
                f"Timeout reached ({elapsed:.1f}s/{self.max_duration_seconds}s)",
                {"elapsed_seconds": elapsed, "max_duration_seconds": self.max_duration_seconds}
            )
        
        return None
    
    def reset(self) -> None:
        """Reset timer."""
        super().reset()
        self.start_time = None


class HandoffTermination(BaseTermination):
    """Terminates when agent requests handoff to specific target."""
    
    def __init__(self, target: str):
        super().__init__()
        self.target = target
    
    def check(self, new_messages: Sequence[Message]) -> Optional[StopMessage]:
        """Check for handoff requests in assistant messages."""
        for message in new_messages:
            if isinstance(message, AssistantMessage):
                # Look for handoff patterns in content
                content_lower = message.content.lower()
                handoff_patterns = [
                    f"handoff to {self.target.lower()}",
                    f"transfer to {self.target.lower()}",
                    f"pass to {self.target.lower()}",
                    f"delegate to {self.target.lower()}"
                ]
                
                for pattern in handoff_patterns:
                    if pattern in content_lower:
                        return self._set_termination(
                            f"Handoff requested to '{self.target}'",
                            {"target": self.target, "pattern": pattern}
                        )
        
        return None


class ExternalTermination(BaseTermination):
    """Terminates based on external signal."""
    
    def __init__(self, check_callback: Callable[[], bool]):
        super().__init__()
        self.check_callback = check_callback
    
    def check(self, new_messages: Sequence[Message]) -> Optional[StopMessage]:
        """Check external termination signal."""
        try:
            if self.check_callback():
                return self._set_termination(
                    "External termination signal received",
                    {"source": "external_callback"}
                )
        except Exception as e:
            # Don't let callback errors stop orchestration
            pass
        
        return None


class CancellationTermination(BaseTermination):
    """Terminates when cancellation token is triggered."""
    
    def __init__(self, cancellation_token: CancellationToken):
        super().__init__()
        self.cancellation_token = cancellation_token
    
    def check(self, new_messages: Sequence[Message]) -> Optional[StopMessage]:
        """Check if cancellation token is triggered."""
        if self.cancellation_token.is_cancelled():
            return self._set_termination(
                "Cancellation token triggered",
                {"source": "cancellation_token"}
            )
        
        return None


class FunctionCallTermination(BaseTermination):
    """Terminates when specific function is called."""
    
    def __init__(self, function_name: str):
        super().__init__()
        self.function_name = function_name
    
    def check(self, new_messages: Sequence[Message]) -> Optional[StopMessage]:
        """Check for specific function calls in tool messages."""
        for message in new_messages:
            if isinstance(message, ToolMessage) and message.tool_name == self.function_name:
                return self._set_termination(
                    f"Function '{self.function_name}' was called",
                    {"function_name": self.function_name, "success": message.success}
                )
        
        return None


class CompositeTermination(BaseTermination):
    """Combines multiple termination conditions with logical operators."""
    
    def __init__(self, conditions: List[BaseTermination], mode: str = "any"):
        super().__init__()
        if mode not in ("any", "all"):
            raise ValueError("Mode must be 'any' or 'all'")
        
        self.conditions = conditions
        self.mode = mode
    
    def check(self, new_messages: Sequence[Message]) -> Optional[StopMessage]:
        """Check all conditions based on mode."""
        results = []
        for condition in self.conditions:
            result = condition.check(new_messages)
            if result:
                results.append(result)
        
        if self.mode == "any" and results:
            # Return first termination result
            first_result = results[0]
            return self._set_termination(
                f"Composite (any): {first_result.content}",
                {"mode": "any", "triggered_conditions": [r.source for r in results]}
            )
        elif self.mode == "all" and len(results) == len(self.conditions):
            # All conditions met
            reasons = [r.content for r in results]
            return self._set_termination(
                f"Composite (all): {'; '.join(reasons)}",
                {"mode": "all", "triggered_conditions": [r.source for r in results]}
            )
        
        return None
    
    def reset(self) -> None:
        """Reset all contained conditions."""
        super().reset()
        for condition in self.conditions:
            condition.reset()
    
    def is_met(self) -> bool:
        """Check if composite condition is met."""
        met_conditions = [c.is_met() for c in self.conditions]
        
        if self.mode == "any":
            return any(met_conditions)
        else:  # mode == "all"
            return all(met_conditions)
    
    def __or__(self, other: BaseTermination) -> 'CompositeTermination':
        """Extend OR composition."""
        if isinstance(other, CompositeTermination) and other.mode == "any":
            return CompositeTermination(self.conditions + other.conditions, mode="any")
        else:
            return CompositeTermination(self.conditions + [other], mode="any")
    
    def __and__(self, other: BaseTermination) -> 'CompositeTermination':
        """Extend AND composition."""
        if isinstance(other, CompositeTermination) and other.mode == "all":
            return CompositeTermination(self.conditions + other.conditions, mode="all")
        else:
            return CompositeTermination(self.conditions + [other], mode="all")
