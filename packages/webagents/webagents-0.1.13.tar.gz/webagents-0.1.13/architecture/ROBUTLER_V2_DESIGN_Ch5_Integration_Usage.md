# Robutler V2 Design Document - Chapter 5: Integration & Usage

## Overview

This chapter provides comprehensive usage examples, integration patterns, and real-world implementation scenarios. It demonstrates how to create agents, integrate skills, and deploy production-ready systems.

---

## 1. Basic Usage Examples

### Minimal Agent Setup

```python
# Option 1: Skill/Model format (explicit and clear)
from robutler.agents.core.base_agent import BaseAgent

# Direct OpenAI with specific model
openai_agent = BaseAgent(
    name="openai-chat",
    instructions="You are a helpful assistant",
    model="openai/gpt-4o"  # Creates OpenAISkill with gpt-4o
)

# Anthropic Claude
claude_agent = BaseAgent(
    name="claude-chat", 
    instructions="You are a helpful assistant",
    model="anthropic/claude-3-sonnet"  # Creates AnthropicSkill with claude-3-sonnet
)

# LiteLLM for cross-provider routing
litellm_agent = BaseAgent(
    name="litellm-chat",
    instructions="You are a helpful assistant", 
    model="litellm/openai/gpt-4o"  # Creates LiteLLMSkill with openai/gpt-4o
)

# xAI Grok
grok_agent = BaseAgent(
    name="grok-chat",
    instructions="You are a helpful assistant",
    model="xai/grok-beta"  # Creates XAISkill with grok-beta
)

# Option 2: Custom LLM skill instance (for advanced configuration)
from robutler.agents.skills.openai import OpenAISkill

custom_agent = BaseAgent(
    name="custom-chat",
    instructions="You are a helpful assistant",
    model=OpenAISkill({
        "api_key": "sk-...", 
        "temperature": 0.7,
        "max_tokens": 1000
    })
)

# Option 3: Skills-only approach (V2 pure approach)
skills_agent = BaseAgent(
    name="skills-chat",
    instructions="You are a helpful assistant",
    skills={
        "openai": OpenAISkill({"api_key": "sk-..."})
    }
)

# All work the same way
response = await openai_agent.run([
    {"role": "user", "content": "Hello, how are you?"}
])
print(response.choices[0].message.content)
```

### Agent with Tools

```python
from robutler.agents.tools.decorators import tool
from robutler.agents.skills.base import Skill

# Define custom skill with @tool decorator (modern pattern)
class CalculatorSkill(Skill):
    async def initialize(self, agent: 'BaseAgent') -> None:
        """Initialize skill - tools auto-registered via @tool decorator!"""
        self.agent = agent
        # No manual register_tool() call needed!

    @tool  # Automatically discovered and registered by BaseAgent
    def calculate(self, expression: str) -> str:
    """Calculate a mathematical expression safely"""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except:
        return "Invalid expression"

# Create agent with skill-based tools - modern pattern
calculator_agent = BaseAgent(
    name="calculator", 
    instructions="You are a helpful calculator assistant. Use the calculate tool for math.",
    model="openai/gpt-4o",  # OpenAI skill with GPT-4o model
    skills={
        "calculator": CalculatorSkill()  # Tools auto-registered from skill decorators
    }
    # Note: No tools=[] parameter needed - tools auto-registered via @tool decorators
)

# Usage
response = await calculator_agent.run([
    {"role": "user", "content": "What's 15 * 23 + 7?"}
])
# Agent will use the calculate tool automatically
```

### Agent with Memory

```python
from robutler.agents.skills.short_term_memory import ShortTermMemorySkill
from robutler.agents.skills.long_term_memory import LongTermMemorySkill

# Agent with memory capabilities  
memory_agent = BaseAgent(
    name="memory-assistant",
    instructions="You are a helpful assistant with perfect memory of our conversations",
    model="openai/gpt-4o",  # Primary LLM using explicit format
    skills={
        "short_term_memory": ShortTermMemorySkill({"max_messages": 50}),
        "long_term_memory": LongTermMemorySkill({"connection_string": "postgresql://..."})
    }
)

# Usage - memory is handled automatically by skills
response1 = await memory_agent.run([
    {"role": "user", "content": "My name is Alice and I love Python programming"}
])

response2 = await memory_agent.run([
    {"role": "user", "content": "What's my name and favorite language?"}
])
# Agent remembers from previous conversation
```

### Agent with Multiple LLM Skills

```python
from robutler.agents.skills.anthropic import AnthropicSkill
from robutler.agents.skills.openai import OpenAISkill

# Agent with primary model + additional LLM skills for specialization
multi_llm_agent = BaseAgent(
    name="multi-llm-assistant",
    instructions="""You are a versatile assistant. Use different LLM skills for different tasks:
    - Use primary LLM for general conversation
    - Use Claude (anthropic) for analytical and reasoning tasks  
    - Use OpenAI specialist for creative and technical tasks""",
    
    model="litellm/openai/gpt-4o",  # Primary LLM using LiteLLM for routing
    
    # Additional LLM skills for handoffs/specialization
    skills={
        "claude": AnthropicSkill({"api_key": "anthropic-key"}),
        "openai_specialist": OpenAISkill({"api_key": "sk-...", "model": "gpt-4-turbo"})
    }
)

# The agent can access different LLMs:
# - agent.context.get_llm_skill() -> returns the primary LiteLLMSkill with openai/gpt-4o
# - agent.context.get_skill("claude") -> returns AnthropicSkill for specialized tasks
# - agent.context.get_skill("openai_specialist") -> returns specialized OpenAI skill
```

