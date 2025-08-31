import sys
import grpc.aio
import agent_pb2_grpc
from typing import Optional

GRPC_SERVER_URL = sys.argv[2] if len(sys.argv) > 2 else "localhost:50051"

_client: Optional[agent_pb2_grpc.AgentServiceStub] = None

def get_client() -> agent_pb2_grpc.AgentServiceStub:
    global _client
    if not _client:
        channel = grpc.aio.insecure_channel(GRPC_SERVER_URL)
        _client = agent_pb2_grpc.AgentServiceStub(channel)
    return _client

def close_client() -> None:
    global _client
    if _client:
        _client._channel.close()
        _client = None

async def wait_for_server_ready(timeout: int = 2000) -> None:
    """Wait for the gRPC server to be ready"""
    import asyncio
    
    channel = grpc.aio.insecure_channel(GRPC_SERVER_URL)
    try:
        await asyncio.wait_for(channel.channel_ready(), timeout=timeout / 1000)
    finally:
        await channel.close()
