# Robutler V2 Design Document - Chapter 3: Skills System

## Overview

This chapter covers the complete skills system implementation - the core architectural feature of Robutler V2. Skills provide modular functionality that can be mixed and matched to create agents with exactly the capabilities needed.

---

## 1. Skill System Architecture

### Core Design Principles

**🎯 Skill System Features:**
- **Modular Design**: Skills organized by directory but used flexibly
- **Automatic Dependency Resolution**: Skills can specify dependencies - dependent skills are auto-included
- **Dynamic Runtime Registration**: Skills can conditionally register tools/hooks/handoffs during request processing
- **Scope-Based Access Control**: Skills have scopes (all/owner/admin) for fine-grained security
- **Simplified Lifecycle Hook System**: Skills use @hook decorator for automatic registration (on_connection, on_chunk, on_message, before/after_toolcall, before/after_handoff, finalize_connection)
- **Thread-Safe Operations**: All registration methods are thread-safe for concurrent requests

### Skill Categories

```
skills/                    # ONE SKILL = ONE FOLDER
├── short_term_memory/     # Short-term memory skill
│   ├── __init__.py
│   └── skill.py          # Message context and filtering  
├── long_term_memory/      # Long-term memory skill
│   ├── __init__.py
│   └── skill.py          # Persistent facts (LangGraph + PostgreSQL)
├── vector_memory/         # Vector memory skill
│   ├── __init__.py
│   └── skill.py          # Semantic search (Milvus)
├── litellm/              # LiteLLM provider skill (PRIORITY V2.0)
│   ├── __init__.py
│   └── skill.py          # LiteLLM integration
├── openai/               # OpenAI provider skill
│   ├── __init__.py
│   └── skill.py          # OpenAI integration
├── anthropic/            # Anthropic provider skill
│   ├── __init__.py
│   └── skill.py          # Anthropic integration
├── xai/                  # xAI provider skill (V2.1)
│   ├── __init__.py
│   └── skill.py          # xAI integration
├── guardrails/           # Content safety and filtering (V2.1)
│   ├── __init__.py
│   └── skill.py          # Content safety and filtering
├── mcp/                  # Model Context Protocol skill
│   ├── __init__.py
│   └── skill.py          # Model Context Protocol integration
├── nli/                  # Natural Language Interface skill
│   ├── __init__.py
│   └── skill.py          # Agent-to-agent communication
├── discovery/            # Agent discovery skill
│   ├── __init__.py
│   └── skill.py          # Agent discovery via Portal
├── auth/                 # Authentication skill (from V1)
│   ├── __init__.py
│   └── skill.py          # Authentication and authorization
├── payments/             # Payment processing skill (from V1)
│   ├── __init__.py
│   └── skill.py          # Payment processing and billing
├── messages/             # Message management skill
│   ├── __init__.py
│   └── skill.py          # Message management
├── storage/              # Portal storage skill
│   ├── __init__.py
│   └── skill.py          # Portal storage API integration
├── google/               # Google services skill (V2.1)
│   ├── __init__.py
│   └── skill.py          # Google services integration
├── database/             # Database operations skill (V2.1)
│   ├── __init__.py
│   └── skill.py          # Database operations
├── filesystem/           # File system skill (V2.1)
│   ├── __init__.py
│   └── skill.py          # File system operations
├── web/                  # Web scraping skill (V2.1)
│   ├── __init__.py
│   └── skill.py          # Web scraping
├── crewai/               # CrewAI integration skill (V2.1)
│   ├── __init__.py
│   └── skill.py          # CrewAI integration
├── n8n/                  # n8n workflow skill (V2.1)
│   ├── __init__.py
│   └── skill.py          # n8n workflow automation
├── zapier/               # Zapier automation skill (V2.1)
│   ├── __init__.py
│   └── skill.py          # Zapier automation
├── base.py              # Skill interface with lifecycle hooks
└── registry.py          # Skill discovery and loading
```

---

## 2. Skill Base Classes

### Core Skill Interface

```python
# robutler/agents/skills/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass

class Skill(ABC):
    """Base interface for agent skills with unified context access
    
    Skills have access to everything through a single Context object:
    - During initialization: Basic agent reference for registration
    - During request processing: Full Context via get_context()
    
    The Context contains BOTH request data AND agent capabilities:
    - Request: messages, user, streaming, usage, etc.  
    - Agent: skills, tools, hooks, capabilities, etc.
    """
    
    def __init__(self, config: Dict[str, Any] = None, scope: str = "all", dependencies: List[str] = None):
        self.config = config or {}
        self.scope = scope  # "all", "owner", "admin" - controls skill availability  
        self.dependencies = dependencies or []  # List of skill names this skill depends on
        self.skill_name = self.__class__.__name__  # For tracking registration source
        self.agent = None  # BaseAgent reference - set during initialization
    
    async def initialize(self, agent: 'BaseAgent') -> None:
        """
        Initialize skill with agent reference.
        Skills should register their tools, hooks, and handoffs here.
        
        Args:
            agent: The BaseAgent instance (for registration only)
        """
        self.agent = agent
        # Subclasses implement their registration logic here
    
    def get_tools(self) -> List[Callable]:
        """Return tools that this skill provides (from agent's central registry)"""
        if not self.agent:
            return []
        return [tool['function'] for tool in self.agent.get_all_tools() 
                if tool.get('source') == self.skill_name]
    
    def register_tool(self, tool_func: Callable, scope: str = None) -> None:
        """Register a tool with the agent (central registration)
        
        Can be called during initialization or at runtime from hooks/tools.
        """
        if not self.agent:
            raise RuntimeError("Cannot register tool: skill not initialized")
        
        # Use provided scope or fall back to skill's default scope
        effective_scope = scope if scope is not None else self.scope
        
        # Allow skill to override tool scope if provided
        if scope and hasattr(tool_func, '_tool_scope'):
            tool_func._tool_scope = scope
            
        # Register with agent's central registry
        self.agent.register_tool(tool_func, source=self.skill_name, scope=effective_scope)
    
    def register_hook(self, event: str, handler: Callable, priority: int = 50) -> None:
        """Register a hook for lifecycle events (central registration)
        
        Hooks receive and return the unified Context object containing everything.
        """
        if not self.agent:
            raise RuntimeError("Cannot register hook: skill not initialized")
            
        # Register with agent's central registry
        self.agent.register_hook(event, handler, priority, source=self.skill_name)
    
    def register_handoff(self, handoff_config: 'HandoffConfig') -> None:
        """Register a handoff configuration"""
        if not self.agent:
            raise RuntimeError("Cannot register handoff: skill not initialized")
            
        # Register with agent's central registry
        self.agent.register_handoff(handoff_config, source=self.skill_name)
    
    # Everything accessible via unified Context during request processing
    def get_context(self) -> Optional['Context']:
        """
        Get unified Context containing EVERYTHING:
        
        Request data:
        - context.messages, context.user, context.stream
        - context.track_usage(), context.get()/set()
        
        Agent capabilities:
        - context.agent_skills, context.agent_tools, context.agent_handoffs
        - context.agent (BaseAgent instance)
        """
        from robutler.server.context.context_vars import get_context
        return get_context()
```

### Dynamic Registration Examples

```python
class AdaptiveSkill(Skill):
    """Skill that adapts its capabilities based on runtime conditions"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        
    async def initialize(self, agent: 'BaseAgent') -> None:
        """Initialize adaptive skill - hooks auto-registered via @hook decorator"""
        self.agent = agent
    
    @hook("on_connection", priority=1)
    async def _analyze_request_and_adapt(self, context: 'Context') -> 'Context':
        """Analyze request and dynamically register capabilities (auto-registered)"""
    
        # Access request data from unified context
        auth_scope = context.get('auth_scope', 'all')  # Custom data
        request_type = 'streaming' if context.stream else 'chat'
        
        # Conditionally register tools based on user scope
        if auth_scope == 'admin':
            self.register_tool(self._admin_database_tool, scope="admin")
            self.register_tool(self._system_management_tool, scope="admin")
        elif auth_scope == 'owner':
            self.register_tool(self._billing_tool, scope="owner")
            self.register_tool(self._user_management_tool, scope="owner")
        
        # Register hooks based on request type
        if request_type == 'streaming':
            self.register_hook('on_chunk', self._stream_optimization, priority=20)
        elif request_type == 'batch':
            self.register_hook('finalize_connection', self._batch_processing, priority=20)
        
        # Access other skills via unified context  
        if "memory_vector" in context.agent_skills:
            # Register memory-enhanced tools if vector memory is available
            self.register_tool(self._memory_enhanced_search, scope="all")
        
        return context
    
    @tool(scope="admin") 
    async def _admin_database_tool(self, query: str) -> str:
        """Admin-only database access tool (registered at runtime)"""
        return f"Database result: {query}"
    
    @tool(scope="owner")
    async def _billing_tool(self, action: str) -> str:
        """Owner-only billing tool (registered at runtime)"""
        # Access unified context within tool
        context = self.get_context()
        if context:
            user_id = context.peer_user_id
            # Can also access agent capabilities if needed
            payment_skill = context.agent_skills.get("robutler.payments")
            return f"Billing action {action} for user {user_id}"
        return f"Billing action: {action}"
```

### StreamingAnalyticsSkill (demonstrating on_chunk and on_toolcall hooks)

