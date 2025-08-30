# Robutler V2 Design Document - Chapter 4: Server & Tools

## Overview

This chapter covers the FastAPI server implementation, endpoint structure, tool execution system, and request management. The server provides a focused, production-ready HTTP interface with comprehensive streaming support.

---

## 1. FastAPI Server Implementation

### RobutlerServer Core

```python
# robutler/server/core/app.py
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional, Callable, Union
import uuid
from datetime import datetime

from ...agents.interfaces.agent import Agent, OpenAIResponse, OpenAITool
from ..context.manager import ContextManager
from ..context.state import RequestContext, UserContext

class RobutlerServer:
    """FastAPI server for AI agents with OpenAI compatibility"""
    
    def __init__(self, 
                 agents: List[Agent],
                 dynamic_agents: Optional[Callable[[str], Agent]] = None):
        """
        Initialize Robutler server
        
        Args:
            agents: List of static Agent instances
            dynamic_agents: Optional function(agent_name: str) -> Agent for /agents/{name}/... routes
        """
        self.app = FastAPI(
            title="Robutler V2 Server",
            description="AI Agent Server with OpenAI Compatibility",
            version="2.0.0"
        )
        
        # Store agents by name for quick lookup
        self.static_agents = {agent.name: agent for agent in agents}
        self.dynamic_agents = dynamic_agents
        
        # Services (simplified - auth/billing handled by agent skills)
        self.context_manager = ContextManager()
        
        # Setup server
        self._setup_middleware()
        self._create_agent_endpoints()
        self._create_discovery_endpoints()
    
    def _setup_middleware(self):
        """Setup request context middleware"""
        @self.app.middleware("http")
        async def context_middleware(request: Request, call_next):
            # Create request context
            request_id = str(uuid.uuid4())
            # Extract user context from headers
            user_context = self._extract_user_context(request)
            context = self.context_manager.create_context(request_id, user_context)
            
            # Store context ID in request for retrieval
            request.state.robutler_context_id = request_id
            
            try:
                response = await call_next(request)
                return response
            finally:
                # Cleanup context (billing handled by agent skills)
                self.context_manager.cleanup_context(request_id)
    
    def _extract_user_context(self, request: Request) -> UserContext:
        """Extract user context from request headers"""
        headers = dict(request.headers)
        return UserContext(
            peer_user_id=headers.get("x-user-id", "anonymous"),
            payment_user_id=headers.get("x-payment-user-id", "anonymous"),
            origin_user_id=headers.get("x-origin-user-id"),
            agent_owner_user_id=headers.get("x-agent-owner-id")
        )
    
    def _create_agent_endpoints(self):
        """Create all necessary endpoints for agents"""
        
        # Static agent endpoints: /{agent_name}/chat/completions
        for agent_name in self.static_agents.keys():
            self._create_endpoints_for_agent(agent_name, is_dynamic=False)
        
        # Dynamic agent endpoints: /{agent_name}/chat/completions (same structure as static)
        if self.dynamic_agents:
            @self.app.post("/{agent_name}/chat/completions")  
            @self.app.post("/{agent_name}/chat/completions/")
            async def dynamic_chat_completion(agent_name: str, request: ChatCompletionRequest, 
                                            fastapi_request: Request):
                return await self._handle_chat_completion(
                    agent_name, request, fastapi_request, is_dynamic=True
                )
            
            @self.app.get("/{agent_name}")
            @self.app.get("/{agent_name}/")
            async def dynamic_agent_info(agent_name: str, fastapi_request: Request):
                return await self._handle_agent_info(agent_name, fastapi_request, is_dynamic=True)
    
    def _create_endpoints_for_agent(self, agent_name: str, is_dynamic: bool = False):
        """Create endpoints for a specific agent (V2.0: completions only)"""
        
        # V2.0: Chat completions endpoint (OpenAI compatible)
        @self.app.post(f"/{agent_name}/chat/completions")
        @self.app.post(f"/{agent_name}/chat/completions/")
        async def chat_completion(request: ChatCompletionRequest, fastapi_request: Request):
            return await self._handle_chat_completion(
                agent_name, request, fastapi_request, is_dynamic=False
            )
        
        # V2.0: Agent info endpoint  
        @self.app.get(f"/{agent_name}")
        @self.app.get(f"/{agent_name}/")
        async def agent_info(fastapi_request: Request):
            return await self._handle_agent_info(agent_name, fastapi_request, is_dynamic=False)
    
    def _create_discovery_endpoints(self):
        """Create agent discovery endpoint if any agent has DiscoverySkill"""
        discovery_agent = self._find_agent_with_discovery_skill()
        if discovery_agent:
            discovery_skill = discovery_agent.context.get_skill("robutler.discovery")  
            self._create_root_discovery_endpoint(discovery_skill)
    
    def _create_root_discovery_endpoint(self, discovery_skill):
        """Create root discovery endpoint with search query parameter"""
        
        @self.app.get("/")
        async def root_discovery(
            search: Optional[str] = None,
            top_k: Optional[int] = 5,
            x_payment_token: Optional[str] = Header(None, alias="X-Payment-Token")
        ):
            """
            Agent discovery endpoint - supports search with query parameter
            
            Examples:
            - GET / -> List all agents  
            - GET /?search=coding -> Search for coding-related agents
            - GET /?search=python&top_k=10 -> Search with custom limit
            """
            
            if search:
                # Search for agents
                try:
                    result = await discovery_skill.discover_agents(
                        query=search,
                        max_results=top_k
                    )
                    
                    return {
                        "query": search,
                        "agents": [
                            {
                                "name": agent.get("name"),
                                "description": agent.get("description"),
                                "url": agent.get("url"),
                                "capabilities": agent.get("capabilities", []),
                                "min_balance": agent.get("min_balance", 0)
                                # Note: Pricing handled by PaymentSkill
                            }
                            for agent in result.get("agents", [])
                        ],
                        "total_results": len(result.get("agents", []))
                    }
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Agent search failed: {str(e)}")
            else:
                # List all available agents
                return {
                    "message": "Robutler V2 Server",
                    "version": "2.0.0", 
                    "agents": list(self.static_agents.keys()),
                    "endpoints": {
                        "discovery": "/?search={query}&top_k={limit}",
                        "agent_info": "/{agent_name}",
                        "chat_completions": "/{agent_name}/chat/completions"
                    }
                }

    def _find_agent_with_discovery_skill(self) -> Optional[Agent]:
        """Find first agent that has discovery skill for server-level endpoints"""
        for agent in self.static_agents.values():
            if hasattr(agent, 'context') and agent.context.get_skill("robutler.discovery"):
                return agent
        return None
```

