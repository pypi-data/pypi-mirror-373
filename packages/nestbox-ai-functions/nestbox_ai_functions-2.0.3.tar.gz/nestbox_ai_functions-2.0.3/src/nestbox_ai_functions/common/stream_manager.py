import asyncio
import json
import random
import time
import sys
from typing import Any, Callable, Dict, Awaitable

import grpc
import agent_pb2
import agent_pb2_grpc

from .grpc_client import get_client, close_client, wait_for_server_ready
from .event_configs import EVENT_CONFIGS

# Ensure UTF-8 encoding for stdout
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

class StreamManagerOptions:
    def __init__(self, id: str, on_task: Callable[[Any], None], log_prefix: str):
        self.id = id
        self.on_task = on_task
        self.log_prefix = log_prefix

class StreamManager:
    def __init__(self, options: StreamManagerOptions):
        self.options = options
        self.active_call: Any = None
        self.backoff_ms = 1000
        self.MAX_BACKOFF = 10000

    async def send_message_to_server(self, payload: Any) -> None:
        """Send a message to the gRPC server"""
        message = agent_pb2.ScriptResponse(
            data=json.dumps(payload or {}).encode("utf-8"),
            timestamp=int(time.time() * 1000),
        )
        
        try:
            client = get_client()
            res = await client.SendResult(message)
            print("[OK] Result sent:", res.ok)
        except Exception as e:
            print(f"[ERROR] Failed to send result: {e}")
            raise

    async def emit(self, context: Any, event_key: str, payload: Any) -> Dict[str, Any]:
        """Emit an event with the given payload"""
        config = EVENT_CONFIGS[event_key]
        complete_payload = {
            **payload,
            "eventType": config["eventType"],
            "webhookListener": config["webhookListener"],
            "webhookGroups": context.webhook_groups,
            "queryId": context.query_id,
            "params": context.params,
            # Include conditional fields based on context type
            **({"agentId": context.agent_id} if hasattr(context, 'agent_id') and context.agent_id else {}),
            **({"chatbotId": context.chatbot_id} if hasattr(context, 'chatbot_id') and context.chatbot_id else {}),
            **({"messages": context.messages} if hasattr(context, 'messages') and context.messages else {}),
        }

        await self.send_message_to_server(complete_payload)
        return complete_payload

    async def start_task_stream(self) -> None:
        """Start the task stream"""
        if self.active_call:
            return

        try:
            await wait_for_server_ready(2000)
        except Exception:
            await self.schedule_reconnect()
            return

        client = get_client()
        call = client.TaskStream(agent_pb2.AgentIdentity(agentId=self.options.id))
        self.active_call = call
        self.backoff_ms = 1000  # reset backoff

        try:
            async for task in call:
                context_data = json.loads(task.payload.decode("utf-8"))
                print(f"Received: {context_data}")
                self.options.on_task(context_data)
        except Exception as e:
            self.on_disconnected(e)

    def on_disconnected(self, reason: Any = None) -> None:
        """Handle disconnection from the stream"""
        if self.active_call:
            self.active_call = None
        print(f"TaskStream disconnected: {str(reason) if reason else ''}")
        asyncio.create_task(self.schedule_reconnect())

    async def schedule_reconnect(self) -> None:
        """Schedule a reconnection with exponential backoff"""
        jitter = random.randint(0, 300)
        wait = min(self.MAX_BACKOFF, self.backoff_ms) + jitter
        print(f"Reconnecting in {wait}ms")
        await asyncio.sleep(wait / 1000)
        self.backoff_ms = min(self.MAX_BACKOFF, self.backoff_ms * 2)
        await self.start_task_stream()

    def start(self) -> None:
        """Start the stream manager"""
        print(f"[START] {self.options.log_prefix} {self.options.id} starting")
        self.setup_process_handlers()
        
        # Start the event loop
        try:
            asyncio.run(self._run_forever())
        except KeyboardInterrupt:
            print(f"{self.options.log_prefix} exiting")
            self.cleanup()
    
    async def _run_forever(self) -> None:
        """Run the stream manager forever"""
        await self.start_task_stream()
        # Keep the event loop running
        while True:
            await asyncio.sleep(1)

    def cleanup(self) -> None:
        """Clean up resources"""
        if self.active_call:
            self.active_call.cancel()
            self.active_call = None
        close_client()

    def setup_process_handlers(self) -> None:
        """Setup process signal handlers"""
        import signal
        
        def cleanup():
            print(f"{self.options.log_prefix} exiting")
            self.cleanup()

        def handle_sigint(signum, frame):
            print("Received SIGINT, cleaning up...")
            cleanup()
            exit(0)

        def handle_sigterm(signum, frame):
            print("Received SIGTERM, cleaning up...")
            cleanup()
            exit(0)

        signal.signal(signal.SIGINT, handle_sigint)
        signal.signal(signal.SIGTERM, handle_sigterm)