---

## 2. Advanced Integration Patterns

### Full-Featured Agent

```python
from robutler.agents.core.base_agent import BaseAgent
from robutler.agents.skills.litellm import LiteLLMSkill
from robutler.agents.skills.short_term_memory import ShortTermMemorySkill
from robutler.agents.skills.long_term_memory import LongTermMemorySkill
from robutler.agents.skills.vector_memory import VectorMemorySkill
from robutler.agents.skills.guardrails import GuardrailsSkill  # V2.1
from robutler.agents.skills.google import GoogleSkill  # V2.1
from robutler.agents.skills.database import DatabaseSkill  # V2.1
from robutler.agents.tools.decorators import tool

# Advanced agent with multiple capabilities
advanced_agent = BaseAgent(
    name="research-assistant",
    instructions="""You are an advanced research assistant with access to:
    - Web search capabilities
    - Database access for storing findings
    - Memory for tracking research progress
    - Safety filters to ensure appropriate content
    
    Help users conduct thorough research on any topic.""",
    
    # Primary LLM using explicit skill/model format
    model="litellm/openai/gpt-4o",  # LiteLLM skill with OpenAI GPT-4o model
    
    skills={
        # Memory system
        "short_term_memory": ShortTermMemorySkill({"max_messages": 100}),
        "long_term_memory": LongTermMemorySkill({"connection_string": "postgresql://..."}),
        "vector_memory": VectorMemorySkill({"collection_name": "research_vectors"}),
        
        # Safety and security
        "guardrails": GuardrailsSkill({"safety_level": "high"}),
        
        # External services
        "google": GoogleSkill({"api_key": "google_api_key"}),
        "database": DatabaseSkill("postgresql://research_db"),
    
    # Custom research skill with @tool decorators
    "research": CustomResearchSkill()
}
# Note: No tools=[] parameter needed - tools auto-registered from skills via @tool decorators

# Custom research skill using modern decorator pattern
class CustomResearchSkill(Skill):
    async def initialize(self, agent: 'BaseAgent') -> None:
        """Initialize - tools auto-registered via decorators!"""
        self.agent = agent

    @tool  # Automatically registered by BaseAgent
    def research_tool(self, topic: str, context: Context = None) -> str:
        """Advanced research tool with context injection"""
        if context:
            user_id = context.peer_user_id
            context.track_usage(20, "Research query")
            
        # Use other skills for research
        google_skill = self.agent.skills["google"]
        database_skill = self.agent.skills["database"]
        
        # Perform research logic
        return f"Researched '{topic}' for user {user_id if context else 'unknown'}"
    
    @tool
    def save_findings_tool(self, findings: str, context: Context = None) -> str:
        """Save research findings with automatic context injection"""
        if context:
            context.track_usage(5, "Save findings")
            
        database_skill = self.agent.skills["database"]
        # Save findings logic
        return f"Saved findings: {findings}"
    
    # Note: Pricing is handled by PaymentSkill, not at agent level
)

@tool(scope="all")
async def research_tool(topic: str, depth: str = "basic") -> str:
    """Conduct research on a topic using available skills"""
    # This tool can access agent context and other skills
    agent_context = current_agent_context()  # Hypothetical context access
    
    # Use Google skill for search
    google_skill = agent_context.get_skill("google")
    search_results = await google_skill.google_search(f"{topic} comprehensive guide")
    
    # Store in vector memory for future retrieval
    vector_skill = agent_context.get_skill("vector_memory")
    await vector_skill.add_content(f"Research on {topic}: {search_results}")
    
    return f"Research completed on {topic}. Findings stored in memory."

@tool(scope="owner")
async def save_findings_tool(findings: str, category: str) -> str:
    """Save research findings to database"""
    agent_context = current_agent_context()
    db_skill = agent_context.get_skill("database")
    
    result = await db_skill.db_insert("research_findings", {
        "content": findings,
        "category": category,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return f"Findings saved: {result}"
```

---

## 3. Robutler Platform Integration

### RobutlerAgent with Full Platform Skills

