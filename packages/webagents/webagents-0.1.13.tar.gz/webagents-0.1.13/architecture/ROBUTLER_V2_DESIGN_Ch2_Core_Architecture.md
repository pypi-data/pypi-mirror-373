# Robutler V2 Design Document - Chapter 2: Core Architecture

## Overview

This chapter covers the detailed component design and core interfaces that form the foundation of the Robutler V2 architecture. These components provide the essential building blocks for agents, tools, and the skill system.

---

## 1. Core Framework Structure

### Project Structure

```
robutler/
├── agents/            # Complete agent system (expandable)
│   ├── core/          # Core agent functionality
│   │   ├── base_agent.py      # BaseAgent implementation
│   │   ├── factory.py         # Agent factory and creation
│   │   ├── runner.py          # Agent execution and lifecycle
│   │   └── context.py         # Run context management
│   ├── skills/        # Hierarchical skill system architecture
│   │   ├── __init__.py        # Skill base classes and categories
│   │   ├── base.py            # Skill interface with lifecycle hooks
│   │   ├── core/              # Essential core skills (V2.0)
│   │   │   ├── __init__.py        # Core skills package
│   │   │   ├── memory/            # 3-tier memory system
│   │   │   │   ├── __init__.py
│   │   │   │   ├── short_term_memory/     # Message context and filtering
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── skill.py
│   │   │   │   ├── long_term_memory/      # Persistent facts (LangGraph + PostgreSQL)
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── skill.py
│   │   │   │   └── vector_memory/         # Semantic search (Milvus)
│   │   │   │       ├── __init__.py
│   │   │   │       └── skill.py
│   │   │   ├── llm/               # LLM provider skills
│   │   │   │   ├── __init__.py
│   │   │   │   ├── litellm/           # LiteLLM integration
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── skill.py
│   │   │   │   ├── openai/            # OpenAI integration
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── skill.py
│   │   │   │   ├── anthropic/         # Anthropic integration
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── skill.py
│   │   │   │   └── xai/               # xAI integration (V2.1)
│   │   │   │       ├── __init__.py
│   │   │   │       └── skill.py
│   │   │   ├── guardrails/        # Content safety and filtering (V2.1)
│   │   │   │   ├── __init__.py
│   │   │   │   └── skill.py
│   │   │   └── mcp/               # Model Context Protocol integration
│   │   │       ├── __init__.py
│   │   │       └── skill.py
│   │   ├── robutler/          # Robutler platform skills (V2.0)
│   │   │   ├── __init__.py        # Platform skills package
│   │   │   ├── auth/              # Authentication and authorization
│   │   │   │   ├── __init__.py
│   │   │   │   └── skill.py
│   │   │   ├── payments/          # Payment processing and billing
│   │   │   │   ├── __init__.py
│   │   │   │   └── skill.py
│   │   │   ├── discovery/         # Agent discovery via Portal
│   │   │   │   ├── __init__.py
│   │   │   │   └── skill.py
│   │   │   ├── nli/               # Natural Language Interface for agent-to-agent communication
│   │   │   │   ├── __init__.py
│   │   │   │   └── skill.py
│   │   │   ├── messages/          # Message management
│   │   │   │   ├── __init__.py
│   │   │   │   └── skill.py
│   │   │   └── storage/           # Portal storage API integration
│   │   │       ├── __init__.py
│   │   │       └── skill.py
│   │   ├── ecosystem/         # Optional ecosystem skills (V2.1+)
│   │   │   ├── __init__.py        # Ecosystem skills package
│   │   │   ├── google/            # Google services integration
│   │   │   │   ├── __init__.py
│   │   │   │   └── skill.py
│   │   │   ├── database/          # Database operations
│   │   │   │   ├── __init__.py
│   │   │   │   └── skill.py
│   │   │   ├── filesystem/        # File system operations
│   │   │   │   ├── __init__.py
│   │   │   │   └── skill.py
│   │   │   ├── web/               # Web scraping
│   │   │   │   ├── __init__.py
│   │   │   │   └── skill.py
│   │   │   ├── crewai/            # CrewAI integration
│   │   │   │   ├── __init__.py
│   │   │   │   └── skill.py
│   │   │   ├── n8n/               # n8n workflow automation
│   │   │   │   ├── __init__.py
│   │   │   │   └── skill.py
│   │   │   └── zapier/            # Zapier automation
│   │   │       ├── __init__.py
│   │   │       └── skill.py
│   │   └── registry.py        # Skill class discovery and loading (NOT tool registry)
│   ├── tools/         # Agent tools system (simplified - centralized in BaseAgent)
│   │   └── decorators.py      # @tool decorator (@pricing moved to PaymentSkill)
│   ├── handoffs/      # OpenAI SDK-compatible handoff system  
│   │   └── base.py            # Handoff base class and LocalAgentHandoff/LLMHandoff/ProcessingPipelineHandoff
│   ├── lifecycle/     # Agent lifecycle management (simplified - hooks in BaseAgent)
│   │   └── context.py         # Context variables and request context management
│   ├── workflows/     # Skill orchestration (simplified - dependencies handled by BaseAgent)
│   │   ├── orchestrator.py    # Skill dependency resolution and initialization order
│   │   └── context.py         # Workflow context and dependency access
│   ├── tracing/       # Observability and tracing
│   │   ├── tracer.py          # Trace creation
│   │   ├── spans.py           # Span management
│   │   └── processors.py      # Trace processors
│   └── interfaces/    # Agent-specific interfaces
│
├── server/            # HTTP server and routing (focused)
│   ├── core/          # Core server components
│   │   ├── app.py             # FastAPI application
│   │   ├── middleware.py      # Request middleware
│   │   ├── routes.py          # Route definitions
│   │   └── lifecycle.py       # Request lifecycle
│   ├── context/       # Request context management
│   │   ├── manager.py         # Context manager
│   │   ├── state.py           # Request state
│   │   └── tracking.py        # Usage tracking
│   ├── endpoints/     # API endpoints (expandable)
│   │   ├── completions.py     # Chat completions (V2.0) ✅
│   │   ├── realtime.py        # Real-time streaming (V2.1+) 🚧
│   │   ├── a2a.py             # Agent-to-agent communication (V2.1+) 🚧
│   │   ├── acp.py             # Agent Communication Protocol (V2.1+) 🚧
│   │   ├── p2p.py             # Peer to peer protocol (V2.1+) 🚧
│   │   ├── voice.py           # Voice interactions (V2.2+) 🚧
│   │   ├── video.py           # Video interactions (V2.2+) 🚧
│   │   └── info.py            # Agent info endpoints (V2.0) ✅
│   └── interfaces/    # Server-specific interfaces
├── api/               # Robutler API client and types
│   ├── client.py      # Main API client for portal integration
│   └── types.py       # API data models and types
├── scripts/           # Simplified helper scripts
│   └── build.sh       # Build
├── utils/             # Utilities and helpers
└── tests/
    ├── agents/            # Agent-specific tests
    ├── server/            # Server-specific tests
    ├── integration/       # Integration tests
    └── fixtures/          # Test fixtures and mocks
```

### Architecture Benefits

**Why This Structure is Better:**
- **Clear Separation**: Agents and server have distinct, focused responsibilities
- **Scalable Architecture**: Agents can expand extensively without affecting server complexity
- **Team Organization**: Different teams can work on agents vs server independently
- **Easier Navigation**: Developers know exactly where to find agent vs server functionality
- **Future-Proof**: Supports all planned agent features (memory, handoffs, tracing, voice, etc.)
- **Modular Testing**: Agent tests and server tests are completely separate

---

## 2. Core Interfaces

### Agent Interface

