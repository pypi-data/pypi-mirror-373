"""
Robutler V2.0 Server Package

FastAPI server implementation with OpenAI compatibility,
streaming support, and comprehensive agent management.
"""

# Import moved to avoid circular dependency
# from .core.app import RobutlerServer, create_server
from .models import (
    ChatCompletionRequest,
    OpenAIResponse, 
    OpenAIStreamChunk,
    AgentInfoResponse,
    ServerInfo,
    HealthResponse
)

__all__ = [
    # 'RobutlerServer',
    # 'create_server', 
    'ChatCompletionRequest',
    'OpenAIResponse',
    'OpenAIStreamChunk', 
    'AgentInfoResponse',
    'ServerInfo',
    'HealthResponse'
]
