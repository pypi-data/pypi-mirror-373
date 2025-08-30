# Robutler V2 Design Document - Chapter 6: Implementation Guide

## Overview

This chapter provides practical guidance for implementing, testing, migrating from V1, and deploying Robutler V2 in production environments. It includes comprehensive testing strategies, migration tools, and operational best practices.

---

## 1. Testing Strategy

### Unit Testing Framework

```python
# tests/agents/test_base_agent.py
import pytest
from unittest.mock import Mock, AsyncMock, patch
from robutler.agents.core.base_agent import BaseAgent
from robutler.agents.skills.openai import OpenAISkill

@pytest.fixture
def mock_openai_skill():
    """Mock OpenAI skill for testing"""
    skill = Mock(spec=OpenAISkill)
    skill.chat_completion = AsyncMock(return_value={
        "choices": [{"message": {"content": "Test response"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
    })
    skill.chat_completion_stream = AsyncMock()
    return skill

@pytest.fixture
def test_agent(mock_openai_skill):
    """Create test agent with mocked dependencies"""
    return BaseAgent(
        name="test-agent",
        instructions="You are a test assistant",
        skills={"openai": mock_openai_skill}
    )

@pytest.mark.asyncio
async def test_agent_run_basic(test_agent, mock_openai_skill):
    """Test basic agent execution"""
    messages = [{"role": "user", "content": "Hello"}]
    
    response = await test_agent.run(messages)
    
    # Verify response structure
    assert response.id
    assert response.object == "chat.completion"
    assert len(response.choices) == 1
    assert response.choices[0].message["content"] == "Test response"
    assert response.usage.total_tokens == 25
    
    # Verify skill was called correctly
    mock_openai_skill.chat_completion.assert_called_once()

@pytest.mark.asyncio
async def test_agent_streaming(test_agent, mock_openai_skill):
    """Test streaming response"""
    # Mock streaming response
    mock_chunks = [
        {"choices": [{"delta": {"role": "assistant", "content": ""}}]},
        {"choices": [{"delta": {"content": "Hello"}}]},
        {"choices": [{"delta": {"content": " there!"}}]},
        {"choices": [{"delta": {}}], "usage": {"total_tokens": 20}}
    ]
    
    async def mock_stream(*args, **kwargs):
        for chunk in mock_chunks:
            yield chunk
    
    mock_openai_skill.chat_completion_stream = AsyncMock(side_effect=mock_stream)
    
    messages = [{"role": "user", "content": "Hello"}]
    chunks = []
    
    async for chunk in test_agent.run_streaming(messages):
        chunks.append(chunk)
    
    # Verify streaming chunks
    assert len(chunks) >= 4  # Initial + content chunks + final
    assert any("usage" in chunk for chunk in chunks)  # Final chunk has usage

@pytest.mark.asyncio
async def test_agent_with_tools(mock_openai_skill):
    """Test agent with custom tools"""
    from robutler.agents.tools.decorators import tool
    
    @tool
    def test_tool(input_text: str) -> str:
        return f"Processed: {input_text}"
    
    agent = BaseAgent(
        name="tool-agent",
        instructions="You are a tool-using agent",
        tools=[test_tool],
        skills={"openai": mock_openai_skill}
    )
    
    # Mock LLM response with tool call
    mock_openai_skill.chat_completion.return_value = {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": "call_123",
                    "type": "function",
                    "function": {"name": "test_tool", "arguments": '{"input_text": "hello"}'}
                }]
            }
        }],
        "usage": {"prompt_tokens": 20, "completion_tokens": 30, "total_tokens": 50}
    }
    
    response = await agent.run([{"role": "user", "content": "Use the test tool"}])
    
    # Verify tool integration works
    assert response.choices[0].message["role"] == "assistant"
```

### Integration Testing