```python
# robutler/core/interfaces/agent.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum

class ToolType(Enum):
    FUNCTION_TOOL = "function"  # @tool decorated functions (executed SERVER-side)
    EXTERNAL_TOOL = "external"  # Tools from request (executed CLIENT-side)

@dataclass
class OpenAITool:
    """OpenAI-compatible tool definition"""
    type: str  # Always "function"
    function: Dict[str, Any]  # name, description, parameters
    
    # Note: This represents BOTH agent tools and external tools
    # - Agent tools: @tool decorated functions, executed server-side
    # - External tools: From request.tools, executed client-side

@dataclass
class AgentConfig:
    """Agent configuration matching OpenAI Agent SDK"""
    name: str
    instructions: str
    model: str = "gpt-4o-mini"
    tools: List[Callable] = None  # @tool decorated functions
    # Note: Intents are handled by DiscoverySkill, not at agent level

@dataclass
class OpenAIUsage:
    """OpenAI-compatible usage tracking"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

@dataclass
class OpenAIChoice:
    """OpenAI-compatible choice structure"""
    index: int
    message: Dict[str, Any]
    finish_reason: str

@dataclass
class OpenAIResponse:
    """OpenAI-compatible response structure"""
    id: str
    object: str  # "chat.completion"
    created: int
    model: str
    choices: List[OpenAIChoice]
    usage: OpenAIUsage

class Agent(ABC):
    """Base agent interface compatible with OpenAI Agent SDK"""
    
    def __init__(self, name: str, instructions: str, 
                 model: Optional[Union[str, Any]] = None,
                 skills: Optional[Dict[str, Skill]] = None,
                 scope: str = "all",
                 tools: Optional[List[Callable]] = None,
                 hooks: Optional[Dict[str, List[Union[Callable, Dict[str, Any]]]]] = None,
                 handoffs: Optional[List[Union[HandoffConfig, Callable]]] = None):
        self.name = name
        self.instructions = instructions
        self.model = model  # Can be string (model name) or LLM skill instance
        self.skills = skills or {}
        self.scope = scope
        # Tools, hooks, and handoffs are registered in central registries
        # Note: Intents are handled by DiscoverySkill, not at agent level
    
    @abstractmethod
    async def run(self, messages: List[Dict[str, Any]], stream: bool = False, 
                  tools: Optional[List[OpenAITool]] = None) -> OpenAIResponse:
        """
        Execute agent with OpenAI-compatible interface
        
        Args:
            messages: OpenAI-format messages
            stream: Whether to stream response
            tools: External tools from request (in addition to agent's @tool functions)
        """
        pass
    
    @abstractmethod
    async def run_streaming(self, messages: List[Dict[str, Any]], 
                           tools: Optional[List[OpenAITool]] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute agent with streaming OpenAI-compatible response chunks"""
        pass
```

### Tool Execution

Tools are executed directly by skills - no separate service layer needed. Each skill manages its own tools and executes them directly when called by the agent.

---

## 3. BaseAgent Implementation

The BaseAgent provides the core implementation for all AI agents, handling LLM integration, tool execution, and response formatting.

