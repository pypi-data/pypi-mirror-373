"""
This module defines the Events interface for handling various events in the agent
"""
from typing import Protocol, Callable, Awaitable
from .payload import AgentEventPayload
from .context import AgentContext


class AgentEvents(Protocol):
    """
    Interface for handling various events in the agent.
    """
    
    def emitQueryCreated(self, event: AgentEventPayload) -> Awaitable[None]:
        """
        Emits an event when a query is created.
        
        Args:
            event: An object containing the data related to the created query.
        """
        ...
    
    def emitQueryCompleted(self, event: AgentEventPayload) -> Awaitable[None]:
        """
        Emits an event when a query is successfully completed.
        
        Args:
            event: An object containing the data related to the completed query.
        """
        ...
    
    def emitQueryFailed(self, event: AgentEventPayload) -> Awaitable[None]:
        """
        Emits an event when a query fails.
        
        Args:
            event: An object containing the data related to the failed query.
        """
        ...
    
    def emitEventCreated(self, event: AgentEventPayload) -> Awaitable[None]:
        """
        Emits an event when a generic event is created.
        
        Args:
            event: An object containing the data related to the created event.
        """
        ...


class AgentEventsImpl:
    """
    Concrete implementation of AgentEvents.
    """
    
    def __init__(self, context: AgentContext, emit: Callable[[AgentContext, str, AgentEventPayload], Awaitable[None]]):
        self.context = context
        self.emit = emit
    
    async def emitQueryCreated(self, event: AgentEventPayload) -> None:
        await self.emit(self.context, "queryCreated", event)
    
    async def emitQueryCompleted(self, event: AgentEventPayload) -> None:
        await self.emit(self.context, "queryCompleted", event)
    
    async def emitQueryFailed(self, event: AgentEventPayload) -> None:
        await self.emit(self.context, "queryFailed", event)
    
    async def emitEventCreated(self, event: AgentEventPayload) -> None:
        await self.emit(self.context, "eventCreated", event) 