```python
from robutler.agents.core.base_agent import BaseAgent
from robutler.agents.skills.payments import PaymentSkill
from robutler.agents.skills.nli import NLISkill
from robutler.agents.skills.discovery import DiscoverySkill
from robutler.agents.skills.storage import StorageSkill

# Modern agent with full Robutler platform integration
robutler_agent = BaseAgent(
    name="platform-agent",
    instructions="You are a Robutler platform agent with full capabilities",
    
    # Modern model configuration (skill_name/model_name format)
    model="litellm/gpt-4o-mini",  # or "openai/gpt-4o", "anthropic/claude-3-5-sonnet-20241022"
    
    # Skills-based configuration (tools auto-registered via @tool decorators)
    skills={
        # Platform skills
        "payments": PaymentSkill({
        "portal_url": "https://robutler.ai",
        "api_key": "robutler_api_key"
        }),
        "discovery": DiscoverySkill({
            "portal_url": "https://robutler.ai",
            "api_key": "robutler_api_key"
        }),
        "nli": NLISkill({
            "portal_url": "https://robutler.ai", 
            "api_key": "robutler_api_key"
        }),
        "storage": StorageSkill({
            "portal_url": "https://robutler.ai",
            "api_key": "robutler_api_key"
        }),
        
        # Custom business skill with @tool decorators
        "business": CustomBusinessSkill()
    }
    
    # Note: No tools=[] parameter needed - tools auto-registered from skills via @tool decorators
    # Note: Pricing handled by PaymentSkill, context managed by unified Context system
)

# Example custom skill using modern decorator pattern
class CustomBusinessSkill(Skill):
    async def initialize(self, agent: 'BaseAgent') -> None:
        """Initialize skill - tools/hooks auto-registered via decorators!"""
        self.agent = agent
        # No manual registration calls needed!
    
    @tool(scope=["owner"])  # Automatically registered by BaseAgent
    def business_analytics(self, query: str, context: Context = None) -> str:
        """Custom business analytics tool with automatic context injection"""
        if context:
            user_id = context.peer_user_id
            context.track_usage(25, "Business analytics query")
            return f"Analytics for {user_id}: {query} -> [business data]"
        return f"Analytics: {query} -> [business data]"
    
    @hook("on_connection", priority=20, scope=["owner", "admin"])
    async def validate_business_access(self, context: Context) -> Context:
        """Business access validation hook"""
        # Custom business logic
        context.set("business_validated", True)
        return context

# Modern BaseAgent with Robutler platform skills automatically includes:
# - PaymentSkill for billing and token validation with scope-based access control
# - DiscoverySkill for finding other agents via Portal API
# - NLISkill for agent-to-agent communication and handoffs  
# - StorageSkill for Portal data storage and retrieval
# - AuthSkill for JWT validation and user identity management
# - MessagesSkill for conversation tracking and management
# - All tools/hooks auto-registered via @tool/@hook decorators with automatic scope filtering
# - Unified Context system providing access to all request data and agent capabilities
```

### Agent-to-Agent Communication Example

```python
from robutler.agents.skills.nli import NLISkill

# Agent 1: Coding Specialist with modern configuration
coding_agent = BaseAgent(
    name="coding-specialist",
    instructions="You are a Python coding expert",
    model="litellm/gpt-4o-mini",
    skills={
        "nli": NLISkill({
            "portal_url": "https://robutler.ai",
            "api_key": "robutler_api_key"
        }),
        "coding": CodingSkill()  # Custom skill with @tool decorators
    }
)

# Agent 2: UI Design Specialist  
design_agent = BaseAgent(
    name="ui-designer",
    instructions="You are a UI/UX design expert", 
    model="anthropic/claude-3-5-sonnet-20241022", 
    skills={
        "nli": NLISkill({
            "portal_url": "https://robutler.ai",
            "api_key": "robutler_api_key"
        }),
        "design": DesignSkill()  # Custom skill with @tool decorators
    }
)

# Agent 3: Coordinator with modern handoff system
coordinator_agent = BaseAgent(
    name="project-coordinator",
    instructions="""You coordinate software projects by delegating to specialists:
    - Use coding-specialist for programming tasks
    - Use ui-designer for interface design
    - Integrate their work into complete solutions""",
    model="openai/gpt-4o",
    skills={
        "nli": NLISkill({
            "portal_url": "https://robutler.ai", 
            "api_key": "robutler_api_key"
        }),
        "coordination": CoordinatorSkill()  # Custom skill with @handoff decorators
    }
)

# Custom coordinator skill using modern @handoff decorators
class CoordinatorSkill(Skill):
    async def initialize(self, agent: 'BaseAgent') -> None:
        """Initialize - handoffs auto-registered via decorators!"""
        self.agent = agent
    
    @handoff(handoff_type="agent", scope=["owner"])  # Automatically registered
    async def delegate_to_coding_specialist(self, task: str, context: Context = None) -> HandoffResult:
        """Delegate coding tasks to specialist agent"""
        if context:
            context.track_usage(10, "Coding delegation")
        
        # NLI skill handles the actual agent communication
        nli_skill = self.agent.skills["nli"]
        result = await nli_skill.communicate_with_agent(
            agent_name="coding-specialist",
            message=f"Please implement: {task}",
            context=context
        )
        return HandoffResult(result=result, handoff_type="agent")
    
    @handoff(handoff_type="agent", scope=["owner"])
    async def delegate_to_ui_designer(self, design_request: str, context: Context = None) -> HandoffResult:
        """Delegate UI/UX tasks to design specialist"""
        if context:
            context.track_usage(10, "Design delegation")
            
        nli_skill = self.agent.skills["nli"]  
        result = await nli_skill.communicate_with_agent(
            agent_name="ui-designer", 
            message=f"Please design: {design_request}",
            context=context
        )
        return HandoffResult(result=result, handoff_type="agent")

# Usage - coordinator automatically uses handoffs to delegate to specialists  
response = await coordinator_agent.run([
    {"role": "user", "content": "Build a login system with modern UI"}
])

# Coordinator will:
# 1. Use discovery skill to find coding-specialist and ui-designer agents
# 2. Use nli_tool tool to delegate: "Create FastAPI login endpoint"
# 3. Use nli_tool tool to delegate: "Design modern login interface" 
# 4. Coordinate and integrate both responses
# 5. Return complete solution to user
```

---

## 4. Server Deployment Patterns

### Single Agent Server