```python
# robutler/agents/skills/core/streaming_analytics.py

class StreamingAnalyticsSkill(Skill):
    """
    Example skill demonstrating on_chunk and on_toolcall lifecycle hooks
    - Real-time content analysis during streaming
    - Tool execution monitoring and modification
    """
    
    async def initialize(self, agent_context) -> None:
        """Initialize streaming analytics with real-time processing hooks"""
        
        # Register chunk-level hooks for real-time processing
        self.register_hook('before_chunk', self._analyze_chunk_sentiment, priority=10)
        self.register_hook('before_chunk', self._detect_content_issues, priority=15)
        self.register_hook('after_chunk', self._update_streaming_metrics, priority=90)
        
        # Register tool-level hooks for tool execution monitoring  
        self.register_hook('before_toolcall', self._validate_tool_security, priority=5)
        self.register_hook('before_toolcall', self._log_tool_usage, priority=10)
        self.register_hook('before_toolcall', self._modify_tool_params, priority=15)
        self.register_hook('after_toolcall', self._process_tool_results, priority=50)
    
    async def _analyze_chunk_sentiment(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment of each streaming chunk in real-time"""
        
        content = context.get("content", "")
        if content:
            # Real-time sentiment analysis
            sentiment = await self._quick_sentiment_analysis(content)
            
            # Add sentiment to context for other hooks
            context["chunk_sentiment"] = sentiment
            
            # If negative sentiment detected, potentially modify chunk
            if sentiment.get("score", 0) < -0.8:
                print(f"Warning: Highly negative content detected in chunk")
                # Could modify the chunk here if needed
                # context["chunk"]["choices"][0]["delta"]["content"] = filtered_content
        
        return context
    
    async def _detect_content_issues(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Detect potential content issues in streaming chunks"""
        
        content = context.get("content", "")
        full_content = context.get("full_content_so_far", "")
        
        # Real-time content filtering
        issues = await self._scan_for_issues(content, full_content)
        
        if issues:
            print(f"Content issues detected: {issues}")
            context["content_issues"] = issues
            
            # Could modify or block the chunk if severe issues found
            if any(issue.get("severity") == "high" for issue in issues):
                # Replace problematic content
                sanitized_content = await self._sanitize_content(content)
                context["chunk"]["choices"][0]["delta"]["content"] = sanitized_content
        
        return context
    
    async def _update_streaming_metrics(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update real-time streaming metrics"""
        
        # Track streaming performance metrics
        completion_id = context.get("completion_id")
        content_length = len(context.get("content", ""))
        
        await self._record_streaming_metric({
            "completion_id": completion_id,
            "chunk_length": content_length,
            "timestamp": time.time(),
            "sentiment": context.get("chunk_sentiment"),
            "issues": context.get("content_issues", [])
        })
        
        return context
    
    async def _validate_tool_security(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tool call security before execution using contextvars"""
        from robutler.server.context.context_vars import get_request_id, get_user_id, get_agent_name
        
        # Access request context via contextvars (thread-safe)
        request_id = get_request_id()
        user_id = get_user_id()
        agent_name = get_agent_name()
        
        tool_call = context.get("tool_call", {})
        function_name = tool_call.get("function", {}).get("name")
        function_args = tool_call.get("function", {}).get("arguments")
        
        # Security validation with context
        security_check = await self._check_tool_security(
            function_name, function_args, user_id=user_id, agent_name=agent_name
        )
        
        if not security_check.get("allowed", True):
            print(f"Tool call blocked for {user_id} on {agent_name}: {security_check.get('reason')}")
            
            # Log security event with request context
            await self._log_security_event({
                "request_id": request_id,
                "user_id": user_id,
                "agent_name": agent_name,
                "blocked_tool": function_name,
                "reason": security_check.get("reason")
            })
            
            # Modify tool call to safe alternative or block it
            if security_check.get("suggested_alternative"):
                context["tool_call"]["function"]["name"] = security_check["suggested_alternative"]
            else:
                # Replace with safe no-op tool
                context["tool_call"]["function"]["name"] = "safe_info_tool"
                context["tool_call"]["function"]["arguments"] = '{"message": "Tool call blocked for security"}'
        
        return context
    
    async def _log_tool_usage(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Log detailed tool usage analytics"""
        
        tool_call = context.get("tool_call", {})
        agent = context.get("agent")
        
        # Log comprehensive tool usage data
        usage_log = {
            "tool_name": tool_call.get("function", {}).get("name"),
            "agent_name": agent.name if agent else None,
            "timestamp": time.time(),
            "streaming": context.get("streaming", False),
            "completion_id": context.get("completion_id"),
            "args_provided": list(json.loads(tool_call.get("function", {}).get("arguments", "{}")).keys())
        }
        
        await self._log_tool_analytics(usage_log)
        return context
    
    async def _modify_tool_params(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Intelligently modify tool parameters based on context"""
        
        tool_call = context.get("tool_call", {})
        function_name = tool_call.get("function", {}).get("name")
        
        # Smart parameter enhancement based on context
        if function_name == "search_web":
            args = json.loads(tool_call.get("function", {}).get("arguments", "{}"))
            
            # Enhance search query with context if available
            if "query" in args and len(args["query"]) < 20:
                enhanced_query = await self._enhance_search_query(args["query"], context)
                args["query"] = enhanced_query
                
                # Update tool call with enhanced parameters
                context["tool_call"]["function"]["arguments"] = json.dumps(args)
                print(f"Enhanced search query: {enhanced_query}")
        
        return context
    
    # Helper methods (implementation would be in actual code)
    async def _quick_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Fast sentiment analysis for real-time processing"""
        return {"score": 0.1, "label": "neutral"}  # Placeholder
    
    async def _scan_for_issues(self, content: str, full_content: str) -> List[Dict[str, Any]]:
        """Scan content for potential issues"""
        return []  # Placeholder
    
    async def _sanitize_content(self, content: str) -> str:
        """Sanitize problematic content"""
        return content  # Placeholder
    
    async def _record_streaming_metric(self, metric: Dict[str, Any]) -> None:
        """Record streaming performance metric"""
        pass  # Placeholder
    
    async def _check_tool_security(self, function_name: str, arguments: str) -> Dict[str, Any]:
        """Check tool call security"""
        return {"allowed": True}  # Placeholder
    
    async def _log_tool_analytics(self, usage_log: Dict[str, Any]) -> None:
        """Log tool usage analytics"""
        pass  # Placeholder
    
    async def _enhance_search_query(self, query: str, context: Dict[str, Any]) -> str:
        """Enhance search query with context"""
        return query  # Placeholder
    
    async def _check_tool_security(self, function_name: str, arguments: str, 
                                  user_id: str = None, agent_name: str = None) -> Dict[str, Any]:
        """Enhanced security check with context"""
        return {"allowed": True}  # Placeholder
    
    async def _log_security_event(self, event: Dict[str, Any]) -> None:
        """Log security events with full context"""
        pass  # Placeholder


### ContextAwareSkill (showing contextvars best practices)

```python
# robutler/agents/skills/core/context_aware.py
from contextvars import copy_context
from robutler.server.context.context_vars import (
    REQUEST_ID, USER_ID, AGENT_NAME, get_request_context
)

class UnifiedContextSkill(Skill):
    """Example skill showing unified context best practices"""
    
    async def initialize(self, agent: 'BaseAgent') -> None:
        """Initialize with context-aware hooks"""
        self.agent = agent
        self.register_hook('before_request', self._context_setup, priority=1)
        self.register_hook('before_chunk', self._context_aware_processing, priority=50)
        self.register_hook('after_response', self._context_cleanup, priority=99)
    
    async def _context_setup(self, context: 'Context') -> 'Context':
        """Set up additional context data"""
        
        # Access everything from unified context
        request_id = context.request_id
        agent_name = context.agent_name_resolved
        user_id = context.peer_user_id
        
        # Store additional data in context
        context.set("skill_initialized", True)
        context.set("processing_start", datetime.utcnow())
        
        print(f"Request {request_id} starting on agent {agent_name} for user {user_id}")
        return context
    
    async def _context_aware_processing(self, context: 'Context') -> 'Context':
        """Process chunks with full context awareness"""
        
        # Everything available in unified context
            content = context.get("content", "")
        full_content = context.get("full_content_so_far", "")
        is_streaming = context.stream
            
            # Context-aware processing based on user, agent, stream state
        if is_streaming and len(content) > 100:
            print(f"Long chunk detected in streaming request {context.request_id}")
            
            # Access agent skills if needed
            memory_skill = context.agent_skills.get("memory_short")
            if memory_skill:
                # Could cache large chunks to memory
                pass
        
        return context
    
    async def _context_cleanup(self, context: 'Context') -> 'Context':
        """Clean up request context"""
        
        processing_start = context.get("processing_start")
        if processing_start:
            duration = datetime.utcnow() - processing_start
            context.track_usage(5, f"Context processing took {duration.total_seconds()}s")
        
        print(f"Request {context.request_id} completed")
        return context
    
    @tool
    async def unified_context_tool(self, query: str, context: Context = None) -> str:
        """Tool that uses unified context (with automatic injection)"""
        
        # Context automatically injected - much cleaner!
        if context:
            # Request data
            request_id = context.request_id
            user_id = context.peer_user_id or "anonymous"
            agent_name = context.agent_name_resolved
            
            # Agent capabilities  
            available_skills = list(context.agent_skills.keys())
            tool_count = len(context.agent_tools)
            
            # Track usage
            context.track_usage(10, f"Tool execution for user {user_id}")
            
            return (f"Processed '{query}' for user {user_id} on agent {agent_name}\n"
                   f"Available skills: {available_skills}\n"
                   f"Total tools: {tool_count}")
        
        return f"Processed '{query}' (no context available)"
    
    async def _run_background_task(self):
        """Example of passing context to background tasks"""
        
        # Get current unified context
        context = self.get_context()
        if context:
            # Pass specific data to background task (don't pass entire context)
            request_data = {
                "request_id": context.request_id,
                "user_id": context.peer_user_id,
                "agent_name": context.agent_name_resolved
            }
        
        def background_work():
                print(f"Background work for request {request_data['request_id']}")
            
            # Run background task
            await asyncio.get_event_loop().run_in_executor(None, background_work)


### FlexibleHandoffSkill (demonstrating all handoff types)

