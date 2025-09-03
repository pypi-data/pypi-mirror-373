"""Subagent hierarchy tracking utility for tool usage display."""

import logging
from typing import Dict, Optional, Callable, Any, List
from dataclasses import dataclass, field
import uuid

from ...debug_logger import debug_logger


@dataclass
class AgentInfo:
    """Information about an agent in the hierarchy."""
    agent_id: str
    agent_level: int
    parent_id: Optional[str] = None
    display_name: Optional[str] = None
    created_at: Optional[float] = None


class SubagentTracker:
    """
    Tracks agent hierarchy levels and provides methods to create hierarchy-aware callbacks.
    
    This utility manages the relationship between main agents and subagents, allowing
    for proper indentation and visual hierarchy in tool usage display.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the subagent tracker.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Track agent hierarchy
        self.agents: Dict[str, AgentInfo] = {}
        self.active_agent_stack: List[str] = []  # Stack of currently active agents
        
        # Create main agent (level 0)
        self.main_agent_id = "main_agent"
        self.register_agent(self.main_agent_id, level=0, display_name="Main Agent")
        self.set_active_agent(self.main_agent_id)
        
        debug_logger.log_event("subagent_tracker_initialized", 
                              main_agent_id=self.main_agent_id)
    
    def register_agent(
        self, 
        agent_id: str, 
        level: int, 
        parent_id: Optional[str] = None,
        display_name: Optional[str] = None
    ) -> AgentInfo:
        """
        Register a new agent in the hierarchy.
        
        Args:
            agent_id: Unique identifier for the agent
            level: Hierarchy level (0 = main agent, 1 = subagent, etc.)
            parent_id: ID of the parent agent (optional)
            display_name: Human-readable name for the agent (optional)
            
        Returns:
            AgentInfo object for the registered agent
        """
        import time
        
        agent_info = AgentInfo(
            agent_id=agent_id,
            agent_level=level,
            parent_id=parent_id,
            display_name=display_name or f"Agent-{level}",
            created_at=time.time()
        )
        
        self.agents[agent_id] = agent_info
        
        debug_logger.log_event("agent_registered",
                              agent_id=agent_id,
                              level=level,
                              parent_id=parent_id,
                              display_name=display_name)
        
        self.logger.debug(f"Registered agent: {agent_id} at level {level}")
        return agent_info
    
    def create_subagent(self, parent_id: Optional[str] = None, display_name: Optional[str] = None) -> str:
        """
        Create a new subagent with automatic ID generation.
        
        Args:
            parent_id: ID of the parent agent (defaults to current active agent)
            display_name: Human-readable name for the subagent
            
        Returns:
            The agent ID of the created subagent
        """
        if parent_id is None:
            parent_id = self.get_current_agent_id()
        
        parent_info = self.agents.get(parent_id)
        if not parent_info:
            self.logger.warning(f"Parent agent {parent_id} not found, using main agent")
            parent_id = self.main_agent_id
            parent_info = self.agents[parent_id]
        
        # Generate unique agent ID
        subagent_id = f"subagent_{uuid.uuid4().hex[:8]}"
        
        # Create subagent at parent level + 1
        subagent_level = parent_info.agent_level + 1
        
        self.register_agent(
            agent_id=subagent_id,
            level=subagent_level,
            parent_id=parent_id,
            display_name=display_name or f"Subagent-{subagent_level}"
        )
        
        debug_logger.log_event("subagent_created",
                              subagent_id=subagent_id,
                              parent_id=parent_id,
                              level=subagent_level)
        
        return subagent_id
    
    def set_active_agent(self, agent_id: str) -> None:
        """
        Set the currently active agent.
        
        Args:
            agent_id: ID of the agent to set as active
        """
        if agent_id not in self.agents:
            self.logger.warning(f"Agent {agent_id} not registered")
            return
        
        # Update the active agent stack
        if not self.active_agent_stack or self.active_agent_stack[-1] != agent_id:
            self.active_agent_stack.append(agent_id)
        
        debug_logger.log_event("active_agent_changed",
                              new_agent_id=agent_id,
                              stack_depth=len(self.active_agent_stack))
        
        self.logger.debug(f"Active agent set to: {agent_id}")
    
    def pop_active_agent(self) -> Optional[str]:
        """
        Pop the current active agent from the stack and return to the previous agent.
        
        Returns:
            The ID of the previous active agent, or None if no previous agent
        """
        if len(self.active_agent_stack) > 1:
            popped_agent = self.active_agent_stack.pop()
            current_agent = self.active_agent_stack[-1]
            
            debug_logger.log_event("active_agent_popped",
                                  popped_agent_id=popped_agent,
                                  current_agent_id=current_agent,
                                  stack_depth=len(self.active_agent_stack))
            
            self.logger.debug(f"Popped agent {popped_agent}, now active: {current_agent}")
            return current_agent
        else:
            self.logger.debug("Cannot pop main agent from stack")
            return None
    
    def get_current_agent_id(self) -> str:
        """Get the ID of the currently active agent."""
        return self.active_agent_stack[-1] if self.active_agent_stack else self.main_agent_id
    
    def get_current_agent_info(self) -> Optional[AgentInfo]:
        """Get the AgentInfo for the currently active agent."""
        current_id = self.get_current_agent_id()
        return self.agents.get(current_id)
    
    def get_agent_info(self, agent_id: str) -> Optional[AgentInfo]:
        """Get AgentInfo for a specific agent."""
        return self.agents.get(agent_id)
    
    def get_agent_hierarchy_path(self, agent_id: str) -> List[AgentInfo]:
        """
        Get the full hierarchy path from root to the specified agent.
        
        Args:
            agent_id: ID of the target agent
            
        Returns:
            List of AgentInfo objects from root to target agent
        """
        path = []
        current_id = agent_id
        
        while current_id:
            agent_info = self.agents.get(current_id)
            if not agent_info:
                break
            
            path.insert(0, agent_info)
            current_id = agent_info.parent_id
        
        return path
    
    def is_subagent(self, agent_id: Optional[str] = None) -> bool:
        """
        Check if the specified agent (or current agent) is a subagent.
        
        Args:
            agent_id: ID of the agent to check (defaults to current agent)
            
        Returns:
            True if the agent is a subagent (level > 0)
        """
        if agent_id is None:
            agent_id = self.get_current_agent_id()
        
        agent_info = self.agents.get(agent_id)
        return agent_info.agent_level > 0 if agent_info else False
    
    def get_hierarchy_context(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get hierarchy context information for tool event data.
        
        Args:
            agent_id: ID of the agent (defaults to current agent)
            
        Returns:
            Dictionary with hierarchy information for tool events
        """
        if agent_id is None:
            agent_id = self.get_current_agent_id()
        
        agent_info = self.agents.get(agent_id)
        if not agent_info:
            # Fallback for unknown agents
            return {
                "agent_id": agent_id,
                "agent_level": 0,
                "is_subagent": False,
                "parent_id": None,
                "display_name": "Unknown Agent"
            }
        
        return {
            "agent_id": agent_info.agent_id,
            "agent_level": agent_info.agent_level,
            "is_subagent": agent_info.agent_level > 0,
            "parent_id": agent_info.parent_id,
            "display_name": agent_info.display_name
        }
    
    def create_hierarchy_aware_callback(
        self,
        base_callback: Callable,
        agent_id: Optional[str] = None
    ) -> Callable:
        """
        Create a hierarchy-aware wrapper around an existing callback.
        
        Args:
            base_callback: The original callback to wrap
            agent_id: ID of the agent this callback belongs to (defaults to current agent)
            
        Returns:
            A wrapped callback that includes hierarchy information
        """
        if agent_id is None:
            agent_id = self.get_current_agent_id()
        
        async def hierarchy_aware_callback(event_name: str, agent: Any, *args, **kwargs: Any) -> None:
            """Wrapped callback that adds hierarchy information."""
            # Get hierarchy context
            hierarchy_context = self.get_hierarchy_context(agent_id)
            
            debug_logger.log_event("hierarchy_aware_callback_invoked",
                                  event_name_param=event_name,
                                  agent_id=agent_id,
                                  agent_level=hierarchy_context["agent_level"],
                                  is_subagent=hierarchy_context["is_subagent"])
            
            # Handle both interface styles (positional kwargs_dict vs **kwargs)
            if args and isinstance(args[0], dict):
                # New interface: modify the kwargs_dict
                kwargs_dict = args[0].copy()
                kwargs_dict.update(hierarchy_context)
                modified_args = (kwargs_dict,) + args[1:]
                await base_callback(event_name, agent, *modified_args, **kwargs)
            else:
                # Legacy interface: add to **kwargs
                modified_kwargs = kwargs.copy()
                modified_kwargs.update(hierarchy_context)
                await base_callback(event_name, agent, *args, **modified_kwargs)
        
        return hierarchy_aware_callback
    
    def clear_agents(self) -> None:
        """Clear all agents except the main agent."""
        self.agents.clear()
        self.active_agent_stack.clear()
        
        # Recreate main agent
        self.register_agent(self.main_agent_id, level=0, display_name="Main Agent")
        self.set_active_agent(self.main_agent_id)
        
        debug_logger.log_event("agents_cleared")
        self.logger.debug("All agents cleared, main agent recreated")


# Global instance for easy access
_global_tracker: Optional[SubagentTracker] = None


def get_global_tracker() -> SubagentTracker:
    """Get the global subagent tracker instance."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = SubagentTracker()
    return _global_tracker


def create_subagent_callback(
    base_callback: Callable,
    agent_id: Optional[str] = None,
    tracker: Optional[SubagentTracker] = None
) -> Callable:
    """
    Convenience function to create a hierarchy-aware callback.
    
    Args:
        base_callback: The original callback to wrap
        agent_id: ID of the agent this callback belongs to (defaults to current agent)
        tracker: SubagentTracker instance (defaults to global tracker)
        
    Returns:
        A wrapped callback that includes hierarchy information
    """
    if tracker is None:
        tracker = get_global_tracker()
    
    return tracker.create_hierarchy_aware_callback(base_callback, agent_id)