```python
# server.py - Single agent deployment with modern architecture
import uvicorn
from fastapi import FastAPI, HTTPException
from robutler.agents.core.base_agent import BaseAgent
from robutler.agents.skills.openai import OpenAISkill

# Create modern agent with automatic registration
my_agent = BaseAgent(
    name="my-assistant",
    instructions="You are my personal assistant with comprehensive capabilities",
    model="openai/gpt-4o-mini",  # Modern model format
    skills={
        "assistant": PersonalAssistantSkill()  # Custom skill with @tool/@hook decorators
    }
)

# Custom skill demonstrating modern patterns
class PersonalAssistantSkill(Skill):
    async def initialize(self, agent: 'BaseAgent') -> None:
        """Initialize - capabilities auto-registered via decorators!"""
        self.agent = agent

    @tool  # Automatically registered by BaseAgent
    def schedule_task(self, task: str, date: str, context: Context = None) -> str:
        """Schedule a task with automatic context injection"""
        if context:
            context.track_usage(5, "Task scheduling")
            user_id = context.peer_user_id
            return f"Scheduled '{task}' for {date} for user {user_id}"
        return f"Scheduled '{task}' for {date}"
    
    @hook("on_connection", priority=15)
    async def greeting_hook(self, context: Context) -> Context:
        """Personalized greeting on connection"""
        context.set("greeting_sent", True)
        return context

# Modern FastAPI server 
app = FastAPI(title="Personal Assistant Server", version="2.0")

@app.post("/my-assistant/chat/completions")
async def chat_completions(request: dict):
    """Chat completions with unified context and automatic registration"""
    try:
        if request.get("stream", False):
            return my_agent.run_streaming(
                messages=request["messages"],
                tools=request.get("tools", [])
            )
        else:
            response = await my_agent.run(
                messages=request["messages"],
                tools=request.get("tools", [])
            )
            return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Usage:
# curl -X POST http://localhost:8000/my-assistant/chat/completions \
#   -H "Content-Type: application/json" \
#   -d '{"messages": [{"role": "user", "content": "Schedule a meeting for tomorrow"}]}'
```

### Multi-Agent Server - Modern Architecture

```python
# multi_server.py - Multiple specialized agents with modern architecture
from fastapi import FastAPI, HTTPException, Path
from typing import Dict
import uvicorn
from robutler.agents.core.base_agent import BaseAgent
from robutler.agents.skills.openai import OpenAISkill
from robutler.agents.skills.anthropic import AnthropicSkill
from robutler.agents.skills.google import GoogleSkill  # V2.1

# Modern specialized skills with automatic registration
class CodingSpecialistSkill(Skill):
    async def initialize(self, agent: 'BaseAgent') -> None:
        self.agent = agent

    @tool  # Automatically registered
    def code_review(self, code: str, context: Context = None) -> str:
        """Review code with context injection"""
        if context:
            context.track_usage(20, "Code review")
        return f"Code review completed: {code[:50]}..."
    
    @hook("on_message", priority=10)
    async def optimize_code_output(self, context: Context) -> Context:
        """Optimize code-related outputs"""
        return context

class WritingSpecialistSkill(Skill):
    async def initialize(self, agent: 'BaseAgent') -> None:
        self.agent = agent

    @tool
    def grammar_check(self, text: str, context: Context = None) -> str:
        """Check grammar with automatic context injection"""
        if context:
            context.track_usage(10, "Grammar check")
        return f"Grammar checked: {text[:50]}..."
    
    @hook("on_connection", priority=20, scope=["owner"])
    async def setup_writing_environment(self, context: Context) -> Context:
        """Setup writing environment for owners"""
        context.set("writing_mode", "professional")
        return context

class ResearchSpecialistSkill(Skill):
    async def initialize(self, agent: 'BaseAgent') -> None:
        self.agent = agent

    @tool(scope=["owner", "premium"])  # Premium feature
    def deep_research(self, topic: str, context: Context = None) -> str:
        """Advanced research with scope restrictions"""
        if context:
            context.track_usage(30, "Deep research")
            auth_scope = context.get("auth_scope", "basic")
        return f"Deep research on {topic}: [comprehensive analysis]"

# Create multiple specialized agents with modern patterns
agents_config = {
    "coder": BaseAgent(
        name="coder",
        instructions="You are a coding assistant with code review and optimization capabilities",
        model="openai/gpt-4o",  # Modern model format
        skills={
            "coding": CodingSpecialistSkill()  # Auto-registered tools/hooks
        }
    ),
    "writer": BaseAgent(
        name="writer", 
        instructions="You are a writing assistant with grammar checking and style analysis",
        model="anthropic/claude-3-5-sonnet-20241022",  # Modern model format
        skills={
            "writing": WritingSpecialistSkill()  # Auto-registered tools/hooks
        }
    ),
    "researcher": BaseAgent(
        name="researcher",
        instructions="You are a research assistant with web search and data analysis capabilities",
        model="litellm/gpt-4o",  # LiteLLM routing
        skills={
            "google": GoogleSkill({"api_key": "google-key"}),
            "research": ResearchSpecialistSkill()  # Auto-registered tools/hooks with scoping
        }
    )
}

# Modern FastAPI server with multiple agents
app = FastAPI(title="Multi-Agent Specialist Server", version="2.0")

@app.post("/agents/{agent_name}/chat/completions")
async def multi_agent_chat(
    agent_name: str = Path(..., description="Agent name (coder, writer, researcher)"),
    request: dict = None
):
    """Multi-agent chat completions with unified context"""
    
    # Get the requested agent
    if agent_name not in agents_config:
        raise HTTPException(
            status_code=404, 
            detail=f"Agent '{agent_name}' not found. Available: {list(agents_config.keys())}"
        )
    
    agent = agents_config[agent_name]
    
    try:
        if request.get("stream", False):
            # Streaming with automatic hook execution
            return agent.run_streaming(
                messages=request["messages"],
                tools=request.get("tools", [])
            )
        else:
            # Standard response with automatic hook execution  
            response = await agent.run(
                messages=request["messages"],
                tools=request.get("tools", [])
            )
            return response
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent '{agent_name}' execution failed: {str(e)}")

@app.get("/agents")
async def list_agents():
    """List available agents and their capabilities"""
    agents_info = {}
    for name, agent in agents_config.items():
        agents_info[name] = {
            "name": agent.name,
            "instructions": agent.instructions[:100] + "..." if len(agent.instructions) > 100 else agent.instructions,
            "skills": list(agent.skills.keys()),
            "tools_count": len(agent.get_all_tools()),
            "hooks_count": sum(len(hooks) for hooks in agent._registered_hooks.values())
        }
    return {"agents": agents_info}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Modern multi-agent endpoints with automatic capability registration:
# POST /agents/coder/chat/completions      - Coding specialist with code review tools
# POST /agents/writer/chat/completions     - Writing specialist with grammar tools  
# POST /agents/researcher/chat/completions - Research specialist with premium features
# GET  /agents                             - List all available agents and capabilities
```