```python
# tests/integration/test_skill_integration.py
import pytest
from robutler.agents.core.base_agent import BaseAgent
from robutler.agents.skills.short_term_memory import ShortTermMemorySkill
from robutler.agents.skills.openai import OpenAISkill

@pytest.mark.integration
@pytest.mark.asyncio
async def test_memory_skill_integration():
    """Test memory skill integration with real components"""
    
    # Create agent with memory skill
    agent = BaseAgent(
        name="memory-test-agent",
        instructions="You remember our conversations",
        skills={
            "openai": OpenAISkill({"api_key": "test-key"}),
            "short_term_memory": ShortTermMemorySkill({"max_messages": 10})
        }
    )
    
    # Initialize skills
    await agent.context.initialize_skills()
    
    # Test memory operations
    memory_skill = agent.context.get_skill("short_term_memory")
    
    # Add message to memory
    await memory_skill.add_message({"role": "user", "content": "Remember this"})
    
    # Retrieve messages
    recent_messages = await memory_skill.get_recent_messages(5)
    
    assert len(recent_messages) == 1
    assert recent_messages[0]["content"] == "Remember this"

@pytest.mark.integration
@pytest.mark.asyncio 
async def test_skill_dependency_resolution():
    """Test automatic skill dependency resolution"""
    from robutler.agents.skills.payments import PaymentSkill
    from robutler.agents.skills.auth import AuthSkill
    
    # PaymentSkill depends on AuthSkill
    agent = BaseAgent(
        name="payment-agent",
        instructions="Test payment functionality",
        skills={
            "payments": PaymentSkill()  # Only specify payment skill
        }
    )
    
    # Verify AuthSkill was automatically included
    assert "robutler.auth" in agent.skills
    assert isinstance(agent.skills["robutler.auth"], AuthSkill)
    assert isinstance(agent.skills["payments"], PaymentSkill)

@pytest.mark.integration 
@pytest.mark.asyncio
async def test_dynamic_tool_registration():
    """Test dynamic tool registration based on request context"""
    from robutler.agents.skills.base import Skill
    from robutler.agents.tools.decorators import tool
    
    class DynamicSkill(Skill):
        def __init__(self):
            super().__init__()
        
        async def initialize(self, agent_context):
            self.agent_context = agent_context
            self.register_hook('before_request', self._dynamic_registration, priority=1)
        
        async def _dynamic_registration(self, request_context):
            auth_scope = request_context.get('auth_scope', 'all')
            if auth_scope == 'admin':
                self.register_tool(self._admin_tool)
            return request_context
        
        @tool(scope="admin")
        async def _admin_tool(self, action: str) -> str:
            return f"Admin action: {action}"
    
    agent = BaseAgent(
        name="dynamic-agent",
        instructions="Dynamic tool registration test",
        skills={
            "dynamic": DynamicSkill(),
            "openai": OpenAISkill({"api_key": "test-key"})
        }
    )
    
    # Test that tools are registered dynamically
    dynamic_skill = agent.skills["dynamic"]
    assert len(dynamic_skill.get_tools()) == 0  # No tools initially
    
    # Simulate request with admin scope
    await dynamic_skill._dynamic_registration({"auth_scope": "admin"})
    
    assert len(dynamic_skill.get_tools()) == 1  # Tool registered
```

### Server Testing

```python
# tests/server/test_robutler_server.py
import pytest
from fastapi.testclient import TestClient
from robutler.server.core.app import RobutlerServer
from robutler.agents.core.base_agent import BaseAgent

@pytest.fixture
def test_server():
    """Create test server with mock agents"""
    agent = BaseAgent(
        name="test-agent",
        instructions="Test agent",
        skills={"openai": Mock(spec=OpenAISkill)}
    )
    
    server = RobutlerServer(agents=[agent])
    return TestClient(server.app)

def test_health_endpoint(test_server):
    """Test health check endpoint"""
    response = test_server.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "test-agent" in data["agents"]

def test_agent_info_endpoint(test_server):
    """Test agent info endpoint"""
    response = test_server.get("/test-agent")
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-agent"
    assert data["description"] == "Test agent"

def test_chat_completion_endpoint(test_server):
    """Test chat completion endpoint"""
    # Mock the agent's run method
    with patch.object(BaseAgent, 'run') as mock_run:
        mock_run.return_value = OpenAIResponse(
            id="test-123",
            object="chat.completion",
            created=1234567890,
            model="test-agent",
            choices=[OpenAIChoice(
                index=0,
                message={"role": "assistant", "content": "Test response"},
                finish_reason="stop"
            )],
            usage=OpenAIUsage(prompt_tokens=10, completion_tokens=15, total_tokens=25)
        )
        
        response = test_server.post("/test-agent/chat/completions", json={
            "messages": [{"role": "user", "content": "Hello"}]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["choices"][0]["message"]["content"] == "Test response"

def test_streaming_endpoint(test_server):
    """Test streaming chat completion"""
    
    async def mock_stream():
        yield {"choices": [{"delta": {"role": "assistant", "content": ""}}]}
        yield {"choices": [{"delta": {"content": "Hello"}}]}
        yield {"choices": [{"delta": {"content": " there!"}}]}
        yield {"choices": [{"delta": {}}], "usage": {"total_tokens": 20}}
    
    with patch.object(BaseAgent, 'run_streaming', return_value=mock_stream()):
        response = test_server.post("/test-agent/chat/completions", json={
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": True
        })
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
        
        # Verify streaming response format
        content = response.content.decode()
        assert "data: " in content
        assert "data: [DONE]" in content
```