### Request/Response Models

```python
# robutler/server/models.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request"""
    model: Optional[str] = None  # Agent name used as model
    messages: List[Dict[str, Any]]
    stream: Optional[bool] = False
    tools: Optional[List[Dict[str, Any]]] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[Union[str, List[str]]] = None

class AgentInfoResponse(BaseModel):
    """Agent information response"""
    name: str
    description: str
    capabilities: List[str]
    skills: List[str]
    pricing: Dict[str, Any]
    # Note: Intents are handled by DiscoverySkill, not exposed in agent info
```

---

## 2. Endpoint Implementation

### Chat Completions Handler

```python
async def _handle_chat_completion(self, agent_name: str, request: ChatCompletionRequest,
                                 fastapi_request: Request, is_dynamic: bool = False) -> Union[OpenAIResponse, StreamingResponse]:
    """Handle chat completion request"""
    
    # Get request context
    context = self._get_request_context(fastapi_request)
    
    # Resolve agent
    agent = await self._resolve_agent(agent_name, is_dynamic, context)
    
    # Extract tools from request (external tools)
    external_tools = self._extract_tools_from_request(request)
    
    # Execute agent
    if request.stream:
        # Streaming response
        return StreamingResponse(
            self._stream_agent_response(agent, request.messages, external_tools, context),
            media_type="text/plain"
        )
    else:
        # Non-streaming response  
        response = await agent.run(
            messages=request.messages,
            stream=False, 
            tools=external_tools
        )
        
        # Track token usage
        await self._track_token_usage(context, response.usage, agent)
        
        return response

async def _stream_agent_response(self, agent: Agent, messages: List[Dict], 
                               external_tools: List[OpenAITool], context: RequestContext):
    """Handle streaming agent response with proper billing finalization"""
    
    final_usage = None
    
    try:
        async for chunk in agent.run_streaming(messages, tools=external_tools):
            # Stream chunk to client
            yield f"data: {json.dumps(chunk)}\n\n"
            
            # Capture final usage info when available
            if "usage" in chunk:
                final_usage = chunk["usage"]
        
        # End stream
        yield "data: [DONE]\n\n"
        
    finally:
        # Track final usage after streaming completes
        if final_usage:
            await self._track_token_usage(context, final_usage, agent)

async def _resolve_agent(self, agent_name: str, is_dynamic: bool, context: RequestContext) -> Agent:
    """Resolve agent by name from static or dynamic sources"""
    
    if is_dynamic:
        if not self.dynamic_agents:
            raise HTTPException(status_code=404, detail="Dynamic agents not supported")
        
        agent = self.dynamic_agents(agent_name)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Dynamic agent '{agent_name}' not found")
    else:
        agent = self.static_agents.get(agent_name)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    # Store agent in context
    context.agent = AgentContext(
        name=agent_name,
        instance=agent,
        pricing={}  # Pricing handled by PaymentSkill
    )
    
    return agent
```

