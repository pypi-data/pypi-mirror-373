# nestbox_ai/chatbot/hooks/use_chatbot.py
from ..types.chatbot.handler import ChatbotHandler

def use_chatbot(chatbot: ChatbotHandler) -> ChatbotHandler:
    """
    Returns the provided chatbot handler function.

    Args:
        chatbot (ChatbotHandler): The chatbot function to be used.

    Returns:
        ChatbotHandler: The same chatbot function.
    """
    return chatbot
