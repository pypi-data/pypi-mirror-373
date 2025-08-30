"""
Round-robin orchestration pattern.

This module provides the RoundRobinOrchestrator that cycles through agents 
in fixed order, giving each agent access to the complete shared conversation history.
"""

from typing import List, Union, Dict, Any
from ..agents import BaseAgent
from ..messages import Message, UserMessage
from ..types import AgentResponse
from ._base import BaseOrchestrator
from .termination import BaseTermination


class RoundRobinOrchestrator(BaseOrchestrator):
    """
    Round-robin orchestration pattern.
    
    Cycles through agents in fixed order, giving each agent access to
    the complete shared conversation history.
    """
    
    def __init__(
        self,
        agents: List[BaseAgent],
        termination: BaseTermination,
        max_iterations: int = 50
    ):
        super().__init__(agents, termination, max_iterations)
        self.current_agent_index = 0
    
    def select_next_agent(self) -> BaseAgent:
        """Select next agent in round-robin order."""
        agent = self.agents[self.current_agent_index]
        # Fix: increment BEFORE returning, not after
        self.current_agent_index = (self.current_agent_index + 1) % len(self.agents)
        return agent
    
    def prepare_context_for_agent(self, agent: BaseAgent) -> str:
        """Format full shared conversation history as a single context string."""
        if not self.shared_messages:
            return "You are part of a team taking turns to collaboratively addressing a task. It is now your turn. "

        context = "You are part of a team taking turns to collaboratively addressing a task. Here's the progress/history so far:\n\n"
        for msg in self.shared_messages:
            context += f"{msg}\n"
        context += "\nIt is now your turn."
        return context
    
    def update_shared_state(self, result: AgentResponse) -> None:
        """Add new messages to shared conversation."""
        # With context as string, agent responses should only contain new messages
        # Skip the first message which is the user context we sent
        new_messages = result.messages[1:] if len(result.messages) > 1 else []
        self.shared_messages.extend(new_messages)
    
    def _get_pattern_metadata(self) -> Dict[str, Any]:
        """Get round-robin specific metadata."""
        base_metadata = super()._get_pattern_metadata()
        base_metadata.update({
            "cycles_completed": self.iteration_count // len(self.agents),
            "current_agent_index": self.current_agent_index,
            "agents_order": [agent.name for agent in self.agents]
        })
        return base_metadata
    
    def _reset_for_run(self) -> None:
        """Reset round-robin state."""
        super()._reset_for_run()
        self.current_agent_index = 0