```python  
# robutler/agents/skills/core/flexible_handoffs.py
from robutler.agents.core.base_agent import (
    LocalAgentHandoff, RemoteAgentHandoff, CrewAIHandoff, N8nWorkflowHandoff,
    LLMHandoff, ProcessingPipelineHandoff, handoff
)

class FlexibleHandoffSkill(Skill):
    """
    Comprehensive skill demonstrating all types of flexible handoffs:
    - Agent handoffs (to specialized agents)
    - LLM handoffs (to different models)  
    - Pipeline handoffs (to specialized processing)
    - Skill handoffs (to domain-specific skills)
    """
    
    async def initialize(self, agent_context) -> None:
        """Initialize with comprehensive handoff examples"""
        
        # Register conditional handoffs based on request analysis
        self.register_hook('before_request', self._analyze_and_register_handoffs, priority=5)
    
    async def _analyze_and_register_handoffs(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze request and register appropriate handoffs"""
        
        messages = context.get("messages", [])
        request_content = " ".join([msg.get("content", "") for msg in messages if msg.get("content")])
        
        # 🤖 Local Agent handoffs - route to specialized local agents
        if self._needs_coding_help(request_content):
            self.register_handoff(LocalAgentHandoff(
                "coding-specialist-agent",
                tool_name_override="escalate_to_coding_expert",
                tool_description_override="Transfer complex coding tasks to specialized development agent",
                on_handoff=self._log_coding_handoff
            ))
        
        if self._needs_research(request_content):
            self.register_handoff(LocalAgentHandoff(
                "research-agent",
                tool_name_override="transfer_to_research_specialist",
                tool_description_override="Transfer research tasks to academic research specialist",
                input_filter=self._filter_research_context
            ))
        
        # 🌐 Remote Agent handoffs - via NLI skill
        nli_skill = self.agent_context.get_skill("robutler.nli")
        if nli_skill and self._needs_external_consultation(request_content):
            self.register_handoff(RemoteAgentHandoff(
                "https://partner-api.example.com/expert-agent",
                nli_skill,
                tool_name_override="consult_external_expert",
                tool_description_override="Consult external domain expert for specialized knowledge",
                on_handoff=self._log_external_handoff
            ))
        
        # 🎭 CrewAI handoffs - multi-agent orchestration
        crewai_skill = self.agent_context.get_skill("crewai")
        if crewai_skill and self._needs_team_collaboration(request_content):
            self.register_handoff(CrewAIHandoff(
                "data-analysis-crew",
                crewai_skill,
                tool_name_override="activate_analysis_crew",
                tool_description_override="Deploy specialized data analysis crew for complex analytical tasks"
            ))
        
        # 🔧 n8n Workflow handoffs - automated processes
        n8n_skill = self.agent_context.get_skill("n8n")
        if n8n_skill and self._needs_workflow_automation(request_content):
            self.register_handoff(N8nWorkflowHandoff(
                "customer-onboarding-workflow",
                n8n_skill,
                tool_name_override="trigger_onboarding_workflow",
                tool_description_override="Execute automated customer onboarding workflow"
            ))
        
        # 🧠 LLM handoffs - switch models for different tasks
        if self._needs_creative_writing(request_content):
            self.register_handoff(LLMHandoff(
                "claude-3-5-sonnet-20241022",
                provider="anthropic",
                tool_name_override="switch_to_creative_model",
                tool_description_override="Switch to Claude for creative writing and storytelling tasks",
                on_handoff=self._log_model_switch
            ))
        
        if self._needs_math_reasoning(request_content):
            self.register_handoff(LLMHandoff(
                "gpt-4o",
                provider="openai",
                tool_name_override="switch_to_reasoning_model",
                tool_description_override="Switch to GPT-4o for advanced mathematical reasoning and analysis"
            ))
        
        if self._needs_fast_response(request_content):
            self.register_handoff(LLMHandoff(
                "gpt-4o-mini",
                provider="openai",
                tool_name_override="switch_to_fast_model",
                tool_description_override="Switch to GPT-4o-mini for quick responses to simple questions"
            ))
        
        # 🔧 Pipeline handoffs - specialized processing
        if self._contains_images(context):
            self.register_handoff(ProcessingPipelineHandoff(
                "vision-processing-pipeline",
                {
                    "models": ["gpt-4-vision-preview", "claude-3-5-sonnet-20241022"],
                    "capabilities": ["ocr", "image_analysis", "diagram_interpretation"]
                },
                tool_name_override="process_with_vision_pipeline",
                tool_description_override="Process images and visual content using specialized vision pipeline"
            ))
        
        if self._needs_data_analysis(request_content):
            self.register_handoff(ProcessingPipelineHandoff(
                "data-analysis-pipeline",
                {"capabilities": ["statistics", "visualization", "ml_insights"]},
                tool_name_override="analyze_with_data_pipeline",
                tool_description_override="Process complex data using specialized analytics pipeline"
            ))
        
        return context
    
    # Agent handoff conditions
    async def _check_coding_complexity(self, context: Dict[str, Any]) -> bool:
        """Check if coding task is too complex for current agent"""
        content = " ".join([msg.get("content", "") for msg in context.get("messages", [])])
        
        complexity_indicators = [
            "system architecture", "microservices", "distributed systems",
            "performance optimization", "security audit", "complex algorithm"
        ]
        
        return any(indicator in content.lower() for indicator in complexity_indicators)
    
    async def _check_research_depth(self, context: Dict[str, Any]) -> bool:
        """Check if research task needs specialized agent"""
        content = " ".join([msg.get("content", "") for msg in context.get("messages", [])])
        
        research_indicators = [
            "academic paper", "literature review", "peer review",
            "systematic analysis", "meta-analysis", "citation needed"
        ]
        
        return any(indicator in content.lower() for indicator in research_indicators)
    
    # LLM handoff conditions  
    async def _check_creative_complexity(self, context: Dict[str, Any]) -> bool:
        """Check if task needs creative LLM"""
        content = " ".join([msg.get("content", "") for msg in context.get("messages", [])])
        
        creative_indicators = [
            "creative writing", "story", "poem", "novel", "screenplay",
            "marketing copy", "brand voice", "creative brainstorm"
        ]
        
        return any(indicator in content.lower() for indicator in creative_indicators)
    
    async def _check_math_complexity(self, context: Dict[str, Any]) -> bool:
        """Check if task needs mathematical reasoning LLM"""
        content = " ".join([msg.get("content", "") for msg in context.get("messages", [])])
        
        math_indicators = [
            "mathematical proof", "calculus", "statistics", "linear algebra", 
            "differential equations", "complex analysis", "algorithm complexity"
        ]
        
        return any(indicator in content.lower() for indicator in math_indicators)
    
    async def _check_speed_requirements(self, context: Dict[str, Any]) -> bool:
        """Check if fast response is needed"""
        # Check for urgency indicators
        content = " ".join([msg.get("content", "") for msg in context.get("messages", [])])
        
        speed_indicators = [
            "quickly", "urgent", "asap", "fast", "immediately", 
            "brief", "short answer", "quick question"
        ]
        
        return any(indicator in content.lower() for indicator in speed_indicators)
    
    # Pipeline handoff conditions
    async def _check_image_processing_needs(self, context: Dict[str, Any]) -> bool:
        """Check if images need specialized processing"""
        messages = context.get("messages", [])
        
        # Check for image content or image-related requests
        has_images = any(msg.get("type") == "image" or "image" in str(msg) for msg in messages)
        content = " ".join([msg.get("content", "") for msg in messages if msg.get("content")])
        
        image_processing_needs = [
            "analyze image", "extract text", "describe image", "read document",
            "ocr", "diagram analysis", "chart interpretation"
        ]
        
        return has_images or any(need in content.lower() for need in image_processing_needs)
    
    async def _check_data_complexity(self, context: Dict[str, Any]) -> bool:
        """Check if data analysis is needed"""
        content = " ".join([msg.get("content", "") for msg in context.get("messages", [])])
        
        data_indicators = [
            "data analysis", "statistical analysis", "data visualization", 
            "pandas", "numpy", "machine learning", "regression", "correlation"
        ]
        
        return any(indicator in content.lower() for indicator in data_indicators)
    
    # Skill handoff conditions
    async def _check_memory_requirements(self, context: Dict[str, Any]) -> bool:
        """Check if advanced memory capabilities are needed"""
        content = " ".join([msg.get("content", "") for msg in context.get("messages", [])])
        
        memory_indicators = [
            "remember from previous", "recall conversation", "search history",
            "past interactions", "long term memory", "context retrieval"
        ]
        
        return any(indicator in content.lower() for indicator in memory_indicators)
    
    # Content analysis helpers
    def _needs_coding_help(self, content: str) -> bool:
        coding_keywords = ["code", "programming", "function", "class", "algorithm", "debug"]
        return any(keyword in content.lower() for keyword in coding_keywords)
    
    def _needs_research(self, content: str) -> bool:
        research_keywords = ["research", "study", "analysis", "investigate", "academic"]
        return any(keyword in content.lower() for keyword in research_keywords)
    
    def _needs_creative_writing(self, content: str) -> bool:
        creative_keywords = ["write", "story", "creative", "poem", "narrative"]
        return any(keyword in content.lower() for keyword in creative_keywords)
    
    def _needs_math_reasoning(self, content: str) -> bool:
        math_keywords = ["math", "calculate", "equation", "formula", "proof", "theorem"]
        return any(keyword in content.lower() for keyword in math_keywords)
    
    def _needs_fast_response(self, content: str) -> bool:
        speed_keywords = ["quick", "fast", "brief", "urgent", "immediately"]
        return any(keyword in content.lower() for keyword in speed_keywords)
    
    def _contains_images(self, context: Dict[str, Any]) -> bool:
        messages = context.get("messages", [])
        return any("image" in str(msg) or msg.get("type") == "image" for msg in messages)
    
    def _needs_data_analysis(self, content: str) -> bool:
        data_keywords = ["data", "analytics", "statistics", "visualization", "analysis"]
        return any(keyword in content.lower() for keyword in data_keywords)
    
    def _needs_advanced_memory(self, content: str) -> bool:
        memory_keywords = ["remember", "recall", "history", "previous", "context"]
        return any(keyword in content.lower() for keyword in memory_keywords)
    
    def _needs_external_consultation(self, content: str) -> bool:
        consultation_keywords = ["expert opinion", "external expert", "domain specialist", "consultant"]
        return any(keyword in content.lower() for keyword in consultation_keywords)
    
    def _needs_team_collaboration(self, content: str) -> bool:
        team_keywords = ["team effort", "collaboration", "multi-agent", "crew", "coordinated analysis"]
        return any(keyword in content.lower() for keyword in team_keywords)
    
    def _needs_workflow_automation(self, content: str) -> bool:
        workflow_keywords = ["automate", "workflow", "process automation", "trigger workflow"]
        return any(keyword in content.lower() for keyword in workflow_keywords)
    
    # Callback methods for handoff events
    async def _log_coding_handoff(self, input_data: Dict, conversation: List[Dict]):
        """Log coding task handoffs"""
        print(f"Coding handoff: {input_data.get('context')} - {len(conversation)} messages")
    
    async def _log_external_handoff(self, input_data: Dict, conversation: List[Dict]):
        """Log external expert consultations"""
        print(f"External consultation: {input_data.get('context')}")
    
    async def _log_model_switch(self, input_data: Dict, conversation: List[Dict]):
        """Log model switches"""
        print(f"Model switch: {input_data.get('reason')}")
    
    async def _filter_research_context(self, conversation: List[Dict]) -> List[Dict]:
        """Filter conversation for research handoffs"""
        # Remove personal information, keep research-relevant content
        filtered = []
        for msg in conversation:
            if "research" in msg.get("content", "").lower() or msg.get("role") == "system":
                filtered.append(msg)
        return filtered[-10:]  # Keep last 10 relevant messages


# Example usage of OpenAI SDK-compatible handoff system:
async def example_handoff_usage():
    """Example showing the new OpenAI SDK-compatible handoff system"""
    
    # In a skill's initialize method:
    class ExampleSkill(Skill):
        async def initialize(self, agent_context):
            self.agent_context = agent_context
            
            # 🤖 Local agent handoff (OpenAI SDK compatible)
            self.register_handoff(LocalAgentHandoff(
                "specialist-agent",
                tool_name_override="escalate_to_specialist", 
                tool_description_override="Transfer complex tasks to specialist agent",
                on_handoff=self._log_handoff
            ))
            
            # 🌐 Remote agent handoff via NLI skill
            nli_skill = self.agent_context.get_skill("robutler.nli")
            if nli_skill:
                self.register_handoff(RemoteAgentHandoff(
                    "https://partner.example.com/api/expert-agent",
                    nli_skill,
                    tool_name_override="consult_external_expert",
                    tool_description_override="Consult external domain expert for specialized guidance"
                ))
            
            # 🎭 CrewAI multi-agent handoff  
            crewai_skill = self.agent_context.get_skill("crewai")
            if crewai_skill:
                self.register_handoff(CrewAIHandoff(
                    "research-analysis-crew",
                    crewai_skill,
                    tool_name_override="deploy_research_crew",
                    tool_description_override="Deploy specialized research crew for comprehensive analysis"
                ))
            
            # 🔧 n8n workflow handoff
            n8n_skill = self.agent_context.get_skill("n8n")
            if n8n_skill:
                self.register_handoff(N8nWorkflowHandoff(
                    "data-processing-workflow",
                    n8n_skill,
                    tool_name_override="trigger_data_workflow",
                    tool_description_override="Execute automated data processing workflow"
                ))
            
            # 🧠 LLM handoff with customization
            self.register_handoff(LLMHandoff(
                "claude-3-5-sonnet-20241022",
                provider="anthropic",
                tool_name_override="switch_to_creative_model",
                tool_description_override="Switch to Claude for creative and storytelling tasks",
                on_handoff=self._log_model_switch
            ))
            
            # 🔧 Processing pipeline handoff
            self.register_handoff(ProcessingPipelineHandoff(
                "multimodal-analysis-pipeline",
                {
                    "stages": ["vision_analysis", "text_extraction", "context_integration"],
                    "models": ["gpt-4-vision-preview", "claude-3-5-sonnet-20241022"],
                    "capabilities": ["image_analysis", "document_processing", "data_extraction"]
                },
                tool_name_override="process_multimodal_content",
                tool_description_override="Process images, documents, and mixed content using specialized pipeline"
            ))
            
            # 🎯 Using the helper function (OpenAI SDK compatible)
            self.register_handoff(handoff(
                "billing-specialist",
                tool_name_override="escalate_to_billing_expert",
                tool_description_override="Escalate billing issues to human billing expert",
                on_handoff=self._log_escalation,
                input_filter=self._sanitize_sensitive_data
            ))
        
        async def _log_handoff(self, input_data: Dict, conversation: List[Dict]):
            """Log handoff events"""
            print(f"Handoff executed: {input_data.get('context')}")
        
        async def _log_model_switch(self, input_data: Dict, conversation: List[Dict]):
            """Log model switches"""
            print(f"Switched models: {input_data.get('reason')}")
        
        async def _sanitize_sensitive_data(self, conversation: List[Dict]) -> List[Dict]:
            """Filter sensitive data from conversation history"""
            # Remove sensitive information before handoff
            return [msg for msg in conversation if not self._contains_sensitive_info(msg)]
```

---

## 3. Core Skills

### Memory Skills (3-Tier System)

#### Short-Term Memory Skill

