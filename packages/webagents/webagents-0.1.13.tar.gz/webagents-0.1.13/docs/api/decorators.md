# Decorators API Reference

## Overview

Robutler provides three main decorators for automatic registration of agent capabilities: `@tool`, `@hook`, `@prompt`, and `@handoff`. These decorators enable clean, declarative definition of agent functionality with automatic discovery and registration.

## @tool Decorator

The `@tool` decorator marks functions as tools available to AI agents, with automatic OpenAI-compatible schema generation.

### Syntax

```python
@tool(name: Optional[str] = None, 
      description: Optional[str] = None, 
      scope: Union[str, List[str]] = "all")
def tool_function(param1: type, param2: type = default) -> return_type:
    """Tool description (used if description not provided)"""
    pass
```

### Parameters

- **`name`**: Override tool name (defaults to function name)
- **`description`**: Tool description (defaults to docstring)
- **`scope`**: Access control - `"all"`, `"owner"`, `"admin"`, or list of scopes

### Example

```python
@tool(description="Calculate mathematical expressions", scope="all")
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely."""
    try:
        result = eval(expression)  # Use ast.literal_eval in production
        return str(result)
    except Exception as e:
        return f"Error: {e}"
```

## @hook Decorator

The `@hook` decorator marks functions as lifecycle hooks that execute at specific points in the agent execution cycle.

### Syntax

```python
@hook(event: str, 
      priority: int = 50, 
      scope: Union[str, List[str]] = "all")
def hook_function(context: Context) -> Context:
    pass
```

### Parameters

- **`event`**: Lifecycle event name
- **`priority`**: Execution priority (higher numbers execute first)
- **`scope`**: Access control - `"all"`, `"owner"`, `"admin"`, or list of scopes

### Available Events

- `"on_connection"`: User connection setup
- `"on_chunk"`: Streaming chunk processing
- `"on_message"`: Complete message processing
- `"before_toolcall"`: Before tool execution
- `"after_toolcall"`: After tool execution
- `"before_handoff"`: Before agent handoff
- `"after_handoff"`: After agent handoff
- `"finalize_connection"`: Connection cleanup

### Example

```python
@hook("on_connection", priority=10, scope="owner")
async def setup_user_context(context: Context) -> Context:
    """Set up user-specific context on connection."""
    user_id = context.get('user_id')
    if user_id:
        user_data = await get_user_data(user_id)
        context.set('user_data', user_data)
    return context
```

## @prompt Decorator

The `@prompt` decorator marks functions as system prompt providers that contribute dynamic content to the system message before LLM execution.

### Syntax

```python
@prompt(priority: int = 50, 
        scope: Union[str, List[str]] = "all")
def prompt_function(context: Context) -> str:
    pass
```

### Parameters

- **`priority`**: Execution priority (lower numbers execute first)
- **`scope`**: Access control - `"all"`, `"owner"`, `"admin"`, or list of scopes

### Execution Flow

1. Prompt functions execute in priority order (ascending)
2. String outputs are combined with double newlines
3. Combined content is added to the system message
4. If no system message exists, one is created with agent instructions + prompts

### Example

```python
@prompt(priority=10)
def system_status_prompt(context: Context) -> str:
    """Add current system status to the prompt."""
    return f"System Status: {get_system_status()}"

@prompt(priority=20, scope="owner")
def user_context_prompt(context: Context) -> str:
    """Add user-specific context for owners."""
    user_id = getattr(context, 'user_id', 'anonymous')
    return f"Current User: {user_id}"

@prompt(priority=5)
async def time_prompt(context: Context) -> str:
    """Add current timestamp."""
    from datetime import datetime
    return f"Current Time: {datetime.now().isoformat()}"
```

### Enhanced System Message

```
You are a helpful AI assistant.

System Status: Online - All services operational

Current User: john_smith

Current Time: 2024-07-22T14:30:15Z
```

## @handoff Decorator

The `@handoff` decorator marks functions as handoff handlers for transferring conversations to other agents or services.

### Syntax

```python
@handoff(name: Optional[str] = None,
         handoff_type: str = "agent",
         description: Optional[str] = None,
         scope: Union[str, List[str]] = "all")
def handoff_function(context: Context) -> HandoffResult:
    pass
```

### Parameters

- **`name`**: Handoff name (defaults to function name)
- **`handoff_type`**: Type of handoff - `"agent"`, `"human"`, `"service"`
- **`description`**: Handoff description (defaults to docstring)
- **`scope`**: Access control - `"all"`, `"owner"`, `"admin"`, or list of scopes

### Example

```python
from robutler.agents.skills.base import HandoffResult

@handoff(handoff_type="human", scope="owner")
async def escalate_to_support(issue: str, context: Context) -> HandoffResult:
    """Escalate complex issues to human support."""
    ticket_id = await create_support_ticket(issue, context.user_id)
    return HandoffResult(
        result=f"Created support ticket: {ticket_id}",
        handoff_type="human",
        success=True,
        metadata={"ticket_id": ticket_id}
    )
```

## Context Injection

All decorators support automatic context injection. If a decorated function has a `context` parameter, the current request context is automatically injected:

```python
@tool
def context_aware_tool(query: str, context: Context = None) -> str:
    """Tool with automatic context injection."""
    if context:
        user_id = context.get('user_id', 'anonymous')
        return f"Query '{query}' from user {user_id}"
    return f"Query: {query}"

@prompt
def context_aware_prompt(context: Context) -> str:
    """Prompt with automatic context injection."""
    return f"Request ID: {context.get('request_id', 'unknown')}"
```

## Scope-Based Access Control

All decorators support scope-based access control:

### Scope Hierarchy

- **`"all"`**: Available to all users (level 1)
- **`"owner"`**: Available to owners and above (level 2) 
- **`"admin"`**: Available to admins only (level 3)

### Scope Lists

```python
@tool(scope=["owner", "admin"])
def privileged_tool() -> str:
    """Available to owners and admins only."""
    return "Privileged data"

@prompt(scope=["admin"])
def debug_prompt(context: Context) -> str:
    """Debug info for admins only."""
    return f"Debug: Server load {get_server_load()}%"
```

## Automatic Registration

All decorated functions are automatically discovered and registered when skills are initialized:

```python
class MySkill(Skill):
    async def initialize(self, agent: BaseAgent):
        """Skills are automatically registered - no manual calls needed!"""
        self.agent = agent
        # @tool, @hook, @prompt, and @handoff functions are auto-discovered
    
    @tool
    def my_tool(self, param: str) -> str:
        return f"Processed: {param}"
    
    @hook("on_connection")
    async def setup(self, context: Context) -> Context:
        return context
    
    @prompt(priority=10)
    def my_prompt(self, context: Context) -> str:
        return "Additional context"
    
    @handoff
    async def escalate(self, context: Context) -> HandoffResult:
        return HandoffResult(result="Escalated", handoff_type="agent")
```

## Error Handling

All decorators include error handling:

- **Tools**: Return error messages on execution failure
- **Hooks**: Log errors but continue execution
- **Prompts**: Log errors but continue with other prompts
- **Handoffs**: Return failed HandoffResult on errors

This ensures system resilience and prevents single failures from breaking agent functionality. 