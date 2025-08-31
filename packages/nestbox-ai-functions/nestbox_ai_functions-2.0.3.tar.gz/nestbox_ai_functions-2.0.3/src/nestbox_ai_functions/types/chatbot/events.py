"""
This module defines the Events interface for handling various events in the Chatbot
"""
from typing import Protocol, Callable, Awaitable

from .payload import ChatbotEventPayload
from .context import ChatbotContext


class ChatbotEvents(Protocol):
    """
    Protocol defining the events interface for chatbots.
    """
    
    def emitQueryCreated(self, event: ChatbotEventPayload) -> Awaitable[None]:
        """
        Emits an event when a query is created.
        
        Args:
            event: An object containing the data related to the created query.
        """
        ...
    
    def emitQueryCompleted(self, event: ChatbotEventPayload) -> Awaitable[None]:
        """
        Emits an event when a query is successfully completed.
        
        Args:
            event: An object containing the data related to the completed query.
        """
        ...
    
    def emitQueryFailed(self, event: ChatbotEventPayload) -> Awaitable[None]:
        """
        Emits an event when a query fails.
        
        Args:
            event: An object containing the data related to the failed query.
        """
        ...
    
    def emitEventCreated(self, event: ChatbotEventPayload) -> Awaitable[None]:
        """
        Emits an event when a generic event is created.
        
        Args:
            event: An object containing the data related to the created event.
        """
        ...


class ChatbotEventsImpl:
    """
    Concrete implementation of ChatbotEvents.
    """
    
    def __init__(self, context: ChatbotContext, emit: Callable[[ChatbotContext, str, ChatbotEventPayload], Awaitable[None]]):
        self.context = context
        self.emit = emit
    
    async def emitQueryCreated(self, event: ChatbotEventPayload) -> None:
        await self.emit(self.context, "queryCreated", event)
    
    async def emitQueryCompleted(self, event: ChatbotEventPayload) -> None:
        await self.emit(self.context, "queryCompleted", event)
    
    async def emitQueryFailed(self, event: ChatbotEventPayload) -> None:
        await self.emit(self.context, "queryFailed", event)
    
    async def emitEventCreated(self, event: ChatbotEventPayload) -> None:
        await self.emit(self.context, "eventCreated", event)
