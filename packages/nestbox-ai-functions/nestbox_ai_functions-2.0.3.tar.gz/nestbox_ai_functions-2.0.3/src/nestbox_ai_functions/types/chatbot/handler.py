"""
Type definition for chatbot handlers.
"""
from typing import Any, Awaitable, Callable

from .context import ChatbotContext
from .events import ChatbotEvents


ChatbotHandler = Callable[[ChatbotContext, ChatbotEvents], Awaitable[Any]]