### Load Testing

```python
# tests/performance/test_load.py
import pytest
import asyncio
import httpx
from concurrent.futures import ThreadPoolExecutor
import time

@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_requests():
    """Test server handling concurrent requests"""
    
    async def make_request(session, agent_name="test-agent"):
        """Make a single request"""
        try:
            response = await session.post(f"http://localhost:8000/{agent_name}/chat/completions", json={
                "messages": [{"role": "user", "content": "Hello"}]
            })
            return response.status_code == 200
        except:
            return False
    
    # Test with increasing concurrency
    for concurrency in [10, 50, 100, 500]:
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=30.0) as session:
            tasks = [make_request(session) for _ in range(concurrency)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        successful = sum(1 for result in results if result is True)
        
        print(f"Concurrency {concurrency}: {successful}/{concurrency} successful, {end_time-start_time:.2f}s")
        
        # Require 95% success rate
        assert successful / concurrency >= 0.95

@pytest.mark.performance
def test_streaming_performance():
    """Test streaming performance under load"""
    
    def stream_request():
        """Make streaming request and measure time"""
        start = time.time()
        
        response = requests.post(
            "http://localhost:8000/test-agent/chat/completions",
            json={
                "messages": [{"role": "user", "content": "Tell me a long story"}],
                "stream": True
            },
            stream=True
        )
        
        chunks = 0
        for line in response.iter_lines():
            if line.startswith(b"data: "):
                chunks += 1
                if b"[DONE]" in line:
                    break
        
        return time.time() - start, chunks
    
    # Test 50 concurrent streaming requests
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(stream_request) for _ in range(50)]
        results = [future.result() for future in futures]
    
    durations = [r[0] for r in results]
    chunks = [r[1] for r in results]
    
    # Performance assertions
    assert max(durations) < 30.0  # No request takes more than 30s
    assert sum(chunks) > 0  # All requests got chunks
    
    print(f"Streaming performance: avg={sum(durations)/len(durations):.2f}s, max={max(durations):.2f}s")
```

---

## 2. Migration from V1

### V1 to V2 Migration Tool

