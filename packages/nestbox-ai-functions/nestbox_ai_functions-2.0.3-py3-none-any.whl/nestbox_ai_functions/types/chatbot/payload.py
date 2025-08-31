"""
Base interface for all chatbot event payloads (user-provided portion)
"""
from dataclasses import dataclass
from typing import Any, Generic, TypeVar, Optional

T = TypeVar('T')


@dataclass
class ChatbotEventPayload(Generic[T]):
    """
    Base class for chatbot event payloads.
    
    Attributes:
        data: Additional data specific to the event.
    """
    
    # Additional data specific to the event
    data: Optional[T] = None