### Agent Info Handler

```python
async def _handle_agent_info(self, agent_name: str, fastapi_request: Request, is_dynamic: bool = False):
    """Handle agent info request"""
    
    context = self._get_request_context(fastapi_request)
    agent = await self._resolve_agent(agent_name, is_dynamic, context)
    
    # Extract agent capabilities
    skills = []
    capabilities = []
    
    if hasattr(agent, 'skills'):
        skills = list(agent.skills.keys())
        
        # Extract capabilities from skills
        for skill_name, skill in agent.skills.items():
            if hasattr(skill, 'get_tools'):
                tools = skill.get_tools()
                capabilities.extend([f"{skill_name}:{tool.__name__}" for tool in tools])
    
    return AgentInfoResponse(
        name=agent.name,
        description=agent.instructions[:200] + "..." if len(agent.instructions) > 200 else agent.instructions,
        capabilities=capabilities,
        skills=skills,
        pricing={}  # Pricing handled by PaymentSkill
        # Note: Intents handled by DiscoverySkill, not exposed in agent info
    )
```

---

## 3. Agent Discovery Endpoint

### Root Discovery Endpoint

The server provides a unified discovery endpoint at the root path that supports both listing all agents and searching with natural language queries.

```python
# Examples of discovery endpoint usage:

# GET / 
# Returns server info and list of available agents

# GET /?search=coding
# Searches for agents related to "coding"

# GET /?search=python%20programming&top_k=10
# Searches with custom result limit
```

**Response Format:**

```python
# Without search parameter:
{
    "message": "Robutler V2 Server",
    "version": "2.0.0",
    "agents": ["agent1", "agent2", "agent3"],
    "endpoints": {
        "discovery": "/?search={query}&top_k={limit}",
        "agent_info": "/{agent_name}",
        "chat_completions": "/{agent_name}/chat/completions"
    }
}

# With search parameter:
{
    "query": "coding",
    "agents": [
        {
            "name": "coding-assistant",
            "description": "Expert programming assistant",
            "url": "http://localhost:8000/coding-assistant",
            "capabilities": ["python", "javascript", "debugging"],
            "min_balance": 0
        }
    ],
    "total_results": 1
}
```

---

## 4. Tool Execution System

### Tool Types: Agent Tools vs External Tools

**🔧 CRITICAL DISTINCTION:** Robutler V2 supports two fundamentally different types of tools:

#### **1. Agent Tools (@tool decorated functions)**
- **Definition**: Functions decorated with `@tool` in agent skills
- **Execution**: **Server-side** execution by the agent
- **Purpose**: Internal agent capabilities (database queries, file operations, calculations)
- **Registration**: Automatically registered by BaseAgent during skill initialization
- **OpenAI Integration**: Automatically included in LLM tool definitions