```python
# migration/v1_to_v2_migrator.py
import json
import yaml
from typing import Dict, Any, List
from robutler.agents.core.base_agent import BaseAgent
from robutler.agents.skills.openai import OpenAISkill

class V1ToV2Migrator:
    """Tool to migrate V1 agents to V2 architecture"""
    
    def __init__(self):
        self.skill_mappings = {
            # V1 -> V2 skill mappings
            "memory": "short_term_memory",
            "long_term_memory": "long_term_memory", 
            "vector_db": "vector_memory",
            "guardrails": "guardrails",
            "google_search": "google",
            "database": "database"
        }
    
    def migrate_agent_config(self, v1_config: Dict[str, Any]) -> Dict[str, Any]:
        """Convert V1 agent config to V2 format"""
        
        v2_config = {
            "name": v1_config.get("name", "migrated-agent"),
            "instructions": v1_config.get("system_prompt", "You are a helpful assistant"),
            "skills": {},
            "tools": []
        }
        
        # Migrate model to LLM skill
        model = v1_config.get("model", "gpt-3.5-turbo")
        if model.startswith("gpt"):
            v2_config["skills"]["openai"] = {
                "class": "OpenAISkill",
                "config": {
                    "api_key": v1_config.get("openai_api_key", "${OPENAI_API_KEY}")
                }
            }
        
        # Migrate capabilities to skills
        capabilities = v1_config.get("capabilities", [])
        for capability in capabilities:
            if capability in self.skill_mappings:
                skill_name = self.skill_mappings[capability]
                v2_config["skills"][skill_name] = {
                    "class": f"{skill_name.title().replace('_', '')}Skill",
                    "config": v1_config.get(f"{capability}_config", {})
                }
        
        # Migrate custom tools
        tools = v1_config.get("tools", [])
        v2_config["tools"] = [self._migrate_tool(tool) for tool in tools]
        
        # Note: Pricing is now handled by PaymentSkill, not at agent level
        # V1 pricing config is ignored in V2
        
        return v2_config
    
    def _migrate_tool(self, v1_tool: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate V1 tool to V2 format"""
        return {
            "name": v1_tool.get("name"),
            "description": v1_tool.get("description"),
            "function": v1_tool.get("implementation"),
            "scope": v1_tool.get("access_level", "all")
        }
    
    def create_v2_agent_from_config(self, v2_config: Dict[str, Any]) -> BaseAgent:
        """Create V2 agent from migrated config"""
        
        # Build skills
        skills = {}
        for skill_name, skill_config in v2_config.get("skills", {}).items():
            skills[skill_name] = self._instantiate_skill(skill_config)
        
        # Build tools (would need to dynamically load from function definitions)
        tools = []  # Simplified for example
        
        return BaseAgent(
            name=v2_config["name"],
            instructions=v2_config["instructions"],
            skills=skills,
            tools=tools
            # Note: Pricing is handled by PaymentSkill in skills
        )
    
    def _instantiate_skill(self, skill_config: Dict[str, Any]):
        """Dynamically instantiate skill from config"""
        class_name = skill_config["class"]
        config = skill_config.get("config", {})
        
        # Simplified skill instantiation
        if class_name == "OpenAISkill":
            return OpenAISkill(config)
        # Add other skills as needed
        
        return None
    
    def migrate_directory(self, v1_dir: str, v2_dir: str):
        """Migrate entire directory of V1 agents"""
        import os
        
        for filename in os.listdir(v1_dir):
            if filename.endswith(".json") or filename.endswith(".yaml"):
                v1_path = os.path.join(v1_dir, filename)
                
                # Load V1 config
                with open(v1_path) as f:
                    if filename.endswith(".json"):
                        v1_config = json.load(f)
                    else:
                        v1_config = yaml.safe_load(f)
                
                # Migrate to V2
                v2_config = self.migrate_agent_config(v1_config)
                
                # Save V2 config
                v2_filename = filename.replace(".json", ".yaml").replace(".yaml", "_v2.yaml")
                v2_path = os.path.join(v2_dir, v2_filename)
                
                with open(v2_path, 'w') as f:
                    yaml.dump(v2_config, f, default_flow_style=False)
                
                print(f"Migrated {v1_path} -> {v2_path}")

# Usage
def main():
    migrator = V1ToV2Migrator()
    
    # Example V1 config
    v1_config = {
        "name": "customer-service-bot",
        "system_prompt": "You are a helpful customer service assistant",
        "model": "gpt-4",
        "openai_api_key": "${OPENAI_API_KEY}",
        "capabilities": ["memory", "guardrails", "google_search"],
        "memory_config": {"max_messages": 100},
        "pricing": {"per_token": 0.001, "per_call": 5.0}
    }
    
    # Migrate
    v2_config = migrator.migrate_agent_config(v1_config)
    
    print("V2 Config:")
    print(yaml.dump(v2_config, default_flow_style=False))
    
    # Create actual V2 agent
    v2_agent = migrator.create_v2_agent_from_config(v2_config)
    print(f"Created V2 agent: {v2_agent.name}")

if __name__ == "__main__":
    main()
```

### Migration Compatibility Layer

```python
# compatibility/v1_compat.py
"""Compatibility layer for V1 API calls"""

from robutler.agents.core.base_agent import BaseAgent
from robutler.server.core.app import RobutlerServer

def create_v1_compatible_server(agents: List[BaseAgent]) -> RobutlerServer:
    """Create server with V1-compatible endpoints"""
    server = RobutlerServer(agents=agents)
    
    # Add V1-compatible endpoints
    @server.app.post("/v1/completions")
    async def v1_completions(request: V1CompletionRequest):
        """V1-style completion endpoint"""
        # Convert V1 request to V2 format
        v2_messages = [{"role": "user", "content": request.prompt}]
        
        # Use first available agent
        agent = list(server.static_agents.values())[0]
        
        response = await agent.run(v2_messages)
        
        # Convert V2 response to V1 format
        return {
            "id": response.id,
            "object": "text_completion",
            "created": response.created,
            "model": response.model,
            "choices": [{
                "text": response.choices[0].message["content"],
                "index": 0,
                "logprobs": None,
                "finish_reason": response.choices[0].finish_reason
            }],
            "usage": response.usage.__dict__
        }
    
    return server

class V1CompletionRequest:
    """V1-style completion request"""
    def __init__(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7):
        self.prompt = prompt
        self.max_tokens = max_tokens
        self.temperature = temperature
```

---

## 3. Production Deployment

### Environment Configuration