```python
# robutler/agents/skills/core/memory/short_term.py
from typing import Dict, Any, List
from ...base import Skill
from ....tools.decorators import tool

class ShortTermMemorySkill(Skill):
    """Short-term memory skill for message filtering and recent context"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config, scope="all")  # Available to all users
        self.message_cache = []
        self.max_messages = config.get('max_messages', 100) if config else 100
    
    async def initialize(self, agent: 'BaseAgent') -> None:
        """Initialize short-term memory"""
        self.agent = agent
        # Register hooks for message processing
        self.register_hook('before_request', self._filter_request, priority=10)
        self.register_hook('after_response', self._cache_response, priority=90)
        
        # Register memory tools
        self.register_tool(self.add_message)
        self.register_tool(self.get_recent_messages)
        self.register_tool(self.clear_cache)
    
    async def _filter_request(self, context: 'Context') -> 'Context':
        """Filter and enhance incoming requests"""
        # Add recent context to request
            recent_context = self.get_recent_context()
        context.set('recent_context', recent_context)
        
        # Enhanced filtering based on user
        if context.peer_user_id:
            user_specific_context = self.get_user_context(context.peer_user_id)
            context.set('user_context', user_specific_context)
        
        return context
    
    async def _cache_response(self, context: 'Context') -> 'Context':
        """Cache response in short-term memory"""
        if len(self.message_cache) >= self.max_messages:
            self.message_cache.pop(0)  # Remove oldest
            
        # Cache the response with metadata
        response_data = {
            "content": context.get("response", {}).get("content", ""),
            "user_id": context.peer_user_id,
            "timestamp": context.start_time,
            "request_id": context.request_id
        }
        self.message_cache.append(response_data)
        return context
    
    @tool(scope="all")
    async def add_message(self, message: Dict[str, Any]) -> str:
        """Add message to short-term memory"""
        self.message_cache.append(message)
        if len(self.message_cache) > self.max_messages:
            self.message_cache.pop(0)
        return f"Added message to cache. Cache size: {len(self.message_cache)}"
    
    @tool(scope="all")
    async def get_recent_messages(self, limit: int = 20) -> List[Dict]:
        """Get recent messages from cache"""
        return self.message_cache[-limit:]
    
    def get_recent_context(self) -> List[Dict]:
        """Get recent messages for context"""
        return self.message_cache[-20:]  # Last 20 messages
    
    @tool(scope="owner")
    async def clear_cache(self) -> str:
        """Clear the message cache"""
        self.message_cache.clear()
        return "Message cache cleared"
```

#### Long-Term Memory Skill

```python
# robutler/agents/skills/core/memory/long_term.py
from typing import Dict, Any, List
from ...base import Skill
from ....tools.decorators import tool

class LongTermMemorySkill(Skill):
    """Long-term memory skill using LangGraph + PostgreSQL"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config, scope="all")  # Available to all users
        self.db_connection = None
        self.langgraph_store = None
        self.connection_string = config.get('connection_string') if config else None
    
    async def initialize(self, agent_context) -> None:
        """Initialize long-term memory storage"""
        self.agent_context = agent_context
        # Initialize PostgreSQL connection and LangGraph checkpoints
        await self._init_connections()
        
        # Register memory tools
        self.register_tool(self.store_fact)
        self.register_tool(self.retrieve_facts)
        self.register_tool(self.create_checkpoint)
        self.register_tool(self.recall)
    
    async def _init_connections(self):
        """Initialize database and LangGraph connections"""
        # Implementation would initialize PostgreSQL and LangGraph
        pass
    
    @tool(scope="all")
    async def store_fact(self, key: str, value: Any, metadata: Dict = None) -> str:
        """Store persistent facts"""
        # Store in PostgreSQL with LangGraph integration
        return f"Stored fact: {key} = {value}"
    
    @tool(scope="all")
    async def retrieve_facts(self, query: str) -> List[Dict]:
        """Retrieve facts by query"""
        # Query PostgreSQL with semantic search
        return [{"key": f"fact_{i}", "value": f"value for {query}"} for i in range(3)]
    
    @tool(scope="all")
    async def create_checkpoint(self, conversation_id: str) -> str:
        """Create LangGraph checkpoint for conversation state"""
        # Create checkpoint in LangGraph store
        return f"Created checkpoint for conversation: {conversation_id}"
    
    async def recall(self, query: str) -> List[Dict[str, Any]]:
        """Recall facts from long-term memory"""
        # Implementation would query PostgreSQL
        return await self.retrieve_facts(query)
```

#### Vector Memory Skill

```python
# robutler/agents/skills/core/memory/vector.py
from typing import Dict, Any, List
from ...base import Skill
from ....tools.decorators import tool

class VectorMemorySkill(Skill):
    """Vector memory skill using Milvus for semantic search"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.milvus_client = None
        self.collection_name = config.get('collection_name', 'agent_vectors') if config else 'agent_vectors'
        self.milvus_host = config.get('milvus_host', 'localhost') if config else 'localhost'
        self.milvus_port = config.get('milvus_port', 19530) if config else 19530
    
    async def initialize(self, agent_context) -> None:
        """Initialize Milvus vector database"""
        self.agent_context = agent_context
        # Initialize Milvus connection and collections
        await self._init_milvus()
        
        # Register vector tools
        self.register_tool(self.add_content)
        self.register_tool(self.search)
        self.register_tool(self.embed_and_store)
    
    async def _init_milvus(self):
        """Initialize Milvus connection"""
        # Implementation would connect to Milvus
        pass
    
    @tool(scope="all")
    async def add_content(self, text: str, metadata: Dict = None) -> str:
        """Add content to vector memory"""
        # Generate embeddings and store
        return await self.embed_and_store(text, metadata)
    
    @tool(scope="all")
    async def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Semantic similarity search"""
        # Generate query embedding and search Milvus
        return await self.similarity_search(query, top_k)
    
    async def embed_and_store(self, text: str, metadata: Dict = None) -> str:
        """Generate embeddings and store in Milvus"""
        # Use agent's LLM for embeddings, store in Milvus
        llm_skill = self.agent_context.get_llm_skill()
        embeddings = await llm_skill.embed(text)
        # Store in Milvus with metadata
        return f"Stored vector embedding for: {text[:50]}..."
    
    async def similarity_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Semantic similarity search"""
        # Generate query embedding and search Milvus
        llm_skill = self.agent_context.get_llm_skill()
        query_embedding = await llm_skill.embed(query)
        # Return similar vectors with metadata
        return [{"content": f"Similar content {i}", "score": 0.9 - i*0.1} for i in range(top_k)]
```

### LLM Provider Skills

> **⚠️ Critical:** LLM skills replace the old `model` parameter in BaseAgent. Every agent needs at least one LLM skill to function.

#### LiteLLM Skill

```python
# robutler/agents/skills/core/llm/litellm.py
from typing import Dict, Any, List
from ...base import Skill
from ....tools.decorators import tool

class LiteLLMSkill(Skill):
    """LiteLLM integration skill for cross-provider LLM routing"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.api_key = config.get('api_key') if config else None
        self.base_url = config.get('base_url', 'http://localhost:2225') if config else 'http://localhost:2225'
        
    async def initialize(self, agent_context) -> None:
        """Initialize LiteLLM skill"""
        self.agent_context = agent_context
        self.register_tool(self.query_llm)
        self.register_tool(self.embed)
    
    @tool(scope="all")
    async def query_llm(self, model: str, messages: List[Dict], **kwargs) -> str:
        """Query any LLM via LiteLLM"""
        # Implementation would use LiteLLM to route to different providers
        return f"LiteLLM response from {model}"
    
    @tool(scope="all") 
    async def embed(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """Generate embeddings via LiteLLM"""
        # Implementation would generate embeddings
        return [0.1, 0.2, 0.3]  # Mock embedding vector
    
    async def chat_completion(self, messages: List[Dict], tools: List = None, stream: bool = False):
        """Core chat completion functionality for BaseAgent"""
        # Implementation for agent's LLM calls
        return {"choices": [{"message": {"content": "LiteLLM response"}}]}
    
    async def chat_completion_stream(self, messages: List[Dict], tools: List = None):
        """Streaming chat completion for BaseAgent"""
        # Implementation for streaming
        for i in range(3):
            yield {"choices": [{"delta": {"content": f"Stream chunk {i}"}}]}
```

#### OpenAI Skill

```python
# robutler/agents/skills/core/llm/openai.py
from typing import Dict, Any, List
from ...base import Skill
from ....tools.decorators import tool

class OpenAISkill(Skill):
    """OpenAI integration skill"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.api_key = config.get('api_key') if config else None
        
    async def initialize(self, agent_context) -> None:
        """Initialize OpenAI skill"""
        self.agent_context = agent_context
        self.register_tool(self.query_openai)
        self.register_tool(self.embed)
        
    @tool(scope="all") 
    async def query_openai(self, model: str, messages: List[Dict], **kwargs) -> str:
        """Query OpenAI models directly"""
        return f"OpenAI response from {model}"
    
    @tool(scope="all")
    async def embed(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """Generate OpenAI embeddings"""
        return [0.1, 0.2, 0.3]  # Mock embedding
    
    async def chat_completion(self, messages: List[Dict], tools: List = None, stream: bool = False):
        """Core chat completion functionality for BaseAgent"""
        return {"choices": [{"message": {"content": "OpenAI response"}}]}
    
    async def chat_completion_stream(self, messages: List[Dict], tools: List = None):
        """Streaming chat completion for BaseAgent"""
        for i in range(3):
            yield {"choices": [{"delta": {"content": f"OpenAI chunk {i}"}}]}
```

### Guardrails Skill

```python
# robutler/agents/skills/core/guardrails.py
from typing import Dict, Any, List
from ..base import Skill
from ...tools.decorators import tool

class GuardrailsSkill(Skill):
    """Content safety and guardrails skill"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.safety_level = config.get('safety_level', 'standard') if config else 'standard'
        self.blocked_patterns = config.get('blocked_patterns', []) if config else []
    
    async def initialize(self, agent: 'BaseAgent') -> None:
        """Initialize guardrails"""
        self.agent = agent
        self.register_hook('before_request', self._check_input_safety, priority=3)
        self.register_hook('before_response', self._check_output_safety, priority=5)
        self.register_hook('before_handoff', self._filter_handoff, priority=10)  # NEW: Handoff filtering
        
        # Register safety tools
        self.register_tool(self.analyze_content_safety)
        self.register_tool(self.add_blocked_pattern)
    
    async def _check_input_safety(self, context: 'Context') -> 'Context':
        """Check input for safety violations"""
        for message in context.messages:
                if message.get('role') == 'user':
                    safety_result = await self._analyze_content_safety(message['content'])
                    if not safety_result['safe']:
                    context.set('safety_violation', safety_result)
                    context.set('blocked', True)
                    # Could modify messages in place to filter content
                    break
        return context
    
    async def _check_output_safety(self, context: 'Context') -> 'Context':
        """Check output for safety violations"""
        response = context.get('response', {})
        if 'content' in response:
            safety_result = await self._analyze_content_safety(response['content'])
            if not safety_result['safe']:
                response['content'] = "[Content blocked by safety filters]"
                context.set('response', response)
                context.set('safety_filtered', True)
        return context
    
    async def _filter_handoff(self, context: 'Context') -> 'Context':
        """Filter conversation and validate handoff before execution"""
        
        # Get handoff-specific data from context
        handoff_type = context.get("handoff_type")
        target = context.get("target")
        conversation = context.messages  # Use context messages
        
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
        
        # Store filtered conversation in context for handoff execution
        context.set("filtered_conversation", filtered_conversation)
        
        # Log handoff for audit
        await self._log_handoff(context)
        
        return context
    
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
    
    async def _log_handoff(self, context: 'Context') -> None:
        """Log handoff for security audit"""
        handoff_type = context.get("handoff_type")
        target = context.get("target")
        print(f"🔒 Handoff filtered: {handoff_type} -> {target}")
        # In production: send to audit log
        pass
    
    @tool(scope="all")
    async def analyze_content_safety(self, content: str) -> Dict:
        """Analyze content for safety"""
        return await self._analyze_content_safety(content)
    
    async def _analyze_content_safety(self, content: str) -> Dict:
        """Analyze content for safety"""
        # Use agent's LLM or external safety service
        for pattern in self.blocked_patterns:
            if pattern.lower() in content.lower():
                return {"safe": False, "reason": f"Blocked pattern: {pattern}"}
        return {"safe": True}
    
    @tool(scope="admin")
    async def add_blocked_pattern(self, pattern: str) -> str:
        """Add a blocked pattern (admin only)"""
        self.blocked_patterns.append(pattern)
        return f"Added blocked pattern: {pattern}"
```

---

## 4. Robutler Platform Skills

### NLI Skill (Natural Language Interface)

