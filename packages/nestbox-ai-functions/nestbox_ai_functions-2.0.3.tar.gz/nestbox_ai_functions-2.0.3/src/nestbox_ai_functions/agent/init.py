import sys
import asyncio
from typing import Any

# Ensure UTF-8 encoding for stdout
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from ..types.agent.context import AgentContext
from ..types.agent.events import AgentEventsImpl
from ..types.agent.handler import AgentHandler
from ..common.stream_manager import StreamManager, StreamManagerOptions

AGENT_ID = sys.argv[1] if len(sys.argv) > 1 else None

def init_agent(agent: AgentHandler):
    if not AGENT_ID:
        print("Usage: python agent.py <AGENT_ID>")
        sys.exit(1)

    def on_task(context_data: Any):
        context = AgentContext(
            params=context_data.get("params", {}),
            query_id=context_data.get("queryId", ""),
            webhook_groups=context_data.get("webhookGroups", []),
            agent_id=context_data.get("agentId", ""),
            agent_name=context_data.get("agentName", "")
        )

        events = AgentEventsImpl(context, stream_manager.emit)

        # Wrap agent execution in async context to handle both sync and async errors
        async def execute_agent():
            try:
                await agent(context, events)
            except Exception as e:
                print("Agent execution failed:", e)
                await events.emitQueryFailed({"data": str(e)})
        
        asyncio.create_task(execute_agent())

    stream_manager = StreamManager(StreamManagerOptions(
        id=AGENT_ID,
        on_task=on_task,
        log_prefix="Agent"
    ))

    stream_manager.start()
