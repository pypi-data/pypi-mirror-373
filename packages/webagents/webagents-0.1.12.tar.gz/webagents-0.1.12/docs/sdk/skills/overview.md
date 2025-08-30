# Skills Overview

Skills are the fundamental building blocks of Robutler agents, providing modular capabilities that go far beyond simple tool integration. Unlike plain tools, skills bundle prompts, hooks, tools, and handoffs into cohesive modules that are easy to test and reuse.

## What Are Skills?

Skills are comprehensive agent capabilities that encapsulate:

- **Custom Logic** - Domain-specific reasoning and decision-making
- **Tools** - Executable functions via `@tool` decorator
- **Hooks** - Lifecycle event handlers via `@hook` decorator  
- **Handoffs** - Agent routing via `@handoff` decorator
- **Prompts** - Skill-specific instructions for the LLM
- **Dependencies** - Automatic inclusion of required skills

## Why Skills > MCP

While Model Context Protocol (MCP) provides basic tool integration, Robutler skills offer:

1. **Prompts** - Guide LLM behavior with skill-specific instructions
2. **Lifecycle Hooks** - React to events during request processing
3. **Handoffs** - Enable seamless multi-agent workflows
4. **Dependencies** - Automatically resolve required capabilities
5. **Custom Logic** - Implement complex business logic beyond tools
6. **Community Ecosystem** - Share and reuse skills

## Skill Categories

### Core Skills

Essential functionality auto-included in most agents:

```python
# LLM Skills - Language model providers
from robutler.agents.skills import OpenAISkill, AnthropicSkill, LiteLLMSkill

# Memory Skills - Conversation persistence  
from robutler.agents.skills import ShortTermMemorySkill, LongTermMemorySkill, VectorMemorySkill

# MCP Skill - Model Context Protocol integration
from robutler.agents.skills import MCPSkill
```

### Platform Skills

Robutler platform integration:

```python
# Multi-agent communication
from robutler.agents.skills import NLISkill

# Agent discovery
from robutler.agents.skills import DiscoverySkill

# Authentication & payments
from robutler.agents.skills import AuthSkill, PaymentSkill

# Storage & messaging
from robutler.agents.skills import StorageSkill, MessagesSkill
```

### Extra Skills

Domain-specific capabilities:

```python
# External services
from robutler.agents.skills import GoogleSkill, DatabaseSkill, FilesystemSkill

# Workflow automation
from robutler.agents.skills import CrewAISkill, N8NSkill, ZapierSkill
```

## Creating a Skill

### Basic Structure

```python
from robutler.agents.skills import Skill
from robutler.agents.tools.decorators import tool
from robutler.agents.skills.decorators import hook, handoff

class MySkill(Skill):
    def __init__(self, config=None):
        super().__init__(
            config=config,
            scope="all",  # Access control: all/owner/admin
            dependencies=["memory"]  # Required skills
        )
    
    def get_prompts(self) -> List[str]:
        """Provide skill-specific instructions"""
        return [
            "You have access to custom functionality.",
            "Always validate inputs before processing."
        ]
    
    @tool
    def my_tool(self, param: str) -> str:
        """Tool automatically registered with agent"""
        return f"Processed: {param}"
    
    @hook("on_message")
    async def process_message(self, context):
        """Hook automatically called on each message"""
        # Custom logic
        return context
    
    @handoff("expert-agent")
    def needs_expert(self, query: str) -> bool:
        """Handoff automatically triggered when True"""
        return "expert" in query
```

## Using Skills

### Adding to Agents

```python
from robutler.agents import BaseAgent

agent = BaseAgent(
    name="my-agent",
    model="openai/gpt-4o",
    skills={
        "custom": MySkill({"api_key": "..."}),
        "memory": ShortTermMemorySkill(),
        "discovery": DiscoverySkill()
    }
)
```

### Skill Dependencies

```python
class DependentSkill(Skill):
    def __init__(self, config=None):
        super().__init__(
            config=config,
            dependencies=["memory", "auth", "nli"]
        )
    
    # Memory, auth, and nli skills auto-included
```

### Dynamic Capabilities