```python
# robutler/agents/skills/robutler/nli.py
from typing import Dict, Any
from ..base import Skill
from ...tools.decorators import tool

class NLISkill(Skill):
    """Natural Language Interface skill for communicating with other agents"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.portal_url = config.get('portal_url') if config else None
        self.api_key = config.get('api_key') if config else None
        
        # Register the nli_tool tool for agent-to-agent communication
        self.register_tool(self.nli_tool)
    
    async def initialize(self, agent_context) -> None:
        """Initialize NLI for agent communication"""
        self.agent_context = agent_context
    
    @tool(scope="all")
    async def nli_tool(self, agent_url: str, message: str, authorized_amount: float = 0.1) -> str:
        """
        Natural Language Interface to communicate with other RobutlerAgent servers.
        
        Use this tool to send natural language messages to other agents and get their responses.
        This enables agent-to-agent collaboration and delegation.
        
        Args:
            agent_url: URL of the target agent server (e.g., http://localhost:2226/api/assistant)
            message: Natural language message to send to the agent
            authorized_amount: Maximum cost authorization for the communication (default 0.1)
            
        Returns:
            Response from the target agent
        """
        import httpx
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{agent_url}/chat/completions",
                    json={
                        "messages": [{"role": "user", "content": message}],
                        "stream": False
                    },
                    headers={
                        "Content-Type": "application/json",
                        "X-Payment-Token": self.api_key or "default",
                        "X-Authorized-Amount": str(authorized_amount)
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("choices") and len(result["choices"]) > 0:
                        return result["choices"][0]["message"]["content"]
                    return "No response from agent"
                else:
                    return f"Error communicating with agent: {response.status_code} - {response.text}"
                    
            except Exception as e:
                return f"Failed to communicate with agent at {agent_url}: {str(e)}"
```

### PaymentSkill (with @pricing decorator)

> **Note:** PaymentSkill is the **centralized pricing authority** in Robutler V2. It handles:
> - **Token markup calculation** based on user tiers and usage
> - **Per-call pricing** for tools via `@pricing` decorator  
> - **Billing integration** with the Robutler Portal
> - **Usage tracking** and cost calculation
> 
> Agents are **pricing-agnostic** - they don't have `markup_per_token` or pricing parameters. All pricing logic is handled by PaymentSkill.

```python
# robutler/agents/skills/robutler/payments.py
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from functools import wraps
import asyncio
from ..base import Skill
from ...tools.decorators import tool

class PaymentSkill(Skill):
    """Payment processing skill for token validation and charging"""
    
    def __init__(self, config: Dict = None):
        # PaymentSkill depends on AuthSkill for user validation
        super().__init__(config, scope="owner", dependencies=["robutler.auth"])
        self.portal_url = config.get('portal_url') if config else None
        self.api_key = config.get('api_key') if config else None
    
    async def initialize(self, agent: 'BaseAgent') -> None:
        """Initialize payment service"""
        self.agent = agent
        self.register_hook('before_request', self._validate_payment, priority=15)
        self.register_hook('after_finalize_connection', self._process_charges, priority=5)
        # Register payment tools
        self.register_tool(self.validate_payment_token)
        self.register_tool(self.charge_credits)
    
    async def _validate_payment(self, context: 'Context') -> 'Context':
        """Validate payment tokens for requests"""
        payment_token = context.get('payment_token')
        if payment_token:
            validation = await self._validate_token(payment_token)
            context.set('payment_validation', validation)
        return context
    
    async def _process_charges(self, context: 'Context') -> 'Context':
        """Process accumulated charges at connection end"""
        # Calculate total cost from usage records
        total_cost = sum(record.credits for record in context.usage_records)
        payment_token = context.get('payment_token')
        
        if total_cost > 0 and payment_token:
            result = await self._charge_token(payment_token, total_cost)
            context.set('payment_result', result)
            
        return context
    
    @tool(scope="owner")
    async def validate_payment_token(self, token: str) -> str:
        """Validate a payment token"""
        # Validate token via Robutler Portal API
        return f"Token {token} is valid"
    
    @tool(scope="owner") 
    async def charge_credits(self, token: str, amount: float, description: str) -> str:
        """Charge credits from a payment token"""
        # Charge via Robutler Portal API
        return f"Charged {amount} credits for {description}"
    
    async def _validate_token(self, token: str) -> Dict:
        """Internal token validation"""
        # Implementation would validate via portal API
        return {"valid": True, "balance": 100.0}
    
    async def _charge_token(self, token: str, amount: float) -> Dict:
        """Internal token charging"""
        # Implementation would charge via portal API
        return {"success": True, "remaining": 95.0}

    # @pricing Decorator - Moved from tools/decorators.py to PaymentSkill
    @dataclass
    class PricingInfo:
        """Pricing information returned by decorated functions"""
        credits: float
        reason: str
        metadata: Dict[str, Any] = None
        on_success: Optional[Callable] = None
        on_fail: Optional[Callable] = None

    def pricing(credits_per_call: Optional[float] = None, 
               reason: Optional[str] = None,
               on_success: Optional[Callable] = None, 
               on_fail: Optional[Callable] = None):
        """
        Enhanced pricing decorator for tool functions
        
        Usage patterns:
        1. Fixed pricing: @pricing(credits_per_call=1000)
        2. Dynamic pricing: @pricing() + return (result, PricingInfo(...))
        3. Callback pricing: @pricing(credits_per_call=500, on_success=callback_func)
        
        Args:
            credits_per_call: Fixed credits to charge per call
            reason: Custom reason for usage record
            on_success: Callback after successful payment
            on_fail: Callback after failed payment
        """
        def decorator(func: Callable) -> Callable:
            # Store pricing metadata on function for extraction
            func._robutler_pricing = {
                'credits_per_call': credits_per_call,
                'reason': reason or f"Tool '{func.__name__}' execution",
                'on_success': on_success,
                'on_fail': on_fail,
                'supports_dynamic': True  # Function can return PricingInfo
            }
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                result = await func(*args, **kwargs)
                # Return as-is, billing service will extract pricing info
                return result
            
            @wraps(func) 
            def sync_wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                return result
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
```

---

## 5. Extra Skills

### Google Skill

```python
# robutler/agents/skills/extra/google.py
from typing import Dict, Any
from ..base import Skill
from ...tools.decorators import tool

class GoogleSkill(Skill):
    """Google services integration skill"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.api_key = config.get('api_key') if config else None
        self.search_client = None
        
        # Auto-register tools
        self.register_tool(self.google_search)
        self.register_tool(self.google_translate)
    
    async def initialize(self, agent_context) -> None:
        """Initialize with agent context access"""
        self.agent_context = agent_context
        # Initialize Google services
        
        # Skill can access agent's memory, LLM, etc.
        await self.agent_context.remember_long_term("google_initialized", True)
    
    @tool(scope="all")
    async def google_search(self, query: str, max_results: int = 5) -> str:
        """Search Google and return formatted results"""
        # Implementation would call Google Search API
        results = [
            {"title": f"Result {i}", "url": f"https://example{i}.com", "snippet": f"Info about {query}"}
            for i in range(max_results)
        ]
        
        formatted = f"Google search results for '{query}':\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result['title']}\n   {result['snippet']}\n   {result['url']}\n\n"
        
        return formatted
    
    @tool(scope="all")
    async def google_translate(self, text: str, target_language: str = "en", source_language: str = "auto") -> str:
        """Translate text using Google Translate"""
        # Implementation would call Google Translate API
        return f"Translated '{text}' from {source_language} to {target_language}: [Mock Translation]"
```

### Database Skill

```python
# robutler/agents/skills/extra/database.py  
from typing import Dict, Any
from ..base import Skill
from ...tools.decorators import tool

class DatabaseSkill(Skill):
    """Skill providing database access"""
    
    def __init__(self, connection_string: str, config: Dict = None):
        # DatabaseSkill depends on GuardrailsSkill for security validation
        super().__init__(config, scope="owner", dependencies=["guardrails"])  # Restricted to owners
        self.connection_string = connection_string
        self.db = None
        
        # Auto-register tools with specific scopes
        self.register_tool(self.db_query, scope="owner")  # Override tool scope
        self.register_tool(self.db_insert, scope="owner")  # Restrict to owners
    
    async def initialize(self, agent_context) -> None:
        """Initialize database connection"""
        self.agent_context = agent_context
        self.db = await self._connect_database(self.connection_string)
    
    async def _connect_database(self, connection_string: str):
        """Connect to database"""
        # Implementation would create database connection
        return f"connected_to_{connection_string}"
    
    @tool(scope="owner")  # Database access only for owners
    async def db_query(self, sql: str) -> str:
        """Execute SQL query"""
        if not self.db:
            return "Database not connected"
        
        # Use guardrails skill to validate SQL safety
        guardrails = self.agent_context.get_skill("guardrails")
        if guardrails:
            safety_check = await guardrails.analyze_content_safety(sql)
            if not safety_check.get("safe", True):
                return f"Query blocked by safety filter: {safety_check.get('reason')}"
        
        # Execute query (mock implementation)
        return f"Query result for: {sql}"
    
    @tool(scope="owner")
    async def db_insert(self, table: str, data: Dict[str, Any]) -> str:
        """Insert data into database table"""
        if not self.db:
            return "Database not connected"
        return f"Inserted into {table}: {data}"
```

---

## 6. Skill Dependency System

### Dependency Declaration and Resolution

```python
# Example dependency relationships
class PaymentSkill(Skill):
    def __init__(self, config: Dict = None):
        # PaymentSkill depends on AuthSkill for user validation
        super().__init__(config, scope="owner", dependencies=["robutler.auth"])

class DatabaseSkill(Skill):
    def __init__(self, connection_string: str, config: Dict = None):
        # DatabaseSkill depends on GuardrailsSkill for security validation
        super().__init__(config, scope="owner", dependencies=["guardrails"])

# Automatic Resolution in BaseAgent
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
```

### Usage Examples

```python
# When creating an agent with PaymentSkill, dependencies are auto-included
agent = BaseAgent(
    name="payment-agent",
    skills={
        "payments": PaymentSkill()  # Only specify this skill
    }
)
# Result: Agent automatically includes robutler.auth skill
# Final skills: {"payments": PaymentSkill, "robutler.auth": AuthSkill}

# Complex dependency example
agent = BaseAgent(
    name="complex-agent",
    skills={
        "database": DatabaseSkill("postgresql://localhost/db"),  # Depends on guardrails
        "payments": PaymentSkill()  # Depends on robutler.auth
    }
)
# Result: Agent automatically includes both guardrails and robutler.auth
```

---

## 7. Workflow System

The workflow system provides orchestration capabilities to coordinate multiple skills for complex tasks.

```python
# robutler/agents/workflows/decorators.py
from typing import List, Dict, Any, Callable
from .context import WorkflowContext

def workflow(name: str, dependencies: List[str] = None, version: str = "1.0"):
    """Decorator to register a workflow that orchestrates multiple skills"""
    def decorator(func: Callable):
        func._workflow_name = name
        func._workflow_dependencies = dependencies or []
        func._workflow_version = version
        return func
    return decorator

# Example: Complex research workflow using multiple skills
@workflow(
    name="research_and_report",
    dependencies=["google", "robutler.storage", "robutler.messages", "openai"],
    version="1.0"
)
async def research_and_report_workflow(workflow_context: WorkflowContext, topic: str, depth: str = "basic") -> Dict:
    """
    Orchestrates research workflow using multiple skills:
    1. Search for information (Google skill)
    2. Analyze with different LLM (OpenAI skill) 
    3. Store findings (Storage skill)
    4. Track progress (Messages skill)
    """
    
    # Skills are loaded as dependencies - no tools/hooks active by default
    google_skill = workflow_context.get_dependency("google")
    storage_skill = workflow_context.get_dependency("robutler.storage") 
    messages_skill = workflow_context.get_dependency("robutler.messages")
    openai_skill = workflow_context.get_dependency("openai")
    
    # Track workflow progress
    await messages_skill.store_message(f"Starting research on: {topic}")
    
    # Step 1: Gather information
    search_results = await google_skill.google_search(f"{topic} comprehensive guide")
    
    # Step 2: Analyze with specialized LLM
    analysis = await openai_skill.query_openai(
        "gpt-4", 
        [{"role": "system", "content": f"Analyze this research on {topic}: {search_results}"}]
    )
    
    # Step 3: Store findings
    research_data = {
        "topic": topic,
        "search_results": search_results,
        "analysis": analysis,
        "depth": depth,
        "timestamp": "2024-01-01T00:00:00Z"
    }
    await storage_skill.store_data(f"research_{topic}", research_data)
    
    # Step 4: Complete workflow
    await messages_skill.store_message(f"Research completed for: {topic}")
    
    return {
        "status": "completed",
        "topic": topic,
        "findings_key": f"research_{topic}",
        "analysis_summary": analysis
    }
```