```python
# robutler/core/agent/base_agent.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable, AsyncGenerator, Union
import uuid
import time
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable, AsyncGenerator, Union
from dataclasses import dataclass, field

from ..interfaces.agent import Agent, OpenAIResponse, OpenAIChoice, OpenAIUsage, OpenAITool
from ..tools.decorators import extract_pricing_info
# LLM functionality now provided by core LLM skills (LiteLLMSkill, OpenAISkill, etc.)

# Import handoff system components
from ..handoffs.base import Handoff, LocalAgentHandoff, LLMHandoff, ProcessingPipelineHandoff

# ===== HANDOFF SYSTEM (OpenAI SDK Compatible + Extended) =====

@dataclass
class HandoffInput:
    """Structured input data for handoffs"""
    type: str = field()  # Type identifier for the handoff
    data: Dict[str, Any] = field(default_factory=dict)  # Structured data
    context: Optional[str] = None  # Additional context from LLM
    conversation_summary: Optional[str] = None  # Summary of conversation so far

class Handoff:
    """Base class for handoff configurations (similar to OpenAI SDK pattern)"""
    
    def __init__(self, 
                 target: Any,
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 on_handoff: Optional[Callable] = None,
                 input_type: Optional[type] = None):
        self.target = target
        self.name = name
        self.description = description
        self.on_handoff = on_handoff
        self.input_type = input_type
        self.source = None  # Set by agent during registration
    
    def to_tool_definition(self) -> Dict[str, Any]:
        """Convert to OpenAI tool definition for LLM"""
        raise NotImplementedError("Subclasses must implement to_tool_definition")
    
    async def execute(self, input_data: Dict[str, Any], conversation: List[Dict]) -> Any:
        """Execute the handoff"""
        raise NotImplementedError("Subclasses must implement execute")

class LocalAgentHandoff(Handoff):
    """Handoff to a local agent in the same Robutler instance"""
    
    def __init__(self, target_agent: Union[str, 'BaseAgent'], **kwargs):
        super().__init__(target_agent, **kwargs)
        self.handoff_type = "local_agent"
    
    def to_tool_definition(self) -> Dict[str, Any]:
        agent_name = self.target if isinstance(self.target, str) else self.target.name
        tool_name = self.name or f"transfer_to_{agent_name.replace('-', '_')}"
        description = self.description or f"Transfer conversation to {agent_name} agent"
        
        return {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "context": {
                            "type": "string", 
                            "description": "Context or reason for the handoff"
                        },
                        "data": {
                            "type": "object",
                            "description": "Structured data to pass to the target agent",
                            "additionalProperties": True
                        }
                    },
                    "required": ["context"]
                }
            }
        }
    
    async def execute(self, input_data: Dict[str, Any], conversation: List[Dict]) -> Any:
        """Execute handoff to local agent"""
        # Create handoff context for lifecycle hooks
        handoff_context = {
            "handoff_type": "local_agent", 
            "target": self.target,
            "input_data": input_data,
            "conversation": conversation,
            "filtered_conversation": None,
            "handoff_config": self
        }
        
        # Execute on_handoff hooks (guardrails, logging, filtering, etc.)
        handoff_context = await self._execute_handoff_hooks(handoff_context)
        
        # Use filtered conversation from hooks or original conversation
        filtered_conversation = handoff_context.get("filtered_conversation") or conversation
        
        # Call on_handoff callback if provided (legacy support)
        if self.on_handoff:
            await self.on_handoff(input_data, filtered_conversation)
        
        # Get target agent
        target_agent = self.target
        if isinstance(target_agent, str):
            # Look up agent by name (implementation specific)
            target_agent = self._get_agent_by_name(target_agent)
        
        # Execute with target agent
        return await target_agent.run(filtered_conversation)
    
    async def _execute_handoff_hooks(self, handoff_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute on_handoff lifecycle hooks (implemented by skills like GuardrailsSkill)"""
        # This would be implemented by the agent that owns this handoff
        # For now, just return the context unchanged
        return handoff_context

# NOTE: RemoteAgentHandoff and CrewAIHandoff are implemented within NLISkill and CrewAISkill respectively

# NOTE: N8nWorkflowHandoff, CrewAIHandoff, and RemoteAgentHandoff are implemented
# within their respective skills (N8nSkill, CrewAISkill, NLISkill).
# This keeps handoff logic encapsulated within the skills that provide the capabilities.

class LLMHandoff(Handoff):
    """Handoff to a different LLM model"""
    
    def __init__(self, model: str, **kwargs):
        super().__init__(model, **kwargs)
        self.model = model  # Format: "skill_name/model_name" (e.g., "anthropic/claude-3-5-sonnet-20241022")
        self.handoff_type = "llm"
    
    def to_tool_definition(self) -> Dict[str, Any]:
        model_name = self.model.split('/')[-1] if '/' in self.model else self.model
        tool_name = self.name or f"switch_to_{model_name.replace('-', '_')}"
        description = self.description or f"Switch to {model_name} for specialized processing"
        
        return {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "reason": {"type": "string", "description": "Reason for switching models"},
                        "temperature": {"type": "number", "description": "Temperature override"},
                        "max_tokens": {"type": "integer", "description": "Max tokens override"}
                    },
                    "required": ["reason"]
                }
            }
        }
    
    async def execute(self, input_data: Dict[str, Any], conversation: List[Dict]) -> Any:
        """Execute LLM handoff"""
        if self.on_handoff:
            await self.on_handoff(input_data, conversation)
        
        # Switch LLM and re-execute
        # Implementation would depend on LLM management system
        pass

class ProcessingPipelineHandoff(Handoff):
    """Handoff to specialized processing pipeline"""
    
    def __init__(self, pipeline_name: str, pipeline_config: Dict[str, Any], **kwargs):
        super().__init__({"name": pipeline_name, **pipeline_config}, **kwargs)
        self.handoff_type = "pipeline"
    
    def to_tool_definition(self) -> Dict[str, Any]:
        pipeline_name = self.target["name"]
        tool_name = self.name or f"process_with_{pipeline_name.replace('-', '_')}"
        description = self.description or f"Process data with {pipeline_name} pipeline"
        
        return {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input_data": {
                            "type": "object",
                            "description": "Data to process",
                            "additionalProperties": True
                        },
                        "pipeline_params": {
                            "type": "object", 
                            "description": "Pipeline-specific parameters",
                            "additionalProperties": True
                        }
                    },
                    "required": ["input_data"]
                }
            }
        }
    
    async def execute(self, input_data: Dict[str, Any], conversation: List[Dict]) -> Any:
        """Execute processing pipeline"""
        if self.on_handoff:
            await self.on_handoff(input_data, conversation)
        
        # Execute specialized processing pipeline
        # Implementation would depend on pipeline system
        pass

# Helper functions for creating handoffs (OpenAI SDK compatible)
def handoff(target: Any, **kwargs) -> Handoff:
    """Create appropriate handoff config based on target type
    
    Note: Some handoff types (Remote agents, CrewAI, n8n workflows) are implemented
    within their respective skills. This helper primarily handles local agents,
    LLM handoffs, and processing pipelines.
    """
    if isinstance(target, str):
        if target.startswith("http://") or target.startswith("https://"):
            # Remote agent handoffs are implemented within NLISkill
            raise ValueError("Remote agent handoffs are implemented within NLISkill")
        elif "workflow" in target.lower() or "n8n" in target.lower():
            # n8n workflow handoffs are implemented within N8nSkill
            raise ValueError("n8n workflow handoffs are implemented within N8nSkill")
        elif "crew" in target.lower():
            # CrewAI handoffs are implemented within CrewAISkill
            raise ValueError("CrewAI handoffs are implemented within CrewAISkill")
        else:
            # Local agent handoff
            return LocalAgentHandoff(target, **kwargs)
    elif hasattr(target, 'run'):
        # Agent instance
        return LocalAgentHandoff(target, **kwargs)
    elif isinstance(target, dict):
        if "model" in target:
            # LLM handoff
            return LLMHandoff(target["model"], target.get("provider", "openai"), **kwargs)
        elif "pipeline" in target or "workflow" in target:
            # Processing pipeline
            return ProcessingPipelineHandoff(target["name"], target, **kwargs)
    
    raise ValueError(f"Unknown handoff target type: {type(target)}")

class BaseAgent(Agent):
    """
    Base implementation for AI agents with OpenAI compatibility
    
    Handles:
    - LLM provider integration (litellm, OpenAI, etc.)
    - Tool execution (@tool decorated functions + external tools)
    - Streaming and non-streaming responses  
    - Usage tracking and pricing integration
    - OpenAI-compatible response formatting
    """
    
    def __init__(self, name: str, instructions: str,
                 model: Optional[Union[str, Any]] = None,
                 tools: List[Callable] = None,
                 skills: Dict[str, Any] = None):
        super().__init__(name, instructions, model, tools)
        
        # Central registries for all agent capabilities
        self._registered_tools = []  # All tools from agent + skills
        self._registered_hooks = {   # All hooks organized by event type
            'on_connection': [],
            'on_request': [],
            'on_chunk': [],
            'on_toolcall': [],
            'on_handoff': [],            # NEW: Called before handoff execution
            'on_response': [],
            'on_finalize_connection': []
        }
        self._registered_handoffs = []  # All handoff configurations
        
        # Thread-safe registration lock
        import threading
        self._registration_lock = threading.Lock()
        
        # Register agent's direct tools first
        if tools:
            for tool in tools:
                self.register_tool(tool, source="agent")
        
        # Handle model parameter intelligently
        skills = skills or {}
        if model is not None:
            skills = self._process_model_parameter(model, skills)
        
        # Skill system
        self.skills = self._initialize_skills_with_defaults(skills)
        self.context = AgentContext(self, self.skills)
        
        # Initialize skills (they will register their capabilities with the agent)
        asyncio.create_task(self._initialize_all_skills())
        
        # Prepare tool definitions for LLM (will be updated as skills register tools)
        self._prepared_tools = self._prepare_tool_definitions()
    
    async def _initialize_all_skills(self):
        """Initialize all skills - they will register their capabilities with the agent"""
        await self.context.initialize_skills()
    
    # ===== CENTRAL REGISTRATION METHODS =====
    # Skills use these methods to register their capabilities with the agent
    
    def register_tool(self, tool_func: Callable, source: str = "skill", scope: str = "all") -> None:
        """Register a tool with the agent (called by skills during initialization)"""
        with self._registration_lock:
            tool_config = {
                'function': tool_func,
                'source': source,  # "agent", "skill_name", etc.
                'scope': scope,    # "all", "owner", "admin"
                'name': getattr(tool_func, '__name__', str(tool_func))
            }
            self._registered_tools.append(tool_config)
            
            # Update prepared tools for LLM
            self._prepared_tools = self._prepare_tool_definitions()
    
    def register_hook(self, event: str, handler: Callable, priority: int = 50, 
                     source: str = "skill") -> None:
        """Register a lifecycle hook with the agent (called by skills during initialization)"""
        with self._registration_lock:
            if event not in self._registered_hooks:
                self._registered_hooks[event] = []
            
            hook_config = {
                'handler': handler,
                'priority': priority,
                'source': source,  # Which skill registered this hook
                'name': getattr(handler, '__name__', str(handler))
            }
            
            self._registered_hooks[event].append(hook_config)
            
            # Sort by priority (lower numbers = higher priority)
            self._registered_hooks[event].sort(key=lambda x: x['priority'])
    
    def register_handoff(self, handoff_config: Union['Handoff', Any], source: str = "skill") -> None:
        """Register a handoff configuration with the agent (similar to OpenAI SDK pattern)"""
        with self._registration_lock:
            # Ensure we have proper metadata
            if not hasattr(handoff_config, 'to_tool_definition'):
                raise ValueError("Invalid handoff config - must be a Handoff object")
            
            # Add source tracking
            handoff_config.source = source
            self._registered_handoffs.append(handoff_config)
    
    def get_handoff_tools(self) -> List[Dict[str, Any]]:
        """Get tool definitions for all registered handoffs (for LLM tool calling)"""
        with self._registration_lock:
            tools = []
            for handoff in self._registered_handoffs:
                tools.append(handoff.to_tool_definition())
            return tools
    
    # ===== CENTRAL CAPABILITY ACCESS METHODS =====
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all registered tools with metadata"""
        with self._registration_lock:
            return self._registered_tools.copy()
    
    def get_tools_by_scope(self, scope: str) -> List[Callable]:
        """Get tools filtered by scope"""
        with self._registration_lock:
            return [tool['function'] for tool in self._registered_tools 
                   if tool.get('scope') == scope or tool.get('scope') == 'all']
    
    def get_hooks_for_event(self, event: str) -> List[Dict[str, Any]]:
        """Get hooks for a specific event (already sorted by priority)"""
        with self._registration_lock:
            return self._registered_hooks.get(event, []).copy()
    
    def get_all_handoffs(self) -> List[Dict[str, Any]]:
        """Get all registered handoffs"""
        with self._registration_lock:
            return self._registered_handoffs.copy()
    
    def get_handoffs_by_type(self, handoff_type: str) -> List[Dict[str, Any]]:
        """Get handoffs filtered by type"""
        with self._registration_lock:
            return [handoff for handoff in self._registered_handoffs
                   if handoff.get('handoff_type') == handoff_type]
    
    async def run(self, messages: List[Dict[str, Any]], stream: bool = False, 
                  tools: Optional[List[OpenAITool]] = None) -> OpenAIResponse:
        """
        Execute agent with OpenAI-compatible interface
        
        Args:
            messages: OpenAI-format messages
            stream: Whether to stream response (handled by server layer)
            tools: External tools from request (merged with agent's @tool functions)
        """
        if stream:
            # For streaming, this method shouldn't be called directly
            # Server layer handles streaming via run_streaming()
            raise ValueError("Use run_streaming() for stream=True")
        
        # Set up context variables for this request
        request_id = f"req_{uuid.uuid4().hex[:8]}"
        REQUEST_ID.set(request_id)
        AGENT_NAME.set(self.name)
        
        # Create request context for hooks
        request_context = RequestContext(
            request_id=request_id,
            messages=messages,
            tools=tools,
            stream=False,
            agent=self
        )
        REQUEST_CONTEXT.set(request_context)
        
        # Execute on_request hooks (auth, payment validation, input safety, memory retrieval)
        # Hooks can access context via contextvars or receive it as parameter
        request_context = await self._execute_hooks("on_request", request_context)
        
        # Merge tools: agent's @tool functions + external tools from request
        all_tools = self._merge_tools(tools)
        
        # Prepare messages with system prompt
        formatted_messages = self._prepare_messages(messages)
        
        # Execute LLM call via LLM skill
        llm_skill = self.context.get_llm_skill()
        llm_response = await llm_skill.chat_completion(
            messages=formatted_messages,
            tools=all_tools,
            stream=False
        )
        
        # Handle tool calls if present
        if self._has_tool_calls(llm_response):
            llm_response = await self._handle_tool_calls(llm_response, formatted_messages, all_tools)
        
        # Convert to OpenAI format
        openai_response = self._format_openai_response(llm_response)
        
        # Create response context for hooks
        response_context = {
            **request_context,
            "response": openai_response,
            "llm_response": llm_response
        }
        
        # Execute on_response hooks (output safety, payment charging, memory storage)
        response_context = await self._execute_hooks("on_response", response_context)
        
        return response_context.get("response", openai_response)
    
    async def run_streaming(self, messages: List[Dict[str, Any]], 
                           tools: Optional[List[OpenAITool]] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute agent with streaming OpenAI-compatible response chunks"""
        
        # Set up context variables for streaming request
        request_id = f"req_{uuid.uuid4().hex[:8]}"
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
        REQUEST_ID.set(request_id)
        AGENT_NAME.set(self.name)
        
        # Create request context for hooks
        request_context = RequestContext(
            request_id=request_id,
            messages=messages,
            tools=tools,
            stream=True,
            agent=self,
            completion_id=completion_id
        )
        REQUEST_CONTEXT.set(request_context)
        
        # Execute on_request hooks (auth, payment validation, input safety, memory retrieval)
        request_context = await self._execute_hooks("on_request", request_context)
        
        # Merge tools
        all_tools = self._merge_tools(tools)
        
        # Prepare messages  
        formatted_messages = self._prepare_messages(messages)
        
        # Start streaming LLM call
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
        created_time = int(time.time())
        
        # Initial chunk with role
        yield {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": created_time,
            "model": self.name,  # Use agent name as model
            "choices": [{
                "index": 0,
                "delta": {"role": "assistant", "content": ""},
                "finish_reason": None
            }]
        }
        
        # Stream content via LLM skill
        llm_skill = self.context.get_llm_skill()
        full_content = ""
        tool_calls = []
        
        async for chunk in llm_skill.chat_completion_stream(
            messages=formatted_messages,
            tools=all_tools
        ):
            
            if chunk.get("choices", [{}])[0].get("delta", {}).get("content"):
                # Content chunk
                content = chunk["choices"][0]["delta"]["content"]
                full_content += content
                
                chunk_data = {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": created_time,
                    "model": self.name,
                    "choices": [{
                        "index": 0,
                        "delta": {"content": content},
                        "finish_reason": None
                    }]
                }
                
                # Execute on_chunk hooks (content filtering, real-time processing)
                chunk_context = {
                    **request_context,
                    "chunk": chunk_data,
                    "content": content,
                    "full_content_so_far": full_content,
                    "completion_id": completion_id
                }
                chunk_context = await self._execute_hooks("on_chunk", chunk_context)
                
                # Yield potentially modified chunk
                yield chunk_context.get("chunk", chunk_data)
            
            elif chunk.get("choices", [{}])[0].get("delta", {}).get("tool_calls"):
                # Tool call chunk
                tool_calls.extend(chunk["choices"][0]["delta"]["tool_calls"])
        
        # Handle tool calls if present
        if tool_calls:
            async for tool_chunk in self._handle_streaming_tool_calls(
                tool_calls, formatted_messages, all_tools, completion_id, created_time
            ):
                yield tool_chunk
        
        # Final chunk with usage
        usage_info = self._calculate_usage(formatted_messages, full_content, tool_calls)
        
        final_chunk = {
            "id": completion_id,
            "object": "chat.completion.chunk", 
            "created": created_time,
            "model": self.name,
            "choices": [{
                "index": 0,
                "delta": {},
                "finish_reason": "stop"
            }],
            "usage": usage_info.__dict__
        }
        
        # Create response context for hooks
        response_context = {
            **request_context,
            "response": {
                "content": full_content,
                "tool_calls": tool_calls,
                "usage": usage_info
            },
            "completion_id": completion_id,
            "final_chunk": final_chunk
        }
        
        # Execute on_response hooks (output safety, payment charging, memory storage)
        response_context = await self._execute_hooks("on_response", response_context)
        
        # Yield final chunk (potentially modified by hooks)
        yield response_context.get("final_chunk", final_chunk)
    
    def _process_model_parameter(self, model: Union[str, Any], skills: Dict[str, Any]) -> Dict[str, Any]:
        """Process model parameter and add appropriate LLM skill"""
        if isinstance(model, str):
            # Parse skill/model format: "skill_name/model_name"
            if "/" in model:
                skill_name, model_name = model.split("/", 1)  # Split on first "/" only
                
                # Create appropriate skill based on skill name
                if skill_name == "openai":
                    from robutler.agents.skills.core.llm.openai import OpenAISkill
                    skills["primary_llm"] = OpenAISkill({
                        "model": model_name,
                        "api_key": None  # Will use environment variables
                    })
                elif skill_name == "anthropic":
                    from robutler.agents.skills.core.llm.anthropic import AnthropicSkill
                    skills["primary_llm"] = AnthropicSkill({
                        "model": model_name,
                        "api_key": None
                    })
                elif skill_name == "xai":
                    from robutler.agents.skills.core.llm.xai import XAISkill
                    skills["primary_llm"] = XAISkill({
                        "model": model_name,
                        "api_key": None
                    })
                elif skill_name == "litellm":
                    from robutler.agents.skills.core.llm.litellm import LiteLLMSkill
                    skills["primary_llm"] = LiteLLMSkill({
                        "model": model_name,  # e.g., "openai/gpt-4o" or "claude-3-sonnet"
                        "api_key": None
                    })
                else:
                    raise ValueError(f"Unknown LLM skill: {skill_name}")
            else:
                raise ValueError(f"Model string must be in format 'skill_name/model_name', got: {model}")
        else:
            # Assume it's an LLM skill instance
            skills["primary_llm"] = model
        
        return skills
    
    def _initialize_skills_with_defaults(self, provided_skills: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize skills, auto-adding missing core skills with defaults and resolving dependencies"""
        skills = provided_skills.copy()
        
        # Default core skills (only add if not provided)
        core_defaults = {
            "litellm": LiteLLMSkill(),
        }
        
        # Add missing core skills with defaults
        for name, default_skill in core_defaults.items():
            if name not in skills:
                skills[name] = default_skill
        
        # Resolve skill dependencies - if a skill has dependencies, auto-include them
        skills = self._resolve_skill_dependencies(skills, core_defaults)
        
        return skills
    
    def _resolve_skill_dependencies(self, skills: Dict[str, Any], available_defaults: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve skill dependencies by automatically including required skills"""
        resolved_skills = skills.copy()
        to_process = list(skills.keys())
        processed = set()
        
        while to_process:
            skill_name = to_process.pop(0)
            if skill_name in processed:
                continue
                
            skill = resolved_skills[skill_name]
            dependencies = skill.get_dependencies() if hasattr(skill, 'get_dependencies') else []
            
            for dep_name in dependencies:
                if dep_name not in resolved_skills:
                    # Try to find dependency in available defaults
                    if dep_name in available_defaults:
                        resolved_skills[dep_name] = available_defaults[dep_name]
                        to_process.append(dep_name)  # Process new dependency's dependencies
                    else:
                        # Could raise warning or error, for now just log
                        print(f"Warning: Skill '{skill_name}' depends on '{dep_name}' but it's not available")
            
            processed.add(skill_name)
        
        return resolved_skills
    
    def _merge_tools(self, external_tools: Optional[List[OpenAITool]] = None) -> List[OpenAITool]:
        """Merge agent's @tool functions with external tools from request"""
        merged_tools = []
        
        # Add agent's @tool decorated functions
        merged_tools.extend(self._prepared_tools)
        
        # Add external tools from request
        if external_tools:
            merged_tools.extend(external_tools)
        
        return merged_tools
    
    def _prepare_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare messages with system prompt"""
        formatted_messages = []
        
        # Add system message if instructions provided
        if self.instructions:
            formatted_messages.append({
                "role": "system",
                "content": self.instructions
            })
        
        # Add user messages
        formatted_messages.extend(messages)
        
        return formatted_messages
    
    def _prepare_tool_definitions(self) -> List[OpenAITool]:
        """Prepare OpenAI tool definitions from @tool decorated functions"""
        tool_definitions = []
        
        for tool_func in self.tools:
            if hasattr(tool_func, '_robutler_tool_definition'):
                # Extract tool definition from @tool decorator
                tool_def = tool_func._robutler_tool_definition
                tool_definitions.append(OpenAITool(
                    type="function",
                    function={
                        "name": tool_def["name"],
                        "description": tool_def["description"],
                        "parameters": tool_def["parameters"]
                    }
                ))
        
        return tool_definitions
    
    def _format_openai_response(self, llm_response: Dict) -> OpenAIResponse:
        """Convert LLM provider response to OpenAI format"""
        
        # Extract content and usage from provider response
        content = self._extract_content(llm_response)
        usage_data = self._extract_usage(llm_response)
        
        return OpenAIResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
            object="chat.completion",
            created=int(time.time()),
            model=self.name,
            choices=[
                OpenAIChoice(
                    index=0,
                    message={
                        "role": "assistant",
                        "content": content
                    },
                    finish_reason="stop"
                )
            ],
            usage=OpenAIUsage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0)
            )
        )
    
    async def _execute_hooks(self, hook_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute registered hooks of the specified type in priority order"""
        
                    # Get hooks from central registry (already sorted by priority)
            hooks_for_event = self.get_hooks_for_event(hook_name)
            
            # Execute hooks in priority order
            for hook_config in hooks_for_event:
                try:
                    hook_func = hook_config['handler']
                    source = hook_config['source']
                    
                    # Call the hook function with the context
                    context = await hook_func(context)
                    
                    # Ensure context is still a dict
                    if not isinstance(context, dict):
                        hook_name_str = hook_config.get('name', str(hook_func))
                        raise ValueError(f"Hook {hook_name_str} from {source} must return a dict")
                        
                except Exception as e:
                    # Log error but continue with other hooks
                    hook_name_str = hook_config.get('name', str(hook_func))
                    source = hook_config.get('source', 'unknown')
                    print(f"Error in {hook_name} hook {hook_name_str} from {source}: {e}")
            
            return context
    
    async def _execute_handoff_hooks(self, handoff_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute on_handoff lifecycle hooks (filtering, validation, logging)"""
        return await self._execute_hooks("on_handoff", handoff_context)

# Example: GuardrailsSkill implementing handoff filtering via on_handoff hook
class GuardrailsSkill(Skill):
    """Content safety and filtering skill with handoff filtering capabilities"""
    
    async def initialize(self, agent_context) -> None:
        """Initialize guardrails skill and register hooks"""
        self.agent_context = agent_context
        
        # Register lifecycle hooks  
        self.register_hook('on_request', self._filter_input, priority=5)
        self.register_hook('on_response', self._filter_output, priority=95)
        self.register_hook('on_handoff', self._filter_handoff, priority=10)  # NEW: Handoff filtering
    
    async def _filter_handoff(self, handoff_context: Dict[str, Any]) -> Dict[str, Any]:
        """Filter conversation and validate handoff before execution"""
        conversation = handoff_context.get("conversation", [])
        handoff_type = handoff_context.get("handoff_type")
        target = handoff_context.get("target")
        
        # Remove sensitive information from conversation before handoff
        filtered_conversation = []
        for message in conversation:
            content = message.get("content", "")
            
            # Apply content filtering
            if not self._contains_sensitive_info(content):
                # Clean up the message content
                filtered_content = self._sanitize_content(content)
                filtered_message = {**message, "content": filtered_content}
                filtered_conversation.append(filtered_message)
        
        # Validate handoff target
        if not self._is_handoff_allowed(handoff_type, target):
            raise ValueError(f"Handoff to {handoff_type}:{target} not allowed by security policy")
        
        # Update context with filtered conversation
        handoff_context["filtered_conversation"] = filtered_conversation
        
        # Log handoff for audit
        await self._log_handoff(handoff_context)
        
        return handoff_context
    
    def _contains_sensitive_info(self, content: str) -> bool:
        """Check if content contains sensitive information"""
        sensitive_patterns = ["password", "api_key", "secret", "token", "ssn", "credit_card"]
        return any(pattern in content.lower() for pattern in sensitive_patterns)
    
    def _sanitize_content(self, content: str) -> str:
        """Sanitize content by removing/masking sensitive data"""
        # Implementation would mask or remove sensitive patterns
        import re
        # Example: mask potential API keys
        content = re.sub(r'[a-zA-Z0-9]{32,}', '[REDACTED_KEY]', content)
        return content
    
    def _is_handoff_allowed(self, handoff_type: str, target: str) -> bool:
        """Check if handoff is allowed by security policy"""
        # Example security policy
        allowed_handoffs = self.config.get('allowed_handoffs', {})
        
        if handoff_type == "remote_agent":
            allowed_domains = allowed_handoffs.get('remote_domains', [])
            return any(domain in target for domain in allowed_domains)
        elif handoff_type == "local_agent":
            allowed_agents = allowed_handoffs.get('local_agents', ["*"])
            return "*" in allowed_agents or target in allowed_agents
        
        return True  # Default: allow other handoff types
    
    async def _log_handoff(self, handoff_context: Dict[str, Any]) -> None:
        """Log handoff for security audit"""
        print(f"🔒 Handoff filtered: {handoff_context['handoff_type']} -> {handoff_context['target']}")
        # In production: send to audit log
        pass
    
    async def _handle_tool_calls(self, llm_response: Dict[str, Any], 
                                messages: List[Dict[str, Any]], 
                                tools: List[Callable]) -> Dict[str, Any]:
        """Handle tool calls in non-streaming mode with on_toolcall hooks"""
        
        tool_calls = llm_response.get("tool_calls", [])
        if not tool_calls:
            return llm_response
            
        # Process each tool call
        tool_results = []
        for tool_call in tool_calls:
            
            # Execute on_toolcall hooks (validation, logging, modification)
            toolcall_context = {
                "tool_call": tool_call,
                "available_tools": tools,
                "messages": messages,
                "agent": self
            }
            toolcall_context = await self._execute_hooks("on_toolcall", toolcall_context)
            
            # Get potentially modified tool call
            modified_tool_call = toolcall_context.get("tool_call", tool_call)
            
            # Execute the tool
            try:
                result = await self._execute_single_tool(modified_tool_call, tools)
                tool_results.append(result)
            except Exception as e:
                tool_results.append({
                    "tool_call_id": modified_tool_call.get("id"),
                    "role": "tool", 
                    "content": f"Error: {str(e)}"
                })
        
        # Add tool results to messages and get final response
        messages_with_tools = messages + [
            {"role": "assistant", "tool_calls": tool_calls}
        ] + tool_results
        
        # Get final LLM response
        llm_skill = self.context.get_llm_skill()
        return await llm_skill.chat_completion(
            messages=messages_with_tools,
            tools=tools,
            stream=False
        )
    
    async def _handle_streaming_tool_calls(self, tool_calls: List[Dict[str, Any]], 
                                          messages: List[Dict[str, Any]], 
                                          tools: List[Callable],
                                          completion_id: str, 
                                          created_time: int) -> AsyncGenerator[Dict[str, Any], None]:
        """Handle tool calls in streaming mode with on_toolcall hooks"""
        
        # Process each tool call
        tool_results = []
        for tool_call in tool_calls:
            
            # Execute on_toolcall hooks 
            toolcall_context = {
                "tool_call": tool_call,
                "available_tools": tools,
                "messages": messages,
                "agent": self,
                "streaming": True,
                "completion_id": completion_id
            }
            toolcall_context = await self._execute_hooks("on_toolcall", toolcall_context)
            
            # Get potentially modified tool call
            modified_tool_call = toolcall_context.get("tool_call", tool_call)
            
            # Execute the tool
            try:
                result = await self._execute_single_tool(modified_tool_call, tools)
                tool_results.append(result)
                
                # Yield tool execution chunk
                yield {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": created_time,
                    "model": self.name,
                    "choices": [{
                        "index": 0,
                        "delta": {"tool_calls": [{"type": "function", "function": {"name": modified_tool_call["function"]["name"]}}]},
                        "finish_reason": None
                    }]
                }
                
            except Exception as e:
                error_result = {
                    "tool_call_id": modified_tool_call.get("id"),
                    "role": "tool",
                    "content": f"Error: {str(e)}"
                }
                tool_results.append(error_result)
        
        # If we had tool calls, get final response from LLM
        if tool_results:
            messages_with_tools = messages + [
                {"role": "assistant", "tool_calls": tool_calls}
            ] + tool_results
            
            # Stream final LLM response after tool execution
            llm_skill = self.context.get_llm_skill()
            async for final_chunk in llm_skill.chat_completion_stream(
                messages=messages_with_tools,
                tools=tools
            ):
                yield final_chunk
    
    async def _execute_single_tool(self, tool_call: Dict[str, Any], tools: List[Callable]) -> Dict[str, Any]:
        """Execute a single tool call"""
        import json
        import asyncio
        
        function_name = tool_call["function"]["name"]
        function_args = json.loads(tool_call["function"]["arguments"])
        
        # Find the tool function
        tool_func = None
        for tool in tools:
            if hasattr(tool, '__name__') and tool.__name__ == function_name:
                tool_func = tool
                break
        
        if not tool_func:
            raise ValueError(f"Tool {function_name} not found")
        
        # Execute the tool
        if asyncio.iscoroutinefunction(tool_func):
            result = await tool_func(**function_args)
        else:
            result = tool_func(**function_args)
        
        return {
            "tool_call_id": tool_call.get("id"),
            "role": "tool",
            "content": str(result)
        }

```