### Dynamic Agent Server - Modern Architecture

```python
# dynamic_server.py - Modern dynamic agent creation with full platform integration
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from robutler.agents.core.base_agent import BaseAgent
from robutler.agents.skills.openai import OpenAISkill
from robutler.agents.skills.anthropic import AnthropicSkill
from robutler.agents.skills.google import GoogleSkill  # V2.1
from robutler.agents.skills.database import DatabaseSkill  # V2.1
from robutler.server.context.context_vars import CONTEXT
import uvicorn

# Advanced dynamic agent factory using modern patterns
class DynamicAgentFactory:
    """Factory for creating agents dynamically with full skill integration"""
    
    def __init__(self):
        self._agent_cache: Dict[str, BaseAgent] = {}
        self._agent_configs = {
            "custom-coder": {
                "instructions": "You are a coding assistant with database access and advanced debugging capabilities",
                "model": "openai/gpt-4o",  # Modern model format
                "skills": {
                    "database": DatabaseSkill("postgresql://coding_db"),
                    "coding": CodingSkill()  # Custom skill with @tool decorators
                }
            },
            "custom-writer": {
                "instructions": "You are a writing assistant with research capabilities and style analysis",
                "model": "anthropic/claude-3-5-sonnet-20241022",  # Modern model format
                "skills": {
                    "google": GoogleSkill({"api_key": "google_key"}),
                    "writing": WritingSkill()  # Custom skill with @tool decorators
                }
            },
            "research-specialist": {
                "instructions": "You are a research specialist with comprehensive data access",
                "model": "litellm/gpt-4o",
                "skills": {
                    "google": GoogleSkill({"api_key": "google_key"}),
                    "database": DatabaseSkill("postgresql://research_db"),
                    "research": ResearchSkill()  # Custom skill with @tool and @hook decorators
                }
            }
        }
    
    async def create_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Create or retrieve cached agent with modern architecture"""
        
        # Return cached agent if exists
        if agent_name in self._agent_cache:
            return self._agent_cache[agent_name]
        
        # Check if we have a configuration for this agent
        if agent_name not in self._agent_configs:
            return None
            
        config = self._agent_configs[agent_name]
        
        # Create modern BaseAgent with automatic registration
        agent = BaseAgent(
            name=agent_name,
            instructions=config["instructions"],
            model=config["model"],  # Uses modern skill_name/model_name format
            skills=config["skills"]  # All tools/hooks auto-registered via decorators
        )
        
        # Cache the agent for reuse
        self._agent_cache[agent_name] = agent
        return agent

# Custom skills using modern decorator patterns
class CodingSkill(Skill):
    async def initialize(self, agent: 'BaseAgent') -> None:
        """Initialize - capabilities auto-registered via decorators!"""
        self.agent = agent
    
    @tool(scope=["owner"])  # Automatically registered by BaseAgent
    def debug_code(self, code: str, context: Context = None) -> str:
        """Debug code with automatic context injection and usage tracking"""
        if context:
            context.track_usage(15, "Code debugging")
            user_id = context.peer_user_id
        return f"Debugged code for {user_id if context else 'user'}: {code[:50]}..."
    
    @hook("on_connection", priority=10, scope=["owner"])
    async def setup_coding_environment(self, context: Context) -> Context:
        """Setup coding environment on connection"""
        context.set("coding_environment", "ready")
        return context

class WritingSkill(Skill):
    async def initialize(self, agent: 'BaseAgent') -> None:
        self.agent = agent
    
    @tool  # All users by default
    def analyze_style(self, text: str, context: Context = None) -> str:
        """Analyze writing style with context injection"""
        if context:
            context.track_usage(10, "Style analysis")
        return f"Style analysis: {text[:30]}... [analysis results]"
    
    @hook("on_message", priority=20)
    async def enhance_writing_output(self, context: Context) -> Context:
        """Enhance writing outputs"""
        # Writing enhancement logic
        return context

# Modern FastAPI server with dynamic agents
app = FastAPI(title="Dynamic Agents Server", version="2.0")
agent_factory = DynamicAgentFactory()

@app.post("/agents/{agent_name}/chat/completions")
async def dynamic_chat_completions(agent_name: str, request: dict):
    """Dynamic agent endpoint with unified context and automatic registration"""
    
    # Create or get cached agent
    agent = await agent_factory.create_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    # Execute with unified context system
    try:
        if request.get("stream", False):
            # Return streaming response with automatic hook execution
            return agent.run_streaming(
                messages=request["messages"],
                tools=request.get("tools", [])
        )
    else:
            # Return standard response with automatic hook execution
            response = await agent.run(
                messages=request["messages"],
                tools=request.get("tools", [])
            )
            return response
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

@app.get("/agents/{agent_name}/info")
async def get_agent_info(agent_name: str):
    """Get dynamic agent capabilities and metadata"""
    agent = await agent_factory.create_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    # Return agent capabilities (automatically discovered from skills)
    return {
        "name": agent.name,
        "instructions": agent.instructions,
        "skills": list(agent.skills.keys()),
        "tools": len(agent.get_all_tools()),
        "hooks": sum(len(hooks) for hooks in agent._registered_hooks.values()),
        "handoffs": len(agent.get_all_handoffs())
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Modern dynamic agents available at:
# POST /agents/custom-coder/chat/completions      - Coding assistant with DB access
# POST /agents/custom-writer/chat/completions     - Writing assistant with research
# POST /agents/research-specialist/chat/completions - Full research capabilities
# GET  /agents/{agent_name}/info                  - Agent capabilities and metadata
```

