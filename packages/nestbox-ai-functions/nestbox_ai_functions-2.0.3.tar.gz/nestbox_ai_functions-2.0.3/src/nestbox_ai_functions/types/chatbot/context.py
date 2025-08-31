"""
Interface of the context object used in the chatbot
"""
from dataclasses import dataclass
from typing import Any, List

from .message import ChatbotMessage


@dataclass
class ChatbotContext:
    """
    Context object used in the chatbot.
    
    Attributes:
        messages: The chatbot messages.
        params: Parameters passed to the context, can be of any type.
        query_id: A unique identifier for the query being processed.
        webhook_groups: An array of webhook group names associated with the context.
        chatbot_id: The unique identifier of the chatbot handling the context.
        chatbot_name: The name of the chatbot handling the context.
    """
    # The chatbot messages
    messages: List[ChatbotMessage]
    
    # Parameters passed to the context, can be of any type.
    params: Any
    
    # A unique identifier for the query being processed.
    query_id: str
    
    # An array of webhook group names associated with the context.
    webhook_groups: List[str]
    
    # The unique identifier of the chatbot handling the context.
    chatbot_id: str
    
    # The name of the chatbot handling the context.
    chatbot_name: str