```python
class AdaptiveSkill(Skill):
    @hook("on_connection")
    async def adapt_to_user(self, context):
        """Register capabilities based on context"""
        
        user_type = context.get("user_type", "basic")
        
        if user_type == "premium":
            # Register premium tools
            self.register_tool(self.premium_analysis)
            self.register_tool(self.advanced_export)
        
        if user_type == "developer":
            # Register developer tools
            self.register_tool(self.code_generator)
            self.register_tool(self.api_tester)
        
        return context
```

## Skill Lifecycle

```mermaid
graph TD
    Init[Skill.__init__] --> Agent[Agent Creation]
    Agent --> Initialize[skill.initialize(agent)]
    Initialize --> Register[Register tools/hooks/handoffs]
    Register --> Ready[Skill Ready]
    
    Request[Incoming Request] --> Connection[on_connection hooks]
    Connection --> Message[on_message hooks]
    Message --> Tools{Tool calls?}
    Tools -->|Yes| BeforeTool[before_toolcall hooks]
    BeforeTool --> Execute[Execute tool]
    Execute --> AfterTool[after_toolcall hooks]
    
    Message --> Handoff{Handoff needed?}
    Handoff -->|Yes| BeforeHandoff[before_handoff hooks]
    BeforeHandoff --> RouteAgent[Route to agent]
    RouteAgent --> AfterHandoff[after_handoff hooks]
    
    Tools --> Response[Generate response]
    Handoff --> Response
    Response --> Chunks[on_chunk hooks]
    Chunks --> Finalize[finalize_connection hooks]
```

> Finalize hooks run for cleanup even if a structured error was raised earlier (for example, a 402 payment/auth error). Keep finalize handlers idempotent.

## Skill Patterns

### Stateful Skills

```python
class StatefulSkill(Skill):
    def __init__(self, config=None):
        super().__init__(config)
        self.session_data = {}
    
    @hook("on_connection")
    async def init_session(self, context):
        """Initialize session state"""
        session_id = context.completion_id
        self.session_data[session_id] = {
            "start_time": time.time(),
            "actions": []
        }
        return context
    
    @tool
    def track_action(self, action: str) -> str:
        """Track user actions in session"""
        context = self.get_context()
        session_id = context.completion_id
        
        if session_id in self.session_data:
            self.session_data[session_id]["actions"].append(action)
            return f"Tracked action: {action}"
        
        return "No active session"
```

### Composable Skills

```python
class CompositeSkill(Skill):
    """Skill that combines other skills"""
    
    def __init__(self, config=None):
        super().__init__(config)
        
        # Compose functionality
        self.analyzer = AnalyzerSkill()
        self.reporter = ReporterSkill()
    
    @tool
    async def full_analysis(self, data: str) -> Dict:
        """Combine multiple skill capabilities"""
        
        # Use analyzer skill
        analysis = await self.analyzer.analyze(data)
        
        # Use reporter skill
        report = await self.reporter.generate_report(analysis)
        
        return {
            "analysis": analysis,
            "report": report
        }
```

### Extensible Skills

```python
class PluginSkill(Skill):
    """Skill with plugin system"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.plugins = {}
    
    def register_plugin(self, name: str, plugin):
        """Register a plugin"""
        self.plugins[name] = plugin
        
        # Register plugin tools
        for method_name in dir(plugin):
            method = getattr(plugin, method_name)
            if hasattr(method, "_is_tool"):
                self.register_tool(method)
    
    @tool
    def list_plugins(self) -> List[str]:
        """List available plugins"""
        return list(self.plugins.keys())
```

## Best Practices

1. **Single Responsibility** - Each skill should have one clear purpose
2. **Clear Dependencies** - Explicitly declare required skills
3. **Proper Scoping** - Use appropriate access control levels
4. **Error Handling** - Skills should handle errors gracefully
5. **Documentation** - Provide clear prompts and docstrings
6. **Testing** - Skills should be independently testable

## Next Steps

- [Prompts](prompts.md) - Guide LLM behavior with skill prompts
- [Tools](tools.md) - Add executable functions to skills
- [Hooks](hooks.md) - React to lifecycle events
- [Handoffs](handoffs.md) - Enable multi-agent workflows
- [Dependencies](dependencies.md) - Manage skill relationships
- [Creating Custom Skills](custom.md) - Build your own skills 