### **Dynamic Agents Architecture Benefits**

The modern dynamic agents system provides several key advantages over static agent deployment:

#### **🚀 Key Features:**
- **✅ On-Demand Creation**: Agents created only when requested, reducing memory usage
- **✅ Intelligent Caching**: Agent instances cached for performance, with configurable TTL
- **✅ Configuration-Driven**: Agent definitions stored as configuration, enabling rapid changes
- **✅ Auto-Discovery**: All capabilities automatically registered via `@tool`, `@hook`, `@handoff` decorators
- **✅ Unified Context**: Full context injection and tracking across all dynamic agents
- **✅ Scope-Based Access**: Different agents can have different permission levels and feature sets
- **✅ Elastic Scaling**: Create agents based on demand patterns, scale up/down as needed

#### **🏗️ Architecture Integration:**

```python
# Dynamic agents fully integrate with Robutler V2 architecture:
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │    │  DynamicAgent    │    │   BaseAgent     │
│   Endpoints     │───▶│   Factory        │───▶│   (Modern)      │
├─────────────────┤    ├──────────────────┤    ├─────────────────┤
│ /agents/{name}  │    │ • Configuration  │    │ • Unified       │
│ /completions    │    │ • Caching        │    │   Context       │
│ /info           │    │ • Validation     │    │ • Auto-Reg      │
└─────────────────┘    └──────────────────┘    │ • Scope Control │
                                               └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │   Skills with   │
                                               │   @decorators   │
                                               ├─────────────────┤
                                               │ @tool           │
                                               │ @hook           │
                                               │ @handoff        │
                                               └─────────────────┘
```

#### **🎯 Use Cases:**

1. **Multi-Tenant SaaS**: Different agents per customer/organization
2. **Specialized Services**: Domain-specific agents created on-demand  
3. **A/B Testing**: Multiple agent variants with different configurations
4. **Resource Optimization**: Agents created/destroyed based on usage patterns
5. **Development/Staging**: Different agent configurations per environment

#### **📊 Performance Benefits:**

```python
# Memory usage comparison:
Static Deployment:  [Agent1][Agent2][Agent3][Agent4] = 400MB constant
Dynamic Deployment: [Factory] + [ActiveAgent] = 50MB + 100MB per active = 150MB typical

# Scaling benefits:
- Create 100s of agent configurations without memory impact
- Scale active agents based on real demand
- Efficient resource utilization in cloud environments
```

#### **🔧 Implementation Patterns:**

```python
# 1. Database-Driven Dynamic Agents
class DatabaseDynamicAgentFactory:
    async def create_agent(self, agent_name: str) -> BaseAgent:
        # Fetch agent config from database
        config = await self.db.get_agent_config(agent_name)
        return BaseAgent(**config)

# 2. Portal Integration Dynamic Agents  
class PortalDynamicAgentFactory:
    async def create_agent(self, agent_name: str) -> BaseAgent:
        # Fetch from Robutler Portal API
        config = await self.portal_api.get_agent(agent_name)
        return BaseAgent(**config)

# 3. Environment-Based Dynamic Agents
class EnvironmentDynamicAgentFactory:
    async def create_agent(self, agent_name: str) -> BaseAgent:
        # Different configs per environment
        env = os.getenv("ENVIRONMENT", "development")
        config = self.configs[env].get(agent_name)
        return BaseAgent(**config) if config else None
```

**Result**: Dynamic agents provide **maximum flexibility** with **optimal resource usage** while maintaining full compatibility with Robutler V2's unified architecture! 🎯

---

