"""
Interface of the context object used in the agent
"""
from dataclasses import dataclass
from typing import Any, List


@dataclass
class AgentContext:
    """
    Context object used in the agent.
    
    Attributes:
        params: Parameters passed to the context, can be of any type.
        query_id: A unique identifier for the query being processed.
        webhook_groups: An array of webhook group names associated with the context.
        agent_id: The unique identifier of the agent handling the context.
        agent_name: The name of the agent handling the context.
    """
    # Parameters passed to the context, can be of any type.
    params: Any
    
    # A unique identifier for the query being processed.
    query_id: str
    
    # An array of webhook group names associated with the context.
    webhook_groups: List[str]
    
    # The unique identifier of the agent handling the context.
    agent_id: str
    
    # The name of the agent handling the context.
    agent_name: str 