"""
Chatbot message types
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ChatbotMessage:
    """
    Represents a message in the chatbot conversation.
    
    Attributes:
        id: The unique identifier for the message.
        content: The content of the message.
        sender: Sender of the message.
        timestamp: Timestamp of the message.
        attachments: Optional attachments to the message.
    """
    
    # The unique identifier for the message.
    # This is a required field.
    id: str
    
    # The content of the message.
    # This is a required field.
    content: str
    
    # Sender of the message.
    sender: str
    
    # Timestamp of the message.
    timestamp: int
    
    # Optional attachments to the message.
    attachments: Optional[List[str]] = None