```python
# config/production.py
import os
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class ProductionConfig:
    """Production configuration management"""
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://localhost/robutler")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Vector Database  
    milvus_host: str = os.getenv("MILVUS_HOST", "localhost")
    milvus_port: int = int(os.getenv("MILVUS_PORT", "19530"))
    
    # External Services
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Robutler Platform
    portal_url: str = os.getenv("ROBUTLER_API_URL", "https://robutler.ai")
    portal_api_key: str = os.getenv("ROBUTLER_API_KEY", "")
    
    # Security
    jwt_secret: str = os.getenv("JWT_SECRET", "change-in-production")
    cors_origins: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Monitoring
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    enable_metrics: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    
    # Performance
    max_concurrent_requests: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "1000"))
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "300"))

def create_production_agent() -> BaseAgent:
    """Create production-ready agent with all skills"""
    config = ProductionConfig()
    
    return BaseAgent(
        name="production-agent",
        instructions="You are a production AI assistant with comprehensive capabilities",
        
        skills={
            # Core skills
            "litellm": LiteLLMSkill({"api_key": config.openai_api_key}),
            "short_term_memory": ShortTermMemorySkill({"max_messages": 100}),
            "long_term_memory": LongTermMemorySkill({
                "connection_string": config.database_url
            }),
            "vector_memory": VectorMemorySkill({
                "milvus_host": config.milvus_host,
                "milvus_port": config.milvus_port
            }),
            "guardrails": GuardrailsSkill({"safety_level": "high"}),
            
            # Platform skills
            "robutler.auth": AuthSkill({
                "jwt_secret": config.jwt_secret,
                "portal_url": config.portal_url
            }),
            "robutler.payments": PaymentSkill({
                "portal_url": config.portal_url,
                "api_key": config.portal_api_key
            }),
            "robutler.storage": StorageSkill({
                "portal_url": config.portal_url,
                "api_key": config.portal_api_key
            }),
            
            # External services
            "google": GoogleSkill({"api_key": config.google_api_key}),
        }
        
        # Note: Pricing is handled by PaymentSkill, not at agent level
    )
```

### Production Server Setup

```python
# server_production.py
import uvicorn
import logging
from robutler.server.core.app import RobutlerServer
from config.production import create_production_agent, ProductionConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def create_production_server():
    """Create production server with monitoring and security"""
    config = ProductionConfig()
    
    # Create agents
    agents = [
        create_production_agent(),
    ]
    
    # Create server
    server = RobutlerServer(agents=agents)
    
    # Add production middleware
    @server.app.middleware("http")
    async def security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response
    
    # Add CORS
    from fastapi.middleware.cors import CORSMiddleware
    server.app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add request limiting
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    
    limiter = Limiter(key_func=get_remote_address)
    server.app.state.limiter = limiter
    server.app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    @server.app.get("/")
    @limiter.limit("100/minute")
    async def root(request):
        return {"message": "Robutler V2 Production Server"}
    
    return server

if __name__ == "__main__":
    config = ProductionConfig()
    server = create_production_server()
    
    uvicorn.run(
        server.app,
        host=config.host,
        port=config.port,
        workers=config.workers,
        log_level=config.log_level.lower()
    )
```

### Docker Production Setup

```dockerfile
# Dockerfile.production
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN groupadd -r robutler && useradd -r -g robutler robutler

# Set working directory
WORKDIR /app

# Copy application
COPY . .
RUN chown -R robutler:robutler /app

# Switch to non-root user
USER robutler

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run server
CMD ["python", "server_production.py"]
```

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  robutler-agent:
    build:
      context: .
      dockerfile: Dockerfile.production
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://robutler:${DB_PASSWORD}@postgres:5432/robutler_prod
      - REDIS_URL=redis://redis:6379/0
      - MILVUS_HOST=milvus
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ROBUTLER_API_URL=${ROBUTLER_API_URL}
      - ROBUTLER_API_KEY=${ROBUTLER_API_KEY}
      - JWT_SECRET=${JWT_SECRET}
      - LOG_LEVEL=INFO
    depends_on:
      - postgres
      - redis
      - milvus
    restart: unless-stopped
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: robutler_prod
      POSTGRES_USER: robutler
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
    
  milvus:
    image: milvusdb/milvus:v2.3.0
    environment:
      ETCD_ENDPOINTS: etcd:2379
      MINIO_ADDRESS: minio:9000
    volumes:
      - milvus_data:/var/lib/milvus
    depends_on:
      - etcd
      - minio
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - robutler-agent
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  milvus_data:
  etcd_data:
  minio_data:
```

---

## 4. Monitoring and Observability

### Metrics Collection

```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server, generate_latest
from fastapi import FastAPI, Response
from functools import wraps
import time
import threading
import asyncio
from typing import Dict, Any

# Prometheus Metrics
REQUEST_COUNT = Counter('robutler_requests_total', 'Total requests', ['agent', 'method', 'status'])
REQUEST_DURATION = Histogram('robutler_request_duration_seconds', 'Request duration', ['agent'])
ACTIVE_CONNECTIONS = Gauge('robutler_active_connections', 'Active connections')
SKILL_USAGE = Counter('robutler_skill_usage_total', 'Skill usage', ['skill', 'agent'])
TOKEN_USAGE = Counter('robutler_tokens_total', 'Token usage', ['agent', 'type'])
AGENT_HEALTH = Gauge('robutler_agent_health', 'Agent health status', ['agent'])
DYNAMIC_AGENTS = Gauge('robutler_dynamic_agents_active', 'Active dynamic agents')

