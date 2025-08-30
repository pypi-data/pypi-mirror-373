"""
Composite termination condition for combining multiple conditions.
"""

from typing import List, Optional, Sequence
from ...messages import Message
from ...types import StopMessage
from ._base import BaseTermination


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