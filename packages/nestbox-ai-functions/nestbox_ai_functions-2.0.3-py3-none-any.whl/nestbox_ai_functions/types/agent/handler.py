"""
Agent handler type definition
"""
from typing import Callable, Any
from .context import AgentContext
from .events import AgentEvents

# Type alias for agent handler function
AgentHandler = Callable[[AgentContext, AgentEvents], Any] 