## 5. Production Deployment

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run server
CMD ["uvicorn", "server:server.app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  robutler-agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ROBUTLER_API_URL=${ROBUTLER_API_URL}
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - postgres
      - milvus
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: robutler
      POSTGRES_USER: robutler
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  milvus:
    image: milvusdb/milvus:v2.3.0
    ports:
      - "19530:19530"
    volumes:
      - milvus_data:/var/lib/milvus

volumes:
  postgres_data:
  milvus_data:
```

### Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: robutler-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: robutler-agent
  template:
    metadata:
      labels:
        app: robutler-agent
    spec:
      containers:
      - name: agent
        image: robutler/agent:v2.0
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: agent-secrets
              key: openai-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi" 
            cpu: "500m"

---
apiVersion: v1
kind: Service
metadata:
  name: robutler-agent-service
spec:
  selector:
    app: robutler-agent
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## 6. Client Integration Examples

### Python Client

```python
# python_client.py
import httpx
import asyncio
import json

class RobutlerClient:
    def __init__(self, base_url: str, payment_token: str = None):
        self.base_url = base_url
        self.payment_token = payment_token
    
    async def chat(self, agent_name: str, messages: list, stream: bool = False):
        """Chat with an agent"""
        url = f"{self.base_url}/{agent_name}/chat/completions"
        headers = {"Content-Type": "application/json"}
        
        if self.payment_token:
            headers["X-Payment-Token"] = self.payment_token
        
        payload = {
            "messages": messages,
            "stream": stream
        }
        
        async with httpx.AsyncClient() as client:
            if stream:
                async with client.stream("POST", url, json=payload, headers=headers) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: "
                            if data == "[DONE]":
                                break
                            yield json.loads(data)
            else:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()

# Usage
async def main():
    client = RobutlerClient("http://localhost:8000")
    
    # Non-streaming
    response = await client.chat("my-assistant", [
        {"role": "user", "content": "Hello, how are you?"}
    ])
    print(response["choices"][0]["message"]["content"])
    
    # Streaming
    async for chunk in client.chat("my-assistant", [
        {"role": "user", "content": "Tell me a story"}
    ], stream=True):
        if "choices" in chunk:
            content = chunk["choices"][0].get("delta", {}).get("content", "")
            if content:
                print(content, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
```

### JavaScript Client

```javascript
// js_client.js
class RobutlerClient {
    constructor(baseUrl, paymentToken = null) {
        this.baseUrl = baseUrl;
        this.paymentToken = paymentToken;
    }
    
    async chat(agentName, messages, stream = false) {
        const url = `${this.baseUrl}/${agentName}/chat/completions`;
        const headers = {'Content-Type': 'application/json'};
        
        if (this.paymentToken) {
            headers['X-Payment-Token'] = this.paymentToken;
        }
        
        const payload = { messages, stream };
        
        if (stream) {
            return this.streamChat(url, payload, headers);
        } else {
            const response = await fetch(url, {
                method: 'POST',
                headers,
                body: JSON.stringify(payload)
            });
            return response.json();
        }
    }
    
    async *streamChat(url, payload, headers) {
        const response = await fetch(url, {
            method: 'POST',
            headers,
            body: JSON.stringify(payload)
        });
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.substring(6);
                    if (data === '[DONE]') return;
                    
                    try {
                        yield JSON.parse(data);
                    } catch (e) {
                        // Skip malformed JSON
                    }
                }
            }
        }
    }
}

// Usage
async function main() {
    const client = new RobutlerClient('http://localhost:8000');
    
    // Non-streaming
    const response = await client.chat('my-assistant', [
        {role: 'user', content: 'Hello, how are you?'}
    ]);
    console.log(response.choices[0].message.content);
    
    // Streaming
    for await (const chunk of client.chat('my-assistant', [
        {role: 'user', content: 'Tell me a story'}
    ], true)) {
        const content = chunk.choices?.[0]?.delta?.content;
        if (content) {
            process.stdout.write(content);
        }
    }
}

main().catch(console.error);
```

---

## 7. Workflow Orchestration

### Multi-Step Research Workflow

```python
from robutler.agents.workflows.decorators import workflow
from robutler.agents.workflows.context import WorkflowContext

