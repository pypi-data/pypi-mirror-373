# nestbox_ai/agent/hooks/use_agent.py
from ..types.agent.handler import AgentHandler

def use_agent(agent: AgentHandler) -> AgentHandler:
    """
    Returns the provided agent handler function.

    Args:
        agent (AgentHandler): The agent function to be used.

    Returns:
        AgentHandler: The same agent function.
    """
    return agent