---

## 4. Agent Context System

The agent context provides comprehensive access to all agent capabilities including skills, tools, hooks, and memory systems. It serves as the central registry and access point for all agent functionality.

**Key Components in AgentContext (via Agent's Central Registry):**
- ✅ **Skills**: All registered skills (core, platform, custom)
- ✅ **Tools**: All tools registered by agent and skills (centrally managed)
- ✅ **Hooks**: All lifecycle hooks with priorities (centrally managed)
- ✅ **Handoffs**: All flexible routing configurations (centrally managed)
- ✅ **Memory**: Access to all memory skills (short/long/vector)
- ✅ **LLM**: Primary and fallback LLM providers
- ✅ **Platform**: Integration skills (robutler.payments, robutler.auth, etc.)
- ❌ **Pricing**: Handled by PaymentSkill, NOT in context

**Central Registration Architecture:**
- 🎯 **Agent is the Registry**: All tools, hooks, and handoffs are registered with the agent
- 🔧 **Skills Register via Agent**: Skills call `self.agent_context.agent.register_*()` methods
- 📊 **Unified Management**: Single source of truth for all agent capabilities
- 🛡️ **Thread-Safe**: Agent provides thread-safe registration and access

**OpenAI SDK-Compatible Handoff System:**
- 🤖 **LocalAgentHandoff**: Transfer to agents in same Robutler instance
- 🌐 **RemoteAgentHandoff**: Call external agents via NLI skill
- 🎭 **CrewAIHandoff**: Deploy multi-agent CrewAI crews via CrewAI skill
- 🔧 **N8nWorkflowHandoff**: Execute n8n workflows via n8n skill  
- 🧠 **LLMHandoff**: Switch to different LLM models for specialized tasks
- ⚙️ **ProcessingPipelineHandoff**: Route to specialized processing pipelines
- 🎯 **handoff() Helper**: Auto-detect target type and create appropriate config
- 📝 **Full Customization**: name, description, on_handoff
- 🔒 **on_handoff Lifecycle Event**: Filtering handled by GuardrailsSkill via hooks (no input_filter needed)

```python
# robutler/agents/core/context.py
from typing import Dict, Any, Optional, List

class AgentContext:
    """
    Agent context providing unified access to skills, tools, hooks, and capabilities
    
    This context is passed to skills during initialization and provides
    a clean interface for skills to interact with the agent and other skills.
    All agent capabilities are accessible through this context.
    """
    
    def __init__(self, agent: 'BaseAgent', skills: Dict[str, Any]):
        self.agent = agent
        self.skills = skills
        self._initialized_skills = set()
    
    async def initialize_skills(self):
        """Initialize all skills with this context"""
        for skill_name, skill in self.skills.items():
            if skill_name not in self._initialized_skills:
                await skill.initialize(self)
                self._initialized_skills.add(skill_name)
    
    def get_skill(self, skill_name: str) -> Optional[Any]:
        """Get a skill by name"""
        return self.skills.get(skill_name)
    
    def get_all_skills(self) -> Dict[str, Any]:
        """Get all available skills"""
        return self.skills.copy()
    
    def get_tools(self) -> List[Callable]:
        """Get all registered tools (delegates to agent's central registry)"""
        return [tool['function'] for tool in self.agent.get_all_tools()]
    
    def get_tools_with_metadata(self) -> List[Dict[str, Any]]:
        """Get all tools with full metadata"""
        return self.agent.get_all_tools()
    
    def get_hooks(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all hooks organized by event type (delegates to agent's central registry)"""
        all_hooks = {}
        
        for event_type in ['on_connection', 'on_request', 'on_chunk', 
                          'on_toolcall', 'on_response', 'on_finalize_connection']:
            all_hooks[event_type] = self.agent.get_hooks_for_event(event_type)
        
        return all_hooks
    
    def get_llm_skill(self) -> Any:
        """Get the primary LLM skill (tries primary_llm first, then defaults)"""
        # First priority: primary_llm from model parameter
        if "primary_llm" in self.skills:
            return self.skills["primary_llm"]
        # Fallback: prefer LiteLLM for cross-provider routing
        elif "litellm" in self.skills:
            return self.skills["litellm"]
        elif "openai" in self.skills:
            return self.skills["openai"]
        elif "anthropic" in self.skills:
            return self.skills["anthropic"]
        else:
            raise ValueError("No LLM skill available")
    
    def get_memory_skills(self) -> Dict[str, Any]:
        """Get all memory-related skills"""
        memory_skills = {}
        for name, skill in self.skills.items():
            if 'memory' in name.lower() or hasattr(skill, '_is_memory_skill'):
                memory_skills[name] = skill
        return memory_skills
    
    def get_platform_skills(self) -> Dict[str, Any]:
        """Get platform integration skills (robutler.* skills)"""
        platform_skills = {}
        for name, skill in self.skills.items():
            if name.startswith('robutler.') or hasattr(skill, '_is_platform_skill'):
                platform_skills[name] = skill
        return platform_skills
    
    def get_handoffs(self) -> List[Dict[str, Any]]:
        """Get all registered handoff configurations (delegates to agent's central registry)"""
        return self.agent.get_all_handoffs()
    
    def get_handoffs_by_type(self, handoff_type: str) -> List[Dict[str, Any]]:
        """Get handoffs filtered by type (delegates to agent's central registry)"""
        return self.agent.get_handoffs_by_type(handoff_type)
    
    def skill_available(self, skill_name: str) -> bool:
        """Check if a skill is available and initialized"""
        return (skill_name in self.skills and 
                skill_name in self._initialized_skills)
    
    async def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get comprehensive agent capabilities summary"""
        handoffs = self.get_handoffs()
        handoff_summary = {}
        for handoff_type in ["agent", "llm", "pipeline", "skill"]:
            type_handoffs = self.get_handoffs_by_type(handoff_type)
            handoff_summary[handoff_type] = len(type_handoffs)
        
        return {
            "agent_name": self.agent.name,
            "skills": list(self.skills.keys()),
            "tools": [getattr(tool, '__name__', str(tool)) for tool in self.get_tools()],
            "hooks": {event: len(hooks) for event, hooks in self.get_hooks().items()},
            "handoffs": handoff_summary,
            "total_handoffs": len(handoffs),
            "memory_skills": list(self.get_memory_skills().keys()),
            "platform_skills": list(self.get_platform_skills().keys()),
            "llm_provider": type(self.get_llm_skill()).__name__ if self.skills else None
        }


# Example: Using the enhanced AgentContext
async def example_agent_context_usage():
    """Example showing comprehensive AgentContext usage"""
    
    # Create agent with skills
    agent = BaseAgent(
        name="research-agent",
        instructions="Research and analysis agent",
        skills={
            "memory_short": ShortTermMemorySkill(),
            "memory_vector": VectorMemorySkill(),
            "robutler.payments": PaymentSkill(),
            "google": GoogleSkill(),
            "primary_llm": OpenAISkill({"model": "gpt-4o"})
        }
    )
    
    # Access via context
    context = agent.context
    
    # ✅ Skills access
    memory_skill = context.get_skill("memory_short")
    all_skills = context.get_all_skills()  # {'memory_short': ..., 'google': ...}
    platform_skills = context.get_platform_skills()  # {'robutler.payments': ...}
    
    # ✅ Tools access (from agent's central registry)
    all_tools = context.get_tools()  # All tools registered with agent
    tools_with_metadata = context.get_tools_with_metadata()  # Includes source, scope
    print(f"Available tools: {[tool.__name__ for tool in all_tools]}")
    print(f"Tool sources: {set(tool['source'] for tool in tools_with_metadata)}")
    
    # ✅ Hooks access (from agent's central registry)
    hooks = context.get_hooks()  # All hooks with metadata
    print(f"Request hooks: {len(hooks['on_request'])}")
    print(f"Chunk hooks: {len(hooks['on_chunk'])}")
    print(f"Tool hooks: {len(hooks['on_toolcall'])}")
    
    # ✅ Handoffs access (from agent's central registry)
    all_handoffs = context.get_handoffs()
    agent_handoffs = context.get_handoffs_by_type("agent")
    llm_handoffs = context.get_handoffs_by_type("llm")
    print(f"Total handoffs: {len(all_handoffs)}")
    print(f"Agent handoffs: {len(agent_handoffs)}")
    print(f"LLM handoffs: {len(llm_handoffs)}")
    
    # ✅ Direct agent registry access
    print(f"Tools by scope 'admin': {len(agent.get_tools_by_scope('admin'))}")
    print(f"All registered capabilities managed centrally by agent")
    
    # ✅ Memory systems
    memory_skills = context.get_memory_skills()  # All memory-related skills
    
    # ✅ LLM access
    llm = context.get_llm_skill()  # Primary LLM provider
    
    # ✅ Capabilities overview
    capabilities = await context.get_agent_capabilities()
    print(f"Agent capabilities: {capabilities}")
    
    # ❌ NO PRICING ACCESS - handled by PaymentSkill
    # pricing = context.get_pricing()  # NOT AVAILABLE - pricing in PaymentSkill only
    
    # 🎯 OpenAI SDK-compatible handoffs (registered as tools for LLM)
    handoff_tools = agent.get_handoff_tools()  # Get tool definitions for LLM
    print(f"Handoff tools available to LLM: {[tool['function']['name'] for tool in handoff_tools]}")
    # Example tools: ["escalate_to_coding_expert", "consult_external_expert", 
    #                "deploy_research_crew", "trigger_data_workflow",
    #                "switch_to_creative_model", "process_multimodal_content"]
    
    # 🔒 on_handoff Lifecycle Event: Handoff filtering and validation
    # GuardrailsSkill automatically filters all handoffs via on_handoff hooks:
    # - Removes sensitive data from conversation history 
    # - Validates handoff targets against security policy
    # - Logs handoffs for security audit
    # - No need for separate input_filter parameters
```

---

## 5. Agent Factory

The factory pattern provides consistent agent creation with validation and configuration management.

```python
# robutler/agents/core/factory.py
from typing import List, Dict, Any, Optional, Callable
from .base_agent import BaseAgent
from ..tools.decorators import tool

class AgentFactory:
    """Factory for creating agents with consistent configuration"""
    
    @staticmethod
    def create_agent(name: str, instructions: str, **kwargs) -> BaseAgent:
        """Create a new agent instance with validation"""
        
        # Validate agent name (URL-safe)
        if not name.replace("-", "").replace("_", "").isalnum():
            raise ValueError(f"Agent name '{name}' must be URL-safe (alphanumeric, hyphens, underscores)")
        
        return BaseAgent(
            name=name,
            instructions=instructions,
            **kwargs
        )
    
    @staticmethod
    def from_config(config: Dict[str, Any]) -> BaseAgent:
        """Create agent from configuration dictionary"""
        
        # Extract tools if specified
        tools = []
        if "tools" in config:
            tools = AgentFactory._resolve_tools(config["tools"])
        
        # Extract skills if specified
        skills = config.get("skills", {})
        
        return AgentFactory.create_agent(
            name=config["name"],
            instructions=config["instructions"],
            tools=tools,
            skills=skills
            # Note: Intents are handled by DiscoverySkill, not at agent level
        )
    
    @staticmethod
    def _resolve_tools(tool_specs: List[Dict[str, Any]]) -> List[Callable]:
        """Resolve tool specifications to callable functions"""
        # This would handle dynamic tool loading, imports, etc.
        # For now, return empty list - tools are typically passed directly
        return []

# Convenience function for creating agents
def create_agent(name: str, instructions: str, **kwargs) -> BaseAgent:
    """Convenience function for creating agents"""
    return AgentFactory.create_agent(name, instructions, **kwargs)
```

---

## 6. Tool System

### Tool and HTTP Decorators

```python
# robutler/agents/tools/decorators.py
from functools import wraps
from typing import Callable, Dict, Any, get_type_hints, Union, List
import inspect
import json

def tool(func: Callable = None, *, name: str = None, description: str = None, scope: Union[str, List[str]] = "all"):
    """
    Decorator to mark functions as tools available to AI agents
    
    Automatically generates OpenAI-compatible function definitions from:
    - Function name (or custom name)
    - Docstring (or custom description)  
    - Type hints for parameters
    - Default values
    
    Args:
        name: Custom tool name (defaults to function name)
        description: Custom description (defaults to docstring)
        scope: Access scope - "all", "owner", "admin", or list of scopes
    
    Usage:
        @tool
        def get_weather(location: str, units: str = "celsius") -> str:
            '''Get current weather for a location'''
            return f"Weather in {location}: 20°{units[0].upper()}"
            
        @tool(name="custom_name", description="Custom description", scope="owner")
        def my_function(param: int) -> str:
            return str(param)
    """
    def decorator(f: Callable) -> Callable:
        # Extract function metadata
        func_name = name or f.__name__
        func_description = description or (f.__doc__ or f"Execute {func_name}").strip()
        
        # Generate OpenAI function schema from type hints
        schema = _generate_function_schema(f, func_name, func_description)
        
        # Store tool definition on function for agent discovery
        f._robutler_tool_definition = schema
        f._robutler_is_tool = True
        f._tool_scope = scope
        
        return f
    
    if func is None:
        # Called with arguments: @tool(name="...", description="...")
        return decorator
    else:
        # Called without arguments: @tool
        return decorator(func)

def http(subpath: str, method: str = "get", scope: Union[str, List[str]] = "all"):
    """Decorator to mark functions as HTTP handlers for automatic registration
    
    Args:
        subpath: URL path after agent name (e.g., "/myapi" -> /{agentname}/myapi)
        method: HTTP method - "get", "post", "put", "delete", etc. (default: "get")
        scope: Access scope - "all", "owner", "admin", or list of scopes
    
    HTTP handler functions receive FastAPI request arguments directly:
    
    @http("/weather", method="get", scope="owner")
    def get_weather(location: str, units: str = "celsius") -> dict:
        # Function receives query parameters as arguments
        return {"location": location, "temperature": 25, "units": units}
    
    @http("/data", method="post")
    async def post_data(request: Request, data: dict) -> dict:
        # Function can receive Request object and body data
        return {"received": data, "status": "success"}
    """
    def decorator(func: Callable) -> Callable:
        # Validate HTTP method
        valid_methods = ["get", "post", "put", "delete", "patch", "head", "options"]
        if method.lower() not in valid_methods:
            raise ValueError(f"Invalid HTTP method '{method}'. Must be one of: {valid_methods}")
        
        # Ensure subpath starts with /
        normalized_subpath = subpath if subpath.startswith('/') else f'/{subpath}'
        
        # Mark function with metadata for BaseAgent discovery
        func._robutler_is_http = True
        func._http_subpath = normalized_subpath
        func._http_method = method.lower()
        func._http_scope = scope
        func._http_description = func.__doc__ or f"HTTP {method.upper()} handler for {normalized_subpath}"
        
        return func
    
    return decorator

def hook(event: str, priority: int = 50, scope: Union[str, List[str]] = "all"):
    """Decorator to mark functions as lifecycle hooks
    
    Args:
        event: Hook event type - "on_request", "on_chunk", "on_response", etc.
        priority: Execution priority (lower numbers = higher priority)
        scope: Access scope for hook execution
    """
    def decorator(func: Callable) -> Callable:
        func._robutler_is_hook = True
        func._hook_event_type = event
        func._hook_priority = priority
        func._hook_scope = scope
        return func
    return decorator

def handoff(name: str = None, handoff_type: str = "agent", 
           description: str = None, scope: Union[str, List[str]] = "all"):
    """Decorator to mark functions as handoff handlers
    
    Args:
        name: Handoff name (defaults to function name)
        handoff_type: Type of handoff - "agent", "llm", "pipeline"
        description: Handoff description
        scope: Access scope for handoff execution
    """
    def decorator(func: Callable) -> Callable:
        func._robutler_is_handoff = True
        func._handoff_name = name or func.__name__
        func._handoff_type = handoff_type
        func._handoff_description = description or func.__doc__ or f"Handoff: {func.__name__}"
        func._handoff_scope = scope
        return func
    return decorator

```

---

## 7. Request Context Management

The request context system manages the lifecycle of individual requests using Python's `contextvars` for async-safe context propagation.

```python
# robutler/server/context/context_vars.py
from contextvars import ContextVar
from typing import Optional
import uuid

# Context variables for request tracking
REQUEST_ID: ContextVar[str] = ContextVar('request_id')
USER_ID: ContextVar[str] = ContextVar('user_id') 
AGENT_NAME: ContextVar[str] = ContextVar('agent_name')
REQUEST_CONTEXT: ContextVar['RequestContext'] = ContextVar('request_context')
STREAMING_CONTEXT: ContextVar['StreamingContext'] = ContextVar('streaming_context')

def get_request_id() -> str:
    """Get current request ID from context"""
    return REQUEST_ID.get(f"req_{uuid.uuid4().hex[:8]}")

def get_user_id() -> Optional[str]:
    """Get current user ID from context"""
    try:
        return USER_ID.get()
    except LookupError:
        return None

def get_agent_name() -> Optional[str]:
    """Get current agent name from context"""
    try:
        return AGENT_NAME.get()
    except LookupError:
        return None

def get_request_context() -> Optional['RequestContext']:
    """Get full request context"""
    try:
        return REQUEST_CONTEXT.get()
    except LookupError:
        return None
```

```python
# robutler/server/context/request_context.py
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

@dataclass
class UsageRecord:
    id: str
    timestamp: datetime
    credits: float
    reason: str
    kind: str
    metadata: Dict[str, Any]

@dataclass
class UserContext:
    peer_user_id: str
    payment_user_id: str
    origin_user_id: Optional[str] = None
    agent_owner_user_id: Optional[str] = None

@dataclass 
class AgentInfo:
    """Simple agent info for request context (distinct from main AgentContext)"""
    name: str
    instance: Any
    api_key: Optional[str] = None
    # Note: Pricing is handled by PaymentSkill, not at agent level

@dataclass
class RequestContext:
    """Enhanced request context with contextvars integration"""
    request_id: str
    start_time: datetime = field(default_factory=datetime.utcnow)
    user: Optional[UserContext] = None
    agent: Optional[Any] = None  # BaseAgent instance  
    agent_info: Optional[AgentInfo] = None  # Simple agent metadata
    
    # Request-specific data
    messages: List[Dict[str, Any]] = field(default_factory=list)
    tools: Optional[List[Any]] = None
    stream: bool = False
    completion_id: Optional[str] = None
    
    # Legacy fields
    data: Dict[str, Any] = field(default_factory=dict)
    usage_records: List[UsageRecord] = field(default_factory=list)
    
    def track_usage(self, credits: float, reason: str, metadata: Dict[str, Any] = None, kind: str = "unspecified") -> str:
        """Track usage in this request context"""
        usage_id = str(uuid.uuid4())
        record = UsageRecord(
            id=usage_id,
            timestamp=datetime.utcnow(), 
            credits=credits,
            reason=reason,
            kind=kind,
            metadata=metadata or {}
        )
        self.usage_records.append(record)
        return usage_id

class ContextManager:
    """Manages request context lifecycle"""
    
    def __init__(self):
        self._contexts: Dict[str, RequestContext] = {}
    
    def create_context(self, request_id: str, user: UserContext) -> RequestContext:
        context = RequestContext(
            request_id=request_id,
            start_time=datetime.utcnow(),
            user=user
        )
        self._contexts[request_id] = context
        return context
    
    def get_context(self, request_id: str) -> Optional[RequestContext]:
        return self._contexts.get(request_id)
    
    def cleanup_context(self, request_id: str) -> None:
        self._contexts.pop(request_id, None)
```

---

## Summary

Chapter 2 provides the foundational architecture for Robutler V2, including:

✅ **Core Framework Structure** - Complete project organization  
✅ **Core Interfaces** - Agent, Tool, and Service interfaces  
✅ **BaseAgent Implementation** - Full agent implementation with skill integration  
✅ **Agent Context System** - Unified access to agent's centrally registered capabilities  
✅ **Agent Factory** - Consistent agent creation and configuration  
✅ **Tool System** - @tool decorator and schema generation  
✅ **Request Context Management** - Request lifecycle and usage tracking  

**Next**: [Chapter 3: Skills System](./ROBUTLER_V2_DESIGN_Ch3_Skills_System.md) - Complete skill implementation details 