---

## Summary

Chapter 3 provides the complete skills system architecture for Robutler V2:

✅ **Skill Base Classes** - Complete interface with dependencies and runtime registration  
✅ **Core Skills** - 3-tier memory system, LLM providers, guardrails, MCP integration  
✅ **Robutler Platform Skills** - NLI, discovery, auth, payments (with @pricing), messages, storage  
✅ **Extra Skills** - Google services, database access, platform integrations  
✅ **Dependency System** - Automatic resolution of skill dependencies  
✅ **Workflow System** - Orchestration of multiple skills for complex tasks  
✅ **Dynamic Registration** - Runtime adaptation based on request context  

**Next**: [Chapter 4: Server & Tools](./ROBUTLER_V2_DESIGN_Ch4_Server_Tools.md) - FastAPI server implementation and tool system 

# ===== UNIFIED CONTEXT APPROACH =====

## **Single Context Design**

**🎯 The Key Insight:** Instead of having multiple confusing "context" types, we use **one unified Context** that contains everything:

### **Context Contains Everything:**

```python
# Single unified Context object available via get_context()
context = get_context()

# Request data
context.messages          # The conversation messages
context.user.peer_user_id # Who's making the request  
context.stream           # Is this streaming?
context.track_usage()    # Track costs/usage
context.get()/set()      # Store custom data

# Agent capabilities
context.agent_skills     # All available skills
context.agent_tools      # All available tools  
context.agent_handoffs   # All available handoffs
context.agent           # Full BaseAgent instance
```

### **External Tools vs Agent Tools:**

**🔧 CRITICAL UNDERSTANDING:** There are two distinct types of tools in Robutler V2:

1. **Agent Tools (@tool decorated functions)**: Executed **SERVER-SIDE** by the agent
   - Purpose: Internal agent capabilities (database, files, calculations)
   - Registration: Automatic via `@tool` decorator in skills
   - Execution: Server processes these tool calls directly

2. **External Tools (from request)**: Executed **CLIENT-SIDE** by the requesting client  
   - Purpose: Client-specific capabilities (user files, client APIs, user permissions)
   - Source: Specified in OpenAI ChatCompletion request's `tools` parameter
   - Server Role: Pass to LLM, return `tool_calls` to client for execution

### **How Skills Use It:**

```python
class MySkill(Skill):
    async def initialize(self, agent: 'BaseAgent') -> None:
        """Skills get simple agent reference for registration"""
        self.agent = agent
        self.register_hook('on_request', self.my_hook)
        self.register_tool(self.my_tool)
    
    async def my_hook(self, context: 'Context') -> 'Context':
        """Hooks receive unified Context with EVERYTHING"""
        
        # ✅ Access request data
        user_id = context.peer_user_id
        messages = context.messages
        is_streaming = context.stream
        
        # ✅ Access agent capabilities  
        other_skills = context.agent_skills
        available_tools = context.agent_tools
        
        # ✅ Store/retrieve custom data
        context.set("my_data", {"processed": True})
        
        # ✅ Track usage
        context.track_usage(10, "Hook processing")
        
        return context
    
    @tool
    async def my_tool(self, query: str) -> str:
        """Tools access everything via get_context()"""
        
        # ✅ Get unified context anywhere
        context = self.get_context()
        if context:
            # Everything available in one place!
            user_id = context.peer_user_id
            other_skills = context.agent_skills
            context.track_usage(25, "Tool execution")
        
        return f"Processed {query}"
```

### **Benefits:**

✅ **Single Mental Model** - Just one "context" concept  
✅ **Everything Accessible** - Request data + agent capabilities in one place  
✅ **No Confusion** - No more "which context do I use?"  
✅ **Backward Compatible** - Still use `get_context()` pattern  
✅ **Clean API** - Properties like `context.peer_user_id`  
✅ **Consistent** - Same pattern everywhere (hooks, tools, skills)  

### **Migration from Old Approach:**

**Before (Confusing):**
```python
# Multiple context types - confusing!
async def my_hook(self, request_context: Dict) -> Dict:
    # Had to access agent capabilities via self.agent_context
    # Had to access request data via request_context parameter
    user_id = request_context.get('user_id')
    skills = self.agent_context.get_all_skills()
```

**After (Simple):**
```python
# Single unified context - clean!
async def my_hook(self, context: Context) -> Context:
    # Everything in one place!
    user_id = context.peer_user_id
    skills = context.agent_skills
```

### **Context Flow:**

1. **BaseAgent** creates Context with request + agent data
2. **Hooks** receive Context, can access everything  
3. **Tools** get Context via `get_context()`, can access everything
4. **Skills** use Context for both request data and agent capabilities

**Result:** One simple, consistent, powerful context system! 🎉

# ===== ENHANCED TOOL AND HANDOFF SYSTEM =====

## **@tool with Context Injection**

Tools can now optionally receive the unified Context as a parameter:

```python
from robutler.agents.tools.decorators import tool
from robutler.server.context.context_vars import get_context

class ResearchSkill(Skill):
    
    @tool
    def basic_search(self, query: str) -> str:
        """Basic search without context"""
        return f"Search results for: {query}"
    
    @tool
    def context_aware_search(self, query: str, context: Context = None) -> str:
        """Advanced search with context (automatically injected)"""
        if context:
            # Access request data
            user_id = context.peer_user_id
            is_streaming = context.stream
            
            # Access agent capabilities
            has_vector_memory = "memory_vector" in context.agent_skills
            
            # Track usage
            context.track_usage(25, f"Search for {user_id}")
            
            # Store search metadata
            context.set("last_search", query)
            context.set("search_timestamp", datetime.utcnow())
            
            # Enhanced search based on available capabilities
            if has_vector_memory:
                vector_skill = context.agent_skills["memory_vector"]
                # Use vector search for semantic results
                semantic_results = vector_skill.similarity_search(query)
                return f"Enhanced search for {user_id}: {query} (found {len(semantic_results)} semantic matches)"
            else:
                return f"Basic search for {user_id}: {query}"
        
        return f"Search: {query} (no context available)"
    
    @tool
    def user_specific_tool(self, action: str, context: Context = None) -> str:
        """Tool that adapts based on user permissions"""
        if context:
            user_id = context.peer_user_id
            payment_user = context.payment_user_id
            
            # Different behavior based on user type
            if context.get("auth_scope") == "admin":
                context.track_usage(10, f"Admin action: {action}")
                return f"Admin {user_id} executed: {action}"
            elif payment_user:
                context.track_usage(20, f"Premium action: {action}")
                return f"Premium user {user_id} executed: {action}"
            else:
                context.track_usage(30, f"Basic action: {action}")
                return f"User {user_id} executed: {action} (basic tier)"
        
        return f"Executed: {action}"
```

## **@handoff Decorator for Control Transfer**

The new `@handoff` decorator handles control transfer to other agents, LLMs, or workflows:

```python
from robutler.agents.tools.decorators import handoff, HandoffResult

class CustomerServiceSkill(Skill):
    
    @handoff
    async def escalate_to_human(self, issue: str, urgency: str = "normal", 
                               context: Context = None) -> HandoffResult:
        """Escalate to human customer service agent"""
        if context:
            user_id = context.peer_user_id
            context.track_usage(100, f"Human escalation for {user_id}")
            
            # Create escalation ticket
            ticket_data = {
                "user_id": user_id,
                "issue": issue,
                "urgency": urgency,
                "conversation_history": context.messages[-10:],  # Last 10 messages
                "agent_attempted_resolution": True
            }
            
            # Transfer to human agent system
            human_agent_system = self.get_external_system("human_agents")
            ticket_id = await human_agent_system.create_ticket(ticket_data)
            
            return HandoffResult(
                result=f"Escalated to human agent. Ticket ID: {ticket_id}",
                handoff_type="human_agent",
                metadata={"ticket_id": ticket_id, "urgency": urgency}
            )
        
        return HandoffResult(
            result="Failed to escalate - no context available",
            handoff_type="human_agent",
            transfer_complete=False
        )
    
    @handoff(handoff_type="llm")
    async def switch_to_creative_model(self, task: str, context: Context = None) -> HandoffResult:
        """Switch to creative LLM for artistic/creative tasks"""
        if context:
            # Get creative LLM skill
            if "anthropic" in context.agent_skills:
                creative_llm = context.agent_skills["anthropic"]
                
                # Prepare creative prompt
                creative_messages = context.messages + [
                    {"role": "system", "content": "You are a highly creative AI assistant. Focus on imaginative, artistic, and innovative responses."},
                    {"role": "user", "content": f"Creative task: {task}"}
                ]
                
                # Execute with creative settings
                result = await creative_llm.chat_completion(
                    messages=creative_messages,
                    temperature=0.9,
                    max_tokens=1000
                )
                
                context.track_usage(75, "Creative LLM handoff")
                
                return HandoffResult(
                    result=result.get("content", "Creative response generated"),
                    handoff_type="llm",
                    metadata={"model": "claude-3-5-sonnet", "temperature": 0.9}
                )
        
        return HandoffResult(
            result="Unable to switch to creative model",
            handoff_type="llm",
            transfer_complete=False
        )
    
    @handoff(handoff_type="workflow")
    async def trigger_approval_workflow(self, request: str, approver_type: str = "manager",
                                      context: Context = None) -> HandoffResult:
        """Trigger n8n approval workflow"""
        if context and "n8n" in context.agent_skills:
            n8n_skill = context.agent_skills["n8n"]
            
            workflow_data = {
                "request": request,
                "approver_type": approver_type,
                "requester_id": context.peer_user_id,
                "request_context": {
                    "messages": context.messages[-5:],  # Recent context
                    "timestamp": context.start_time.isoformat()
                }
            }
            
            # Execute n8n workflow
            workflow_result = await n8n_skill.execute_workflow("approval-flow", workflow_data)
            
            context.track_usage(50, f"Approval workflow triggered")
            
            return HandoffResult(
                result=f"Approval workflow started. ID: {workflow_result.get('workflow_id')}",
                handoff_type="workflow",
                metadata={
                    "workflow_id": workflow_result.get("workflow_id"),
                    "approver_type": approver_type
                }
            )
        
        return HandoffResult(
            result="Approval workflow not available",
            handoff_type="workflow",
            transfer_complete=False
        )
    
    @handoff(handoff_type="agent")
    async def transfer_to_specialist(self, domain: str, query: str, 
                                   context: Context = None) -> HandoffResult:
        """Transfer to domain specialist agent"""
        if context:
            # Map domain to specialist agent
            specialist_mapping = {
                "technical": "tech-support-agent",
                "billing": "billing-agent", 
                "sales": "sales-agent",
                "legal": "legal-agent"
            }
            
            specialist_name = specialist_mapping.get(domain, "general-support-agent")
            
            # Get specialist agent
            specialist_agent = self.get_agent(specialist_name)
            if specialist_agent:
                # Prepare handoff messages
                handoff_messages = context.messages + [
                    {"role": "system", "content": f"You are a {domain} specialist. The user has been transferred to you."},
                    {"role": "user", "content": f"{domain.title()} question: {query}"}
                ]
                
                # Execute specialist agent
                specialist_result = await specialist_agent.run(handoff_messages)
                
                context.track_usage(100, f"Specialist handoff to {specialist_name}")
                
                return HandoffResult(
                    result=specialist_result.choices[0].message.get("content", "Specialist response"),
                    handoff_type="agent",
                    metadata={
                        "specialist_agent": specialist_name,
                        "domain": domain
                    }
                )
        
        return HandoffResult(
            result=f"Unable to transfer to {domain} specialist",
            handoff_type="agent",
            transfer_complete=False
        )

# Usage in agent creation
customer_service_agent = BaseAgent(
    name="customer-service-bot",
    instructions="Provide excellent customer service with escalation capabilities",
    skills={
        "customer_service": CustomerServiceSkill(),
        "n8n": N8nSkill(),
        "anthropic": AnthropicSkill()
    },
    # Include handoff functions in tools list - they appear as tools to LLM
    tools=[
        CustomerServiceSkill().escalate_to_human,
        CustomerServiceSkill().switch_to_creative_model,
        CustomerServiceSkill().trigger_approval_workflow,
        CustomerServiceSkill().transfer_to_specialist
    ]
)
```

