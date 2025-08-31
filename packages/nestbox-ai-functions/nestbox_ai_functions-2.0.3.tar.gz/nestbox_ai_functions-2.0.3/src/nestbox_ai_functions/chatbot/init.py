import sys
import asyncio
from typing import Any

# Ensure UTF-8 encoding for stdout
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from ..types.chatbot.context import ChatbotContext
from ..types.chatbot.events import ChatbotEventsImpl
from ..types.chatbot.handler import ChatbotHandler
from ..common.stream_manager import StreamManager, StreamManagerOptions

CHAT_ID = sys.argv[1] if len(sys.argv) > 1 else None

def init_chatbot(chatbot: ChatbotHandler):
    if not CHAT_ID:
        print("Usage: python chatbot.py <CHAT_ID>")
        sys.exit(1)

    def on_task(context_data: Any):
        context = ChatbotContext(
            params=context_data.get("params", {}),
            query_id=context_data.get("queryId", ""),
            chatbot_id=context_data.get("chatbotId", ""),
            chatbot_name=context_data.get("chatbotName", ""),
            webhook_groups=context_data.get("webhookGroups", []),
            messages=context_data.get("messages", []),
        )

        events = ChatbotEventsImpl(context, stream_manager.emit)

        # Wrap chatbot execution in async context to handle both sync and async errors
        async def execute_chatbot():
            try:
                await chatbot(context, events)
            except Exception as e:
                print("Error in chatbot execution:", e)
                await events.emitQueryFailed({"data": str(e)})
        
        asyncio.create_task(execute_chatbot())

    stream_manager = StreamManager(StreamManagerOptions(
        id=CHAT_ID,
        on_task=on_task,
        log_prefix="Chatbot"
    ))

    stream_manager.start()
