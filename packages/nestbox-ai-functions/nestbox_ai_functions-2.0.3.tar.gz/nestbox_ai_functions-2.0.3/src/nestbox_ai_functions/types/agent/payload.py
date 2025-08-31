"""
Base interface for all event payloads (user-provided portion)
"""
from dataclasses import dataclass
from typing import Any, Generic, TypeVar, Optional

T = TypeVar('T')


@dataclass
class AgentEventPayload(Generic[T]):
    """
    Base class for all event payloads (user-provided portion).
    
    Attributes:
        data: Additional data specific to the event.
    """
    # Additional data specific to the event
    data: Optional[T] = None 