## **Benefits of Enhanced System:**

✅ **Context Injection**: Tools can optionally receive unified Context  
✅ **Cleaner Tool Code**: No need to manually call `get_context()`  
✅ **Handoff Support**: First-class support for control transfer  
✅ **Backward Compatible**: Existing tools without context still work  
✅ **Type Safety**: Context parameter is properly typed and optional  
✅ **Unified Interface**: Both tools and handoffs use same decorator pattern  

## **How It Works:**

1. **@tool with context**: Automatically injects Context if function signature has `context` parameter
2. **@handoff decorator**: Registers handoff functions as tools that transfer control instead of returning results
3. **BaseAgent**: Detects @handoff functions and registers them as handoff configurations
4. **Context Injection**: Both tools and handoffs get automatic context injection
5. **HandoffResult**: Structured result that can be converted to tool response for LLM

**Result**: Much cleaner tool code with powerful handoff capabilities! 🎉

## **Migration: Manual Context vs Context Injection**

**Before (Manual Context Access):**
```python
@tool
async def my_tool(self, query: str) -> str:
    """Tool that manually gets context"""
    
    # Manual context retrieval - verbose and error-prone
    context = self.get_context()  # Could return None
    if context:
        user_id = context.peer_user_id
        agent_skills = context.agent_skills
        
        # Track usage manually
        context.track_usage(25, "Tool execution")
        
        # Do work with context
        if "vector_memory" in agent_skills:
            # Use vector search
            result = f"Enhanced search for {user_id}: {query}"
        else:
            result = f"Basic search for {user_id}: {query}"
            
        return result
    else:
        # Fallback when no context available
        return f"Search: {query} (no context)"
```

**After (Context Injection - Recommended):**
```python
@tool
async def my_tool(self, query: str, context: Context = None) -> str:
    """Tool with automatic context injection"""
    
    # Context automatically injected - clean and reliable
    if context:
        user_id = context.peer_user_id
        agent_skills = context.agent_skills
        
        # Track usage
        context.track_usage(25, "Tool execution")
        
        # Do work with context
        if "vector_memory" in agent_skills:
            result = f"Enhanced search for {user_id}: {query}"
        else:
            result = f"Basic search for {user_id}: {query}"
            
        return result
    
    # Fallback when no context available
    return f"Search: {query} (no context)"
```

**Benefits of Context Injection:**
- ✅ **Cleaner Code**: No manual `get_context()` calls
- ✅ **More Reliable**: Context automatically injected by BaseAgent
- ✅ **Better Testing**: Easy to mock context parameter in tests
- ✅ **Type Safety**: Context parameter is properly typed
- ✅ **Optional**: Tools can work with or without context
- ✅ **Backward Compatible**: Existing tools still work

**Both approaches are supported** - choose what works best for your use case!

# ===== BEFORE/AFTER LIFECYCLE EVENTS =====

## **Enhanced Lifecycle Hook System**

**🎯 The Key Innovation:** Instead of single `on_*` events, we now have **before_** and **after_** events for precise control:

### **Event Types:**

```python
# Request Lifecycle
'before_request'  # Validation, auth, input safety, setup
'after_request'   # Cleanup, audit logging

# Response Lifecycle  
'before_response' # Output filtering, content validation
'after_response'  # Usage tracking, billing, memory storage

# Streaming Lifecycle
'before_chunk'    # Content filtering, modification
'after_chunk'     # Analytics, monitoring, real-time processing

# Tool Execution Lifecycle
'before_toolcall' # Security validation, parameter modification  
'after_toolcall'  # Result processing, logging, analytics

# Handoff Lifecycle
'before_handoff'  # Conversation filtering, security checks
'after_handoff'   # Handoff logging, cleanup, audit

# Connection Lifecycle
'before_connection'        # Connection setup, rate limiting
'after_connection'         # Connection cleanup
'before_finalize_connection'  # Final billing calculations
'after_finalize_connection'   # Cleanup, audit logging
```

### **Benefits of Before/After Pattern:**

✅ **Precise Control**: Execute logic exactly when needed  
✅ **Clear Separation**: Setup vs cleanup logic  
✅ **Better Error Handling**: Separate error handling for each phase  
✅ **Improved Debugging**: Clear visibility into each lifecycle phase  
✅ **Flexible Priorities**: Fine-grained control over execution order  
✅ **Better Testing**: Test before and after logic separately  

### **Hook Execution Order:**

1. **before_connection** (if applicable)
2. **before_request** (authentication, validation, setup)  
3. **before_chunk** (streaming content filtering) - repeated per chunk
4. **after_chunk** (streaming analytics) - repeated per chunk
5. **before_toolcall** (tool security, parameter modification) - per tool
6. **after_toolcall** (tool result processing, logging) - per tool
7. **before_handoff** (conversation filtering, validation) - if handoff occurs
8. **after_handoff** (handoff logging, cleanup) - if handoff occurs
9. **before_response** (output filtering, content validation)
10. **after_response** (usage tracking, memory storage)
11. **before_finalize_connection** (final billing calculations)
12. **after_finalize_connection** (cleanup, audit logging)
13. **after_connection** (if applicable)

**Result**: Precise control over every phase of the request lifecycle! 🎯

# ===== SIMPLIFIED LIFECYCLE HOOK SYSTEM =====

## **New @hook Decorator with Automatic Registration**

**🎯 Key Innovation:** Skills now use `@hook` decorators for automatic lifecycle hook registration - no more manual `register_hook()` calls!

### **Simplified Lifecycle Events:**

```python
# Simplified Event System
'on_connection'        → Connection setup, authentication, validation, input safety
'on_chunk'            → Content filtering, modification (per chunk)
'on_message'          → Content filtering, modification (per message, incoming/outgoing)
'before_toolcall'     → Security validation, parameter modification (per tool)
'after_toolcall'      → Result processing, logging (per tool)
'before_handoff'      → Conversation filtering, security (if handoff)
'after_handoff'       → Handoff logging, cleanup (if handoff)
'finalize_connection' → Connection cleanup, billing, analytics
```

### **@hook Decorator Usage:**

```python
from robutler.agents.tools.decorators import hook, tool, handoff

class ModernSkill(Skill):
    """Example skill using @hook decorator for automatic registration"""
    
    async def initialize(self, agent: 'BaseAgent') -> None:
        """Initialize skill - hooks auto-registered via decorators"""
        self.agent = agent
        # No manual register_hook() calls needed!
    
    @hook("on_connection", priority=5)  # All scopes
    async def setup_connection(self, context: Context) -> Context:
        """Setup connection and authenticate user"""
        # Authentication and connection setup logic
        user_token = context.get('auth_token')
        if user_token:
            user_info = await self._validate_token(user_token)
            context.set('authenticated_user', user_info)
        return context
    
    @hook("on_chunk", priority=10)
    async def filter_chunk(self, context: Context) -> Context:
        """Filter streaming chunks in real-time"""
        chunk_content = context.get('content', '')
        filtered_content = await self._apply_content_filter(chunk_content)
        context.set('content', filtered_content)
        return context
    
    @hook("on_message", priority=15)
    async def process_message(self, context: Context) -> Context:
        """Process complete messages (incoming/outgoing)"""
        # Process assembled messages for both REST requests/responses
        # and streaming chunks assembled into complete messages
        for message in context.messages:
            if message.get('role') == 'user':
                # Filter and validate user messages
                message['content'] = await self._sanitize_input(message['content'])
            elif message.get('role') == 'assistant':
                # Process assistant responses
                message['content'] = await self._enhance_response(message['content'])
        return context
    
    @hook("before_toolcall", priority=5)
    async def validate_tool_security(self, context: Context) -> Context:
        """Validate tool security before execution"""
        tool_call = context.get('tool_call')
        if not self._is_tool_allowed(tool_call, context.peer_user_id):
            raise SecurityError(f"Tool {tool_call['function']['name']} not allowed")
        return context
    
    @hook("after_toolcall", priority=80)
    async def log_tool_execution(self, context: Context) -> Context:
        """Log tool execution results"""
        tool_call = context.get('tool_call')
        tool_result = context.get('tool_result')
        success = context.get('execution_successful', False)
        
        await self._audit_log({
            'tool': tool_call['function']['name'],
            'user': context.peer_user_id,
            'success': success,
            'timestamp': datetime.utcnow()
        })
        return context
    
    @hook("before_handoff", priority=10)
    async def sanitize_handoff(self, context: Context) -> Context:
        """Sanitize conversation before handoff"""
        conversation = context.messages
        sanitized = []
        for msg in conversation:
            if not self._contains_sensitive_data(msg.get('content', '')):
                sanitized.append(msg)
        context.messages = sanitized
        return context
    
    @hook("after_handoff", priority=80) 
    async def audit_handoff(self, context: Context) -> Context:
        """Audit handoff completion"""
        handoff_type = context.get('handoff_type')
        target = context.get('target')
        
        await self._audit_log({
            'event': 'handoff_completed',
            'type': handoff_type,
            'target': target,
            'user': context.peer_user_id,
            'timestamp': datetime.utcnow()
        })
        return context
    
    @hook("finalize_connection", priority=90, scope=["owner", "admin"])
    async def cleanup_and_bill(self, context: Context) -> Context:
        """Final cleanup, billing, and analytics (paid users only)"""
        # Process usage records for billing
        total_usage = sum(record.credits for record in context.usage_records)
        
        # Apply billing for paid users
        if total_usage > 0:
            await self._charge_user(context.peer_user_id, total_usage)
        
        # Update analytics  
        await self._record_session_metrics(context)
        
        # Cleanup resources
        await self._cleanup_session_data(context)
        
        return context
    
    @hook("on_message", priority=20, scope="admin")
    async def admin_message_filter(self, context: Context) -> Context:
        """Advanced message filtering for admin users"""
        # Admin-only message processing
        for message in context.messages:
            if message.get('role') == 'user':
                # Apply advanced admin filters
                message['content'] = await self._apply_admin_filters(message['content'])
        return context
    
    # Tools and handoffs can be mixed with hooks
    @tool  # All scopes
    def example_tool(self, query: str, context: Context = None) -> str:
        """Tool with automatic context injection (available to all users)"""
        if context:
            return f"Processed '{query}' for user {context.peer_user_id}"
        return f"Processed '{query}'"
    
    @tool(scope="owner")
    def owner_billing_tool(self, context: Context = None) -> str:
        """Get detailed billing information (owner only)"""
        if context:
            # Access billing data only available to owners
            billing_data = await self._get_owner_billing_data(context.peer_user_id)
            return f"Billing summary: {billing_data}"
        return "Billing data not available"
    
    @tool(scope=["owner", "admin"])
    def advanced_analytics_tool(self, query: str, context: Context = None) -> str:
        """Advanced analytics for owners and admins"""
        if context:
            # Perform advanced analytics
            analytics = await self._get_advanced_analytics(query, context.peer_user_id)
            return f"Advanced analytics: {analytics}"
        return "Advanced analytics not available"
    
    @handoff  # All scopes
    async def escalate_to_human(self, issue: str, context: Context = None) -> HandoffResult:
        """Handoff to human agent (available to all users)"""
        if context:
            ticket_id = await self._create_support_ticket(issue, context.peer_user_id)
            return HandoffResult(
                result=f"Escalated to human support. Ticket: {ticket_id}",
                handoff_type="human_agent",
                metadata={"ticket_id": ticket_id}
            )
        return HandoffResult(result="Escalation failed - no context", transfer_complete=False)
    
    @handoff(scope="owner")
    async def escalate_to_premium_support(self, issue: str, context: Context = None) -> HandoffResult:
        """Handoff to premium support (owner only)"""
        if context:
            ticket_id = await self._create_premium_support_ticket(issue, context.peer_user_id)
            return HandoffResult(
                result=f"Escalated to premium support. Priority ticket: {ticket_id}",
                handoff_type="premium_human_agent", 
                metadata={"ticket_id": ticket_id, "priority": "high"}
            )
        return HandoffResult(result="Premium escalation failed", transfer_complete=False)
```

