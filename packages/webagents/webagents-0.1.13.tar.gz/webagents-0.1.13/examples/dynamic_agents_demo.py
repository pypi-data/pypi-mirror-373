#!/usr/bin/env python3
"""
Dynamic Agents Demo - Robutler V2.0

Demonstrates the dynamic agent system that fetches agent configurations
from the Robutler portal API and creates BaseAgent instances on-demand.

Usage:
    python examples/dynamic_agents_demo.py

Environment variables required:
    SERVICE_TOKEN - Token for accessing the Robutler portal API
    ROBUTLER_INTERNAL_API_URL - Portal URL (default: https://robutler.ai)
"""

import os
import asyncio
import uvicorn
from webagents.server.core.app import create_server

async def main():
    """Create and run a server with dynamic agents support"""
    
    # Check for required environment variables
    service_token = os.getenv("SERVICE_TOKEN")
    if not service_token:
        print("⚠️ SERVICE_TOKEN not configured!")
        print("Dynamic agents require a service token to fetch agent configurations from the portal.")
        print("Set SERVICE_TOKEN environment variable and try again.")
        return
    
    print("🚀 Robutler V2.0 Dynamic Agents Demo")
    print("=" * 50)
    print(f"Portal URL: {os.getenv('ROBUTLER_INTERNAL_API_URL', 'https://robutler.ai')}")
    print(f"Service Token: ✅ Configured")
    print()
    
    # Create server with dynamic agents (no static agents)
    # The server will automatically use the DynamicAgentFactory for portal-based agent resolution
    server = create_server(
        agents=None,  # No static agents
        dynamic_agents=None,  # Use default portal-based resolver
        title="Dynamic Agents Demo",
        description="Robutler V2.0 server with portal-based dynamic agent creation"
    )
    
    print("✅ Server created with dynamic agent support")
    print()
    print("📋 Available endpoints:")
    print("  GET  /                    - Server info")
    print("  GET  /health              - Health check")
    print("  GET  /stats               - Server statistics")
    print("  GET  /{agent_name}        - Agent info (dynamic)")
    print("  POST /{agent_name}/chat/completions - Chat with agent (dynamic)")
    print()
    print("🔧 Dynamic agent resolution:")
    print("  1. Request comes for /{agent_name}/chat/completions")
    print("  2. DynamicAgentFactory.get_or_create_agent(agent_name) is called")
    print("  3. Factory fetches agent config from portal API")
    print("  4. BaseAgent instance is created with portal configuration")
    print("  5. Agent handles the chat completion request")
    print()
    print("💡 Example usage:")
    print("  # Get agent info")
    print("  curl http://localhost:8000/my-agent")
    print()
    print("  # Chat with agent")
    print("  curl -X POST http://localhost:8000/my-agent/chat/completions \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"model\": \"my-agent\", \"messages\": [{\"role\": \"user\", \"content\": \"Hello!\"}]}'")
    print()
    print("🌐 Starting server on http://localhost:8000")
    print("   Press Ctrl+C to stop")
    
    # Run the server
    config = uvicorn.Config(
        app=server.fastapi_app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
    server_instance = uvicorn.Server(config)
    
    try:
        await server_instance.serve()
    except KeyboardInterrupt:
        print("\n👋 Shutting down server")

if __name__ == "__main__":
    asyncio.run(main()) 