@workflow(
    name="comprehensive_research",
    dependencies=["google", "robutler.storage", "openai", "database"],
    version="1.0"
)
async def comprehensive_research_workflow(
    workflow_context: WorkflowContext, 
    topic: str, 
    depth: str = "comprehensive"
) -> dict:
    """
    Multi-step research workflow:
    1. Initial search and information gathering
    2. Analysis and synthesis with specialized LLM
    3. Storage of findings for future reference
    4. Database storage of structured results
    """
    
    # Get required skills from workflow context
    google_skill = workflow_context.get_dependency("google")
    storage_skill = workflow_context.get_dependency("robutler.storage")
    openai_skill = workflow_context.get_dependency("openai")
    database_skill = workflow_context.get_dependency("database")
    
    results = {}
    
    # Step 1: Initial research
    workflow_context.log(f"Starting research on: {topic}")
    
    search_queries = [
        f"{topic} overview guide",
        f"{topic} best practices", 
        f"{topic} recent developments 2024",
        f"{topic} expert analysis"
    ]
    
    all_search_results = []
    for query in search_queries:
        search_result = await google_skill.google_search(query, max_results=10)
        all_search_results.append(search_result)
    
    results["raw_research"] = all_search_results
    
    # Step 2: Analysis with specialized LLM
    workflow_context.log("Analyzing research findings...")
    
    combined_research = "\n\n".join(all_search_results)
    analysis_prompt = f"""
    Analyze the following research on {topic} and provide:
    1. Key insights and themes
    2. Important trends and developments  
    3. Practical recommendations
    4. Areas needing further research
    
    Research data:
    {combined_research[:10000]}  # Limit for context window
    """
    
    analysis = await openai_skill.query_openai(
        "gpt-4",
        [{"role": "system", "content": analysis_prompt}]
    )
    
    results["analysis"] = analysis
    
    # Step 3: Store in Robutler Portal
    workflow_context.log("Storing findings in portal...")
    
    research_package = {
        "topic": topic,
        "depth": depth,
        "raw_research": all_search_results,
        "analysis": analysis,
        "timestamp": datetime.utcnow().isoformat(),
        "workflow_version": "1.0"
    }
    
    storage_key = f"research_{topic.replace(' ', '_')}_{int(time.time())}"
    await storage_skill.store_data(storage_key, research_package)
    
    results["storage_key"] = storage_key
    
    # Step 4: Store structured results in database
    workflow_context.log("Storing structured results in database...")
    
    await database_skill.db_insert("research_reports", {
        "topic": topic,
        "analysis_summary": analysis[:500],  # Truncated for DB
        "storage_reference": storage_key,
        "depth": depth,
        "created_at": datetime.utcnow().isoformat()
    })
    
    workflow_context.log(f"Research workflow completed for: {topic}")
    
    return {
        "status": "completed",
        "topic": topic,
        "storage_key": storage_key,
        "summary": f"Comprehensive research completed on {topic}",
        "next_steps": "Access findings using storage key or query database"
    }

# Usage in agent
research_agent = BaseAgent(
    name="research-agent",
    instructions="You can conduct comprehensive research using workflows",
    skills={
        "google": GoogleSkill({"api_key": "..."}),
        "robutler.storage": StorageSkill({"portal_url": "...", "api_key": "..."}),
        "openai": OpenAISkill({"api_key": "..."}),
        "database": DatabaseSkill("postgresql://...")
    },
    workflows=[comprehensive_research_workflow]
)
```

---

## 8. Error Handling and Resilience

### Robust Error Handling

```python
from robutler.agents.core.base_agent import BaseAgent
from robutler.agents.skills.base import Skill
from robutler.agents.tools.decorators import tool
import asyncio
import logging
import httpx

logger = logging.getLogger(__name__)

# Custom resilient web skill using modern decorator pattern
class ResilientWebSkill(Skill):
    async def initialize(self, agent: 'BaseAgent') -> None:
        """Initialize - tools auto-registered via decorators!"""
        self.agent = agent

    @tool  # Automatically registered by BaseAgent
    async def resilient_web_request(self, url: str, retries: int = 3, context: Context = None) -> str:
        """Make web request with retries and error handling, plus context injection"""
        
        if context:
            user_id = context.peer_user_id
            context.track_usage(10, f"Web request to {url}")
            logger.info(f"Web request for user {user_id}: {url}")
    
    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.text[:1000]  # Limit response size
                
        except httpx.TimeoutException:
            logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
            if attempt == retries - 1:
                return f"Request to {url} timed out after {retries} attempts"
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
        except httpx.HTTPError as e:
            logger.warning(f"HTTP error on attempt {attempt + 1} for {url}: {e}")
            if attempt == retries - 1:
                return f"HTTP error for {url}: {str(e)}"
            await asyncio.sleep(2 ** attempt)
            
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
            return f"Unexpected error for {url}: {str(e)}"

# Agent with error handling using modern skill-based pattern
resilient_agent = BaseAgent(
    name="resilient-agent",
    instructions="You are a resilient agent that handles errors gracefully",
    model="openai/gpt-4o-mini",
    skills={
        "web": ResilientWebSkill()  # Tools auto-registered from skill decorators
    }
    # Note: No tools=[] parameter needed - tools auto-registered via @tool decorators
)
```

---

## Summary

Chapter 5 provides comprehensive integration and usage examples using modern Robutler V2 patterns:

✅ **Modern Agent Configurations** - BaseAgent with skill-based architecture and `skill_name/model_name` format  
✅ **Automatic Decorator Registration** - All examples use `@tool`, `@hook`, and `@handoff` decorators with auto-registration  
✅ **Unified Context System** - Examples show context injection and unified Context usage throughout  
✅ **Robutler Platform Integration** - Complete platform integration with modern skill-based configuration  
✅ **Advanced Integration Patterns** - Full-featured agents with automatic capability discovery  
✅ **Server Deployment Patterns** - Single, multi-agent, and dynamic deployments with modern FastAPI architecture  
✅ **Dynamic Agents Architecture** - Comprehensive coverage of on-demand agent creation, caching, scaling, and resource optimization  
✅ **Production Deployment** - Docker and Kubernetes configuration for modern agent system  
✅ **Client Integration Examples** - Python and JavaScript client implementations  
✅ **Workflow Orchestration** - Complex multi-step workflows using `@handoff` decorators  
✅ **Error Handling and Resilience** - Production-ready patterns with context injection and automatic registration  

**Next**: [Chapter 6: Implementation Guide](./ROBUTLER_V2_DESIGN_Ch6_Implementation_Guide.md) - Testing, migration, and deployment guidance 