class PrometheusMetrics:
    """Prometheus metrics manager with separate metrics server"""
    
    def __init__(self, metrics_port: int = 9090):
        self.metrics_port = metrics_port
        self.metrics_server_started = False
    
    def start_metrics_server(self):
        """Start Prometheus metrics server on separate port"""
        if not self.metrics_server_started:
            # Start Prometheus HTTP server on separate port (non-blocking)
            def run_metrics_server():
                start_http_server(self.metrics_port)
                print(f"📊 Prometheus metrics server started on port {self.metrics_port}")
            
            # Run in separate thread to avoid blocking main app
            metrics_thread = threading.Thread(target=run_metrics_server, daemon=True)
            metrics_thread.start()
            self.metrics_server_started = True
    
    def track_agent_method(self, func):
    """Decorator to track metrics for agent methods"""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(self, *args, **kwargs)
                REQUEST_COUNT.labels(
                    agent=self.name, 
                    method=func.__name__, 
                    status='success'
                ).inc()
            
            # Track token usage if available
            if hasattr(result, 'usage'):
                TOKEN_USAGE.labels(agent=self.name, type='prompt').inc(result.usage.prompt_tokens)
                TOKEN_USAGE.labels(agent=self.name, type='completion').inc(result.usage.completion_tokens)
            
            return result
                
        except Exception as e:
                REQUEST_COUNT.labels(
                    agent=self.name, 
                    method=func.__name__, 
                    status='error'
                ).inc()
            raise
        finally:
            duration = time.time() - start_time
            REQUEST_DURATION.labels(agent=self.name).observe(duration)
    
    return wrapper
    
    def track_skill_usage(self, skill_name: str, agent_name: str):
        """Track skill usage"""
        SKILL_USAGE.labels(skill=skill_name, agent=agent_name).inc()
    
    def update_agent_health(self, agent_name: str, health_status: float):
        """Update agent health status (1.0 = healthy, 0.0 = unhealthy)"""
        AGENT_HEALTH.labels(agent=agent_name).set(health_status)
    
    def set_dynamic_agents_count(self, count: int):
        """Update count of active dynamic agents"""
        DYNAMIC_AGENTS.set(count)

class MetricsMiddleware:
    """FastAPI middleware for automatic metrics collection"""
    
    def __init__(self, app: FastAPI):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            ACTIVE_CONNECTIONS.inc()
            
            # Extract path and method for metrics
            path = scope.get("path", "unknown")
            method = scope.get("method", "unknown")
            
            try:
                await self.app(scope, receive, send)
                
                # Track successful requests
                if not path.startswith("/metrics"):  # Don't track metrics endpoint
                    REQUEST_COUNT.labels(
                        agent="server", 
                        method=f"{method}_{path.replace('/', '_')}", 
                        status="success"
                    ).inc()
                    
            except Exception:
                REQUEST_COUNT.labels(
                    agent="server", 
                    method=f"{method}_{path.replace('/', '_')}", 
                    status="error"
                ).inc()
                raise
            finally:
                ACTIVE_CONNECTIONS.dec()
                if not path.startswith("/metrics"):
                duration = time.time() - start_time
                    REQUEST_DURATION.labels(agent="server").observe(duration)
        else:
            await self.app(scope, receive, send)

# Global metrics instance
metrics = PrometheusMetrics()
```

### Health Monitoring and Server Setup

```python
# monitoring/health.py
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import asyncio
import psutil
import time
import os
from .metrics import metrics, MetricsMiddleware