### **Benefits of @hook Decorator:**

✅ **Automatic Registration**: No manual `register_hook()` calls needed  
✅ **Cleaner Code**: Decorators clearly mark lifecycle methods  
✅ **Type Safety**: IDE support for decorated methods  
✅ **Priority Control**: Set priority directly in decorator  
✅ **Self-Documenting**: Clear what each method does from decorator  
✅ **Consistent**: Same pattern as `@tool` and `@handoff`  

### **Event Flow:**

1. **on_connection** → User connects, authentication, setup
2. **on_chunk** → Each streaming chunk (real-time processing)  
3. **on_message** → Complete messages (both directions, assembled chunks)
4. **before_toolcall** → Before each tool execution (security, validation)
5. **after_toolcall** → After each tool execution (logging, processing)
6. **before_handoff** → Before handoff (conversation filtering)
7. **after_handoff** → After handoff (auditing, cleanup)
8. **finalize_connection** → Session end (billing, cleanup, analytics)

### **Migration from Manual Registration:**

```python
# OLD WAY (Manual Registration)
class OldSkill(Skill):
    async def initialize(self, agent):
        self.agent = agent
        self.register_hook('before_request', self._validate_input, priority=5)
        self.register_hook('after_response', self._log_response, priority=80)
    
    async def _validate_input(self, context):
        # Implementation
        return context

# NEW WAY (@hook Decorator)  
class NewSkill(Skill):
    async def initialize(self, agent):
        self.agent = agent
        # Hooks auto-registered via decorators!
    
    @hook("on_connection", priority=5)
    async def _validate_input(self, context):
        # Same implementation  
        return context
    
    @hook("finalize_connection", priority=80)
    async def _log_response(self, context):
        # Same implementation
        return context
```

**Result**: Clean, automatic hook registration with clear lifecycle phases! 🚀

# ===== SCOPE-BASED ACCESS CONTROL =====

## **Unified Scope System for @hook, @tool, and @handoff**

**🎯 Key Feature:** All decorators (`@hook`, `@tool`, `@handoff`) now support consistent scope-based access control.

### **Scope Parameter Options:**

```python
# No scope = Available to all users (default)
@tool
@hook("on_message")
@handoff

# String scope = Available to specific user type  
@tool(scope="owner")
@hook("finalize_connection", scope="admin") 
@handoff(scope="owner")

# List scope = Available to multiple user types
@tool(scope=["owner", "admin"])
@hook("on_connection", scope=["owner", "admin", "premium"])
@handoff(scope=["admin"])
```

### **Common Scope Types:**

- **`None` (default)**: Available to all users (no restrictions)
- **`"owner"`**: Available to agent owners (who created/own the agent)
- **`"admin"`**: Available to admin users (platform administrators)  
- **`"premium"`**: Available to premium/paid users
- **`["owner", "admin"]`**: Available to both owners and admins
- **Custom scopes**: Define your own scope types as needed

### **Scope Filtering in Action:**

```python
class ScopedSkill(Skill):
    """Example skill demonstrating comprehensive scope usage"""
    
    # === HOOKS WITH SCOPES ===
    
    @hook("on_connection")  # All users
    async def basic_connection_setup(self, context: Context) -> Context:
        """Basic connection setup for all users"""
        context.set("connection_type", "basic")
        return context
    
    @hook("on_connection", priority=10, scope="owner")  # Owners only
    async def owner_connection_setup(self, context: Context) -> Context:
        """Enhanced connection setup for owners"""
        context.set("connection_type", "owner")
        context.set("premium_features_enabled", True)
        return context
    
    @hook("on_message", scope=["owner", "admin"])  # Owners and admins
    async def advanced_message_processing(self, context: Context) -> Context:
        """Advanced message processing for privileged users"""
        # Apply advanced processing only for owners/admins
        for message in context.messages:
            message['advanced_processed'] = True
        return context
    
    @hook("finalize_connection", scope="admin")  # Admins only  
    async def admin_cleanup(self, context: Context) -> Context:
        """Admin-specific cleanup and auditing"""
        await self._audit_admin_session(context)
        return context
    
    # === TOOLS WITH SCOPES ===
    
    @tool  # All users
    def basic_search(self, query: str) -> str:
        """Basic search available to all users"""
        return f"Basic search results for: {query}"
    
    @tool(scope="owner")  # Owners only
    def owner_dashboard(self, context: Context = None) -> str:
        """Owner dashboard with billing and analytics"""
        if context:
            return f"Owner dashboard for {context.peer_user_id}"
        return "Owner dashboard not available"
    
    @tool(scope=["owner", "admin"])  # Multiple scopes
    def advanced_analytics(self, metric: str, context: Context = None) -> str:
        """Advanced analytics for privileged users"""
        if context:
            return f"Advanced {metric} analytics for {context.peer_user_id}"
        return f"Advanced {metric} analytics not available"
    
    @tool(scope="admin")  # Admins only
    def system_administration(self, command: str) -> str:
        """System administration tools"""
        return f"Executed admin command: {command}"
    
    # === HANDOFFS WITH SCOPES ===
    
    @handoff  # All users
    async def basic_escalation(self, issue: str, context: Context = None) -> HandoffResult:
        """Basic escalation available to all users"""
        return HandoffResult(
            result=f"Basic escalation for: {issue}",
            handoff_type="basic_support"
        )
    
    @handoff(scope="owner")  # Owners only
    async def priority_escalation(self, issue: str, context: Context = None) -> HandoffResult:
        """Priority escalation for owners"""
        return HandoffResult(
            result=f"Priority escalation for: {issue}",
            handoff_type="priority_support",
            metadata={"priority": "high", "sla": "2_hours"}
        )
    
    @handoff(scope=["admin"])  # Admins only
    async def system_handoff(self, system_issue: str, context: Context = None) -> HandoffResult:
        """System-level handoff for admins"""
        return HandoffResult(
            result=f"System handoff for: {system_issue}",
            handoff_type="system_admin",
            metadata={"level": "system", "immediate": True}
        )
```

### **Scope Resolution Logic:**

```python
def _is_scope_allowed(self, required_scope: Union[str, List[str], None], auth_scope: str) -> bool:
    """Check if user scope allows access to item with required scope"""
    # No scope requirement means available to all
    if required_scope is None:
        return True
        
    # Convert to list for uniform handling
    if isinstance(required_scope, str):
        required_scopes = [required_scope]
    else:
        required_scopes = required_scope
    
    # Check if user scope matches any required scope
    return auth_scope in required_scopes
```

### **Runtime Scope Filtering:**

When hooks, tools, or handoffs are accessed:

1. **Hook Execution**: Only hooks with matching scopes are executed
2. **Tool Registration**: Only tools with matching scopes are available to LLM
3. **Handoff Discovery**: Only handoffs with matching scopes are registered

```python
# Example: Getting hooks for owner user
owner_hooks = agent.get_hooks_for_event("on_connection", auth_scope="owner")
# Returns: basic hooks + owner-specific hooks

# Example: Getting hooks for regular user  
user_hooks = agent.get_hooks_for_event("on_connection", auth_scope="user")
# Returns: only basic hooks (no owner/admin hooks)

# Example: Getting tools for admin user
admin_tools = agent.get_tools_by_scope(auth_scope="admin") 
# Returns: all tools + admin-specific tools
```

### **Benefits of Unified Scope System:**

✅ **Consistent**: Same scope parameter across all decorators  
✅ **Flexible**: Support for multiple scopes per item  
✅ **Secure**: Automatic filtering based on user permissions  
✅ **Simple**: No scope = available to all users  
✅ **Extensible**: Define custom scope types as needed  
✅ **Runtime Safe**: Scope filtering happens automatically during execution  

### **Migration from Manual Scoping:**

```python
# OLD: Manual scope checking in code
@tool
def owner_tool(self, context: Context = None) -> str:
    if context and context.get('auth_scope') != 'owner':
        raise PermissionError("Owner access required")
    # Tool logic here

# NEW: Declarative scope on decorator  
@tool(scope="owner")
def owner_tool(self, context: Context = None) -> str:
    # Tool logic here - scope automatically enforced
    pass
```

**Result**: Unified, secure, and maintainable access control across all agent capabilities! 🛡️

### **@prompt Decorator - Dynamic System Prompt Generation**

The `@prompt` decorator enables skills to contribute dynamic content to the system prompt before LLM execution. Prompt functions are called in priority order (lower numbers first) and their outputs are combined into the system message.

```python
from robutler.agents.tools.decorators import prompt

class DynamicPromptSkill(Skill):
    """Example skill using @prompt decorator for system prompt enhancement"""
    
    async def initialize(self, agent: 'BaseAgent') -> None:
        """Initialize skill - prompts auto-registered via decorators"""
        self.agent = agent
        # No manual register_prompt() calls needed!
    
    @prompt(priority=10)  # All scopes
    def system_status_prompt(self, context: Context) -> str:
        """Add current system status to prompt"""
        return f"System Status: {self._get_system_status()}"
    
    @prompt(priority=20, scope="owner")
    def user_context_prompt(self, context: Context) -> str:
        """Add user-specific context (owner only)"""
        user_id = getattr(context, 'user_id', 'anonymous')
        user_data = self._get_user_context(user_id)
        return f"User Context: {user_data['name']} ({user_data['role']})"
    
    @prompt(priority=5, scope=["admin"])
    async def admin_debug_prompt(self, context: Context) -> str:
        """Add debug information for admin users"""
        debug_info = await self._get_debug_info()
        return f"DEBUG MODE: {debug_info}"
    
    @prompt(priority=30)
    def time_context_prompt(self, context: Context) -> str:
        """Add current time context"""
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        return f"Current Time: {current_time}"
```

**Prompt Execution Flow:**
1. Before LLM call, all `@prompt` functions are executed in priority order
2. String outputs are combined with newlines (`\n\n`)
3. Combined prompt content is added to the system message
4. If no system message exists, one is created with agent instructions + prompts
5. If system message exists, prompts are appended to it

**Example Enhanced System Message:**
```
You are a helpful AI assistant.

DEBUG MODE: Server load: 23%, Memory: 1.2GB

System Status: Online - All services operational

User Context: John Smith (Premium User)

Current Time: 2024-07-22 14:30:15 UTC
```

### **Benefits of @prompt Decorator:**

✅ **Dynamic Prompts**: Generate context-aware system prompts at runtime  
✅ **Priority Control**: Control prompt order with priority values  
✅ **Scope Filtering**: Different prompts for different user access levels  
✅ **Context Access**: Full access to request context and user data  
✅ **Automatic Registration**: No manual registration needed  
✅ **Async Support**: Both sync and async prompt functions supported  
✅ **Error Resilience**: Prompt failures don't break LLM execution  
✅ **Modular**: Different skills can contribute different prompt aspects  

### **Event Flow:**

1. **on_connection** → User connects, authentication, setup
2. **on_chunk** → Each streaming chunk (real-time processing)  
3. **on_message** → Complete messages (both directions, assembled chunks)
4. **before_toolcall** → Before each tool execution (security, validation)
5. **after_toolcall** → After each tool execution (logging, processing)
6. **before_handoff** → Before handoff (conversation filtering)
7. **after_handoff** → After handoff (auditing, cleanup)
8. **finalize_connection** → Session end (billing, cleanup, analytics)