```python
# Agent tool - executed SERVER-SIDE
class CalculatorSkill(Skill):
    @tool(scope="all")
    def add_numbers(self, a: int, b: int) -> int:
        """Add two numbers together"""
        return a + b  # Executed on the server
```

#### **2. External Tools (from request tools parameter)**
- **Definition**: Tools specified in the OpenAI ChatCompletion request's `tools` parameter
- **Execution**: **CLIENT-side** execution by the requesting client
- **Purpose**: Client-specific capabilities (user's local files, client-side APIs, user permissions)
- **Server Role**: Pass to LLM, return `tool_calls` to client for execution
- **OpenAI Integration**: Merged with agent tools for LLM awareness

```python
# External tools in request - executed CLIENT-SIDE
{
    "model": "agent-name",
    "messages": [...],
    "tools": [  # External tools - CLIENT executes these
        {
            "type": "function",
            "function": {
                "name": "get_user_files",
                "description": "Get files from user's local system",
                "parameters": {...}
            }
        }
    ]
}
```

#### **3. Tool Flow Architecture**

```mermaid
graph TB
    Client[📱 Client] -->|Request + external tools| Server[🖥️ Robutler Server]
    Server --> Agent[🤖 Agent]
    
    Agent --> LLM[🧠 LLM Skill]
    Agent --> |"@tool functions"| AgentTools[🔧 Agent Tools<br/>SERVER execution]
    
    LLM -->|Combined tools| LLMResponse{LLM Response<br/>tool_calls?}
    
    LLMResponse -->|Agent tool calls| Execute[⚙️ Execute Server-side]
    LLMResponse -->|External tool calls| Return[📤 Return to Client]
    
    Execute --> Continue[🔄 Continue conversation]
    Return --> ClientExec[📱 Client executes<br/>external tools]
    ClientExec --> |Tool results| Server
    
    classDef clientClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef serverClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef toolClass fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    
    class Client,ClientExec clientClass
    class Server,Agent,LLM serverClass  
    class AgentTools,Execute,Return toolClass
```

### Automatic Decorator Registration with Central Agent Registry

The `BaseAgent` automatically discovers and registers `@hook`, `@tool`, and `@handoff` decorated methods during skill initialization, eliminating both separate registry classes and manual registration calls. All decorators are automatically registered with scope filtering:

```python
# Skills use decorators for automatic registration
class ComprehensiveSkill(Skill):
    async def initialize(self, agent: 'BaseAgent') -> None:
        """Initialize skill - all decorators auto-registered!"""
        self.agent = agent
        # No manual register_hook(), register_tool(), register_handoff() calls needed!
    
    @hook("on_connection", priority=10, scope="owner")
    async def setup_connection(self, context: Context) -> Context:
        """Hook automatically discovered and registered by BaseAgent"""
        return context
    
    @tool(scope="all")  # Tools automatically registered by BaseAgent
    def my_tool(self, param: str) -> str:
        """Tool automatically discovered and registered by BaseAgent"""
        return f"Processed: {param}"
    
    @handoff(handoff_type="agent", scope=["admin"])
    async def escalate_to_admin(self, issue: str) -> HandoffResult:
        """Handoff automatically discovered and registered by BaseAgent"""
        return HandoffResult(result=f"Escalated: {issue}", handoff_type="agent")

# Agent provides automatic registration + manual registry functionality
class BaseAgent:
    def __init__(self):
        self._registered_tools = []  # Central storage
        self._registration_lock = threading.Lock()
    
    def _auto_register_skill_decorators(self, skill: Any, skill_name: str) -> None:
        """Auto-discover and register @hook, @tool, and @handoff decorated methods"""
        import inspect
        
        for attr_name in dir(skill):
            if attr_name.startswith('_') and not attr_name.startswith('__'):
                continue
                
            attr = getattr(skill, attr_name)
            if not inspect.ismethod(attr) and not inspect.isfunction(attr):
                continue
            
            # Check for @hook decorator
            if hasattr(attr, '_robutler_is_hook') and attr._robutler_is_hook:
                event_type = attr._hook_event_type
                priority = getattr(attr, '_hook_priority', 50)
                scope = getattr(attr, '_hook_scope', None)  # None means all scopes
                self.register_hook(event_type, attr, priority, source=skill_name, scope=scope)
            
            # Check for @tool decorator  
            elif hasattr(attr, '_robutler_is_tool') and attr._robutler_is_tool:
                scope = getattr(attr, '_tool_scope', None)  # None means all scopes
                self.register_tool(attr, source=skill_name, scope=scope)
            
            # Check for @handoff decorator
            elif hasattr(attr, '_robutler_is_handoff') and attr._robutler_is_handoff:
                handoff_config = HandoffFunction(attr)
                scope = getattr(attr, '_handoff_scope', None)  # None means all scopes
                handoff_config.scope = scope
                self.register_handoff(handoff_config, source=skill_name)
    
    def register_tool(self, tool_func: Callable, source: str = "skill", scope: Union[str, List[str]] = None):
        """Central tool registration - called automatically for @tool decorated methods"""
        with self._registration_lock:
            self._registered_tools.append({
                'function': tool_func,
                'source': source,
                'scope': scope,
                'name': getattr(tool_func, '__name__', str(tool_func)),
                'definition': getattr(tool_func, '_robutler_tool_definition', {})
            })
    
    def get_tools_for_scope(self, auth_scope: str) -> List[Callable]:
        """Get tools filtered by user scope (replaces ToolRegistry method)"""
        scope_hierarchy = {"admin": 3, "owner": 2, "all": 1}
        user_level = scope_hierarchy.get(auth_scope, 1)
        
        available_tools = []
        with self._registration_lock:
            for tool_config in self._registered_tools:
                tool_scope = tool_config['scope']
                required_level = scope_hierarchy.get(tool_scope, 1)
                
                if user_level >= required_level:
                    available_tools.append(tool_config['function'])
        
        return available_tools
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all tools with metadata (replaces ToolRegistry.list_tools)"""
        with self._registration_lock:
            return self._registered_tools.copy()
    
    def _prepare_tool_definitions(self) -> List[Dict[str, Any]]:
        """Prepare OpenAI tool definitions from registered tools"""
        tool_definitions = []
        
        with self._registration_lock:
            for tool_config in self._registered_tools:
                tool_func = tool_config['function']
                if hasattr(tool_func, '_robutler_tool_definition'):
                    tool_definitions.append(tool_func._robutler_tool_definition)
        
        return tool_definitions
```

**Benefits of Automatic Decorator Registration:**
- ✅ **Automatic Discovery**: All decorators (`@hook`, `@tool`, `@handoff`) discovered automatically - no manual calls needed
- ✅ **Single Source of Truth**: Agent manages all its capabilities automatically
- ✅ **No Duplication**: Eliminates both separate registry classes and manual registration calls  
- ✅ **Thread-Safe**: Built-in locking for concurrent access
- ✅ **Rich Metadata**: Stores source, scope, priority, and definitions automatically
- ✅ **Self-Documenting**: All capabilities defined declaratively with decorators
- ✅ **Consistent**: Unified pattern for hooks, tools, and handoffs
- ✅ **Scope Filtering**: Automatic scope-based access control for all decorators

---

## 5. Streaming Implementation

### Streaming Response Handler

The server provides complete OpenAI-compatible streaming with proper SSE formatting:

```python
async def _stream_agent_response(self, agent: Agent, messages: List[Dict], 
                               external_tools: List[OpenAITool], context: RequestContext):
    """Handle streaming agent response with proper billing finalization"""
    
    final_usage = None
    
    try:
        # Stream all chunks from agent
        async for chunk in agent.run_streaming(messages, tools=external_tools):
            # Proper SSE formatting
            chunk_data = json.dumps(chunk)
            yield f"data: {chunk_data}\n\n"
            
            # Capture final usage info when available
            if "usage" in chunk:
                final_usage = chunk["usage"]
        
        # Stream termination
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        # Error handling in streaming
        error_chunk = {
            "error": {
                "message": str(e),
                "type": "server_error"
            }
        }
        yield f"data: {json.dumps(error_chunk)}\n\n"
        yield "data: [DONE]\n\n"
        
    finally:
        # Track final usage after streaming completes
        if final_usage:
            await self._track_token_usage(context, final_usage, agent)
```

### Streaming Features

✅ **OpenAI Compatibility**: Full OpenAI Chat Completions API streaming format  
✅ **Tool Call Streaming**: Function calls and responses streamed in real-time  
✅ **Billing Integration**: Usage tracked after stream completion via finalization  
✅ **Error Handling**: Proper error formatting in streaming chunks  
✅ **Concurrent Support**: Non-blocking async streaming for multiple clients  
✅ **Memory Efficiency**: AsyncGenerator pattern for large responses  

---

## 6. Middleware & Context Management

### Request Context Middleware

```python
@self.app.middleware("http")
async def context_middleware(request: Request, call_next):
    # Create request context
    request_id = str(uuid.uuid4())
    
    # Extract user context from headers
    user_context = UserContext(
        peer_user_id=request.headers.get("x-user-id", "anonymous"),
        payment_user_id=request.headers.get("x-payment-user-id", "anonymous"),
        origin_user_id=request.headers.get("x-origin-user-id"),
        agent_owner_user_id=request.headers.get("x-agent-owner-id")
    )
    
    context = self.context_manager.create_context(request_id, user_context)
    
    # Store context ID in request for retrieval
    request.state.robutler_context_id = request_id
    
    try:
        response = await call_next(request)
        return response
    finally:
        # Process final billing and cleanup
        await self._finalize_request(context)
        self.context_manager.cleanup_context(request_id)

async def _finalize_request(self, context: RequestContext):
    """Finalize request - handle billing and cleanup"""
    if not context.usage_records:
        return
    
    # Calculate total cost
    total_cost = sum(record.credits for record in context.usage_records)
    
    if total_cost > 0:
        # Billing is now handled by PaymentSkill in agents
        # Server just logs the final usage
        logger.info(f"Request {context.request_id} usage: {total_cost} credits")
```

### Error Handling

```python
@self.app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper error formatting"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "type": "http_error",
                "code": exc.status_code
            }
        }
    )

@self.app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "Internal server error",
                "type": "server_error",
                "code": 500
            }
        }
    )
```

---

## 7. Production Features

### Health Checks

```python
@self.app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "agents": list(self.static_agents.keys())
    }

@self.app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with agent status"""
    agent_status = {}
    
    for name, agent in self.static_agents.items():
        try:
            # Check if agent is responsive (could ping agent methods)
            agent_status[name] = {
                "status": "healthy",
                "skills": len(agent.skills) if hasattr(agent, 'skills') else 0,
                "tools": len(agent.tools) if hasattr(agent, 'tools') else 0
            }
        except Exception as e:
            agent_status[name] = {
                "status": "unhealthy",
                "error": str(e)
            }
    
    return {
        "server_status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "agents": agent_status
    }
```

### Metrics & Monitoring

```python
@self.app.get("/metrics")
async def metrics():
    """Prometheus-compatible metrics endpoint"""
    # Implementation would return metrics in Prometheus format
    return Response(
        content="# Robutler V2 Metrics\n# TODO: Implement metrics\n",
        media_type="text/plain"
    )
```

---

## Summary

Chapter 4 provides the complete server and capability registration implementation:

✅ **FastAPI Server** - Production-ready HTTP server with OpenAI compatibility  
✅ **Endpoint Structure** - Chat completions, agent info, and discovery endpoints  
✅ **Automatic Decorator Registration** - Complete auto-discovery of `@hook`, `@tool`, and `@handoff` decorators with scope filtering  
✅ **Tool Execution System** - Comprehensive tool registry and execution with pricing integration  
✅ **Streaming Support** - Full OpenAI-compatible streaming with SSE formatting  
✅ **Request Management** - Unified context middleware and lifecycle management  
✅ **Error Handling** - Comprehensive error handling and logging  
✅ **Production Features** - Health checks, metrics, and monitoring  

**Next**: [Chapter 5: Integration & Usage](./ROBUTLER_V2_DESIGN_Ch5_Integration_Usage.md) - Usage examples and platform integration 