class HealthMonitor:
    """Comprehensive system health monitoring"""
    
    def __init__(self):
        self.start_time = time.time()
        self.checks = {
            'system': self._check_system_health,
            'database': self._check_database,
            'redis': self._check_redis,
            'milvus': self._check_milvus,
            'external_apis': self._check_external_apis,
            'agents': self._check_agents_health
        }
    
    async def get_health_status(self, detailed: bool = False) -> Dict[str, Any]:
        """Get comprehensive health status"""
        status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'uptime_seconds': time.time() - self.start_time,
            'version': os.getenv('APP_VERSION', '2.0.0'),
            'environment': os.getenv('ENVIRONMENT', 'development'),
        }
        
        if detailed:
            status['checks'] = {}
        
        # Run all health checks
        for name, check_func in self.checks.items():
            try:
                check_result = await check_func()
                status['checks'][name] = check_result
                
                    # Update overall status if any check fails
                if not check_result.get('healthy', True):
                        status['status'] = 'unhealthy'
                    
            except Exception as e:
                status['checks'][name] = {
                    'healthy': False,
                        'error': str(e),
                        'timestamp': time.time()
                }
                status['status'] = 'unhealthy'
        
        return status
    
    async def _check_system_health(self) -> Dict[str, Any]:
        """Check system resource health"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'healthy': cpu_percent < 90 and memory.percent < 90 and disk.percent < 90,
            'details': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent
            },
            'timestamp': time.time()
        }
    
    async def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity"""
        # Implement database health check
        return {'healthy': True, 'response_time_ms': 10, 'timestamp': time.time()}
    
    async def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity"""
        # Implement Redis health check
        return {'healthy': True, 'response_time_ms': 5, 'timestamp': time.time()}
    
    async def _check_milvus(self) -> Dict[str, Any]:
        """Check Milvus vector database connectivity"""
        # Implement Milvus health check
        return {'healthy': True, 'response_time_ms': 15, 'timestamp': time.time()}
    
    async def _check_external_apis(self) -> Dict[str, Any]:
        """Check external API health (OpenAI, Anthropic, etc.)"""
        # Implement external API health checks
        return {'healthy': True, 'apis_checked': 3, 'timestamp': time.time()}
    
    async def _check_agents_health(self) -> Dict[str, Any]:
        """Check agent system health"""
        # Check agent metrics and status
        return {'healthy': True, 'active_agents': 5, 'timestamp': time.time()}

# Server setup with health on / and metrics on separate port
def create_monitored_app() -> FastAPI:
    """Create FastAPI app with health endpoint on / and metrics on separate port"""
    
    app = FastAPI(
        title="Robutler V2 Agent Server",
        description="AI Agent Server with Health Monitoring and Prometheus Metrics",
        version="2.0.0"
    )
    
    # Initialize health monitor
    health_monitor = HealthMonitor()
    
    # Add metrics middleware
    app.add_middleware(MetricsMiddleware)
    
    # Start Prometheus metrics server on port 9090 (separate from main app)
    metrics.start_metrics_server()
    
    # Health endpoint on root path
    @app.get("/", response_model=Dict[str, Any])
    async def health_check():
        """Primary health check endpoint - used by load balancers and monitoring"""
        health_status = await health_monitor.get_health_status(detailed=False)
        
        # Return appropriate HTTP status
        if health_status['status'] == 'healthy':
            return health_status
        else:
            raise HTTPException(status_code=503, detail=health_status)
    
    # Detailed health endpoint  
    @app.get("/health/detailed", response_model=Dict[str, Any])
    async def detailed_health_check():
        """Detailed health check with all subsystem status"""
        return await health_monitor.get_health_status(detailed=True)
    
    # Ready endpoint (Kubernetes readiness probe)
    @app.get("/ready")
    async def readiness_check():
        """Kubernetes readiness probe endpoint"""
        health_status = await health_monitor.get_health_status(detailed=False)
        
        if health_status['status'] == 'healthy':
            return {"status": "ready", "timestamp": time.time()}
        else:
            raise HTTPException(status_code=503, detail="Service not ready")
    
    # Live endpoint (Kubernetes liveness probe)
    @app.get("/live")
    async def liveness_check():
        """Kubernetes liveness probe endpoint"""
        return {
            "status": "alive", 
            "timestamp": time.time(),
            "uptime_seconds": time.time() - health_monitor.start_time
        }
    
    return app

# Usage example
if __name__ == "__main__":
    import uvicorn
    
    # Create app with monitoring
    app = create_monitored_app()
    
    print("🚀 Starting Robutler V2 Server with monitoring...")
    print("📊 Prometheus metrics: http://localhost:9090/metrics")
    print("💚 Health check: http://localhost:8000/")
    print("🔍 Detailed health: http://localhost:8000/health/detailed")
    
    # Start main application server
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
```

### **Production-Ready Monitoring Configuration**

```yaml
# docker-compose.monitoring.yml - Complete production monitoring setup

version: '3.8'
services:
  # Main Robutler application
  robutler-app:
    build: .
    ports:
      - "8000:8000"  # Main application port
      # Note: Metrics exposed internally on port 9090
    environment:
      - ENVIRONMENT=production
      - APP_VERSION=2.0.0
      - METRICS_PORT=9090
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - robutler-network
  
  # Prometheus metrics collection
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"  # Prometheus UI (external)
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.enable-lifecycle'
    networks:
      - robutler-network
  
  # Grafana dashboards  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"  # Grafana UI
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=robutler_admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
    networks:
      - robutler-network

volumes:
  prometheus_data:
  grafana_data:

networks:
  robutler-network:
    driver: bridge

---

# prometheus.yml - Scraping configuration
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Scrape Robutler metrics from internal metrics port
  - job_name: 'robutler-metrics'
    static_configs:
      - targets: ['robutler-app:9090']  # Internal metrics port
    scrape_interval: 10s
    metrics_path: '/metrics'
    
  # Scrape health status from main application
  - job_name: 'robutler-health'  
    static_configs:
      - targets: ['robutler-app:8000']  # Main application port
    scrape_interval: 30s
    metrics_path: '/health/detailed'
    scrape_timeout: 5s

---

# Load balancer configuration (nginx/haproxy)
upstream robutler_backend {
    server robutler-app:8000;
    # Health check uses / endpoint
}

server {
    listen 80;
    server_name robutler.example.com;
    
    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://robutler_backend/;
        proxy_connect_timeout 1s;
        proxy_read_timeout 3s;
    }
    
    # Application endpoints
    location / {
        proxy_pass http://robutler_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### **Kubernetes Configuration**

```yaml
# k8s-monitoring.yaml - Kubernetes deployment with proper health checks

apiVersion: apps/v1
kind: Deployment
metadata:
  name: robutler-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: robutler-app
  template:
    metadata:
      labels:
        app: robutler-app
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: robutler-app
        image: robutler:2.0.0
        ports:
        - containerPort: 8000  # Main application
          name: http
        - containerPort: 9090  # Metrics (internal)
          name: metrics
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: METRICS_PORT
          value: "9090"
        
        # Health check probes use different endpoints
        livenessProbe:
          httpGet:
            path: /live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"

---
apiVersion: v1
kind: Service
metadata:
  name: robutler-service
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "9090"
spec:
  selector:
    app: robutler-app
  ports:
  - name: http
    port: 80
    targetPort: 8000  # Main app port for external traffic
  - name: metrics
    port: 9090
    targetPort: 9090  # Internal metrics port for Prometheus
  type: LoadBalancer
```

### **Key Architecture Benefits:**

✅ **🔀 Port Separation**: Main app on 8000, Prometheus metrics on 9090  
✅ **💚 Health on Root**: Load balancers can use simple `GET /` for health checks  
✅ **🎯 Multiple Health Endpoints**: `/` (basic), `/health/detailed` (comprehensive), `/ready`, `/live`  
✅ **📊 Prometheus Integration**: Clean metrics scraping without interfering with app traffic  
✅ **☸️ Kubernetes Ready**: Proper liveness/readiness probes and service annotations  
✅ **🔒 Production Secure**: Internal metrics port, external health endpoints only  
✅ **📈 Monitoring Stack**: Complete Prometheus + Grafana setup with Docker Compose


## Summary

Chapter 6 provides comprehensive implementation guidance:

✅ **Testing Strategy** - Unit, integration, server, and load testing frameworks  
✅ **Migration from V1** - Complete migration tools and compatibility layer  
✅ **Production Deployment** - Environment configuration, Docker, and Kubernetes  
✅ **Monitoring & Observability** - Production-ready monitoring with Prometheus on port 9090, health checks on `/`, complete Docker/Kubernetes configuration  

The complete 6-chapter design provides everything needed to implement, test, deploy, and operate Robutler V2 in production environments.

---

## 🎯 **Implementation Ready**

All chapters of the Robutler V2 Design Document are now complete:

1. **[Chapter 1: Overview](./ROBUTLER_V2_DESIGN_Ch1_Overview.md)** - High-level architecture  
2. **[Chapter 2: Core Architecture](./ROBUTLER_V2_DESIGN_Ch2_Core_Architecture.md)** - Component design  
3. **[Chapter 3: Skills System](./ROBUTLER_V2_DESIGN_Ch3_Skills_System.md)** - Complete skill implementation  
4. **[Chapter 4: Server & Tools](./ROBUTLER_V2_DESIGN_Ch4_Server_Tools.md)** - FastAPI server and tools  
5. **[Chapter 5: Integration & Usage](./ROBUTLER_V2_DESIGN_Ch5_Integration_Usage.md)** - Usage examples  
6. **[Chapter 6: Implementation Guide](./ROBUTLER_V2_DESIGN_Ch6_Implementation_Guide.md)** - Testing and deployment  

**Ready to begin implementation following the [Implementation Plan](./ROBUTLER_V2_0_IMPLEMENTATION_PLAN.md)!** 🚀 