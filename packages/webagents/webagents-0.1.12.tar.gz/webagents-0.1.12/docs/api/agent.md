# BaseAgent

The core agent implementation with automatic decorator registration, unified context management, and comprehensive tool/hook/handoff execution.

## Overview

BaseAgent provides a unified framework for creating AI agents with:
- **Automatic decorator registration** (@tool, @hook, @handoff, @prompt)
- **Unified context management** across all operations
- **Streaming and non-streaming execution**
- **Scope-based access control** (all, owner, admin)
- **Comprehensive tool/handoff execution**
- **OpenAI-compatible tool call handling**

## Constructor

```python
BaseAgent(
    name: str,
    instructions: str = "",
    model: Optional[Union[str, Any]] = None,
    skills: Optional[Dict[str, Skill]] = None,
    scope: str = "all"
)
```

### Parameters

- **`name`**: Agent identifier
- **`instructions`**: System instructions for the agent
- **`model`**: LLM model specification or skill instance
- **`skills`**: Dictionary of skill instances
- **`scope`**: Default access scope for the agent

### Model Parameter Processing

The `model` parameter supports automatic LLM skill creation:

```python
# String format: "skill_type/model_name"
agent = BaseAgent(
    name="my-agent",
    model="openai/gpt-4o"  # Creates OpenAISkill automatically
)

# Supported formats:
# - "openai/gpt-4o" → OpenAISkill
# - "litellm/gpt-4o" → LiteLLMSkill  
# - "anthropic/claude-3" → AnthropicSkill
```

## Core Features

### Automatic Decorator Registration

BaseAgent automatically discovers and registers decorated methods from skills:

```python
class MySkill(Skill):
    @tool
    def my_tool(self, param: str) -> str:
        """Tool description"""
        return f"Result: {param}"
    
    @hook("on_connection", priority=10)
    async def setup_context(self, context):
        """Setup context on connection"""
        return context
    
    @handoff(target="external-service")
    async def handoff_to_service(self, data: dict):
        """Handoff to external service"""
        pass
    
    @prompt(priority=50)
    def system_prompt(self) -> str:
        """Provide system prompt"""
        return "You are a helpful assistant."
```

### Context Management

Unified context flows through all operations:

```python
# Context is automatically created and managed
context = create_context(messages=messages, stream=stream)
context.update_agent_context(self)
set_context(context)

# Access context in any operation
current_context = get_context()
```

## Registration Methods

### Tool Registration

```python
def register_tool(
    self, 
    tool_func: Callable, 
    source: str = "manual", 
    scope: Union[str, List[str]] = None
)
```

**Example:**
```python
@tool(scope="owner")
def admin_function(self, action: str) -> str:
    return f"Admin action: {action}"

agent.register_tool(admin_function, source="custom_skill")
```

### Hook Registration

```python
def register_hook(
    self, 
    event: str, 
    handler: Callable, 
    priority: int = 50, 
    source: str = "manual", 
    scope: Union[str, List[str]] = None
)
```

**Available Events:**
- `"on_connection"`: User connection setup
- `"on_chunk"`: Streaming chunk processing  
- `"on_message"`: Complete message processing
- `"before_toolcall"`: Before tool execution
- `"after_toolcall"`: After tool execution
- `"finalize_connection"`: Connection cleanup

**Example:**
```python
@hook("on_connection", priority=10)
async def validate_user(self, context):
    """Validate user on connection"""
    user_id = context.get("user_id")
    if not user_id:
        raise ValueError("User ID required")
    return context
```

### Handoff Registration

```python
def register_handoff(
    self, 
    handoff_config: Handoff, 
    source: str = "manual"
)
```

**Example:**
```python
@handoff(target="payment-service", handoff_type="service")
async def process_payment(self, amount: float):
    """Handoff to payment processing"""
    pass
```

### Prompt Registration

```python
def register_prompt(
    self, 
    prompt_func: Callable, 
    priority: int = 50, 
    source: str = "manual", 
    scope: Union[str, List[str]] = None
)
```

**Example:**
```python
@prompt(priority=50)
def memory_context(self) -> str:
    """Add memory context to prompts"""
    return f"Previous conversation: {self.get_memory()}"
```

## Execution Methods

### Non-Streaming Execution

```python
async def run(
    self,
    messages: List[Dict[str, Any]],
    tools: Optional[List[Dict[str, Any]]] = None,
    stream: bool = False,
    **kwargs
) -> Dict[str, Any]
```

**Execution Flow:**
1. Create and set context
2. Initialize skills with agent reference
3. Execute `on_connection` hooks
4. Merge external tools with agent tools
5. Enhance messages with dynamic prompts
6. Call LLM skill for completion
7. Handle tool calls (multi-turn conversation)
8. Execute `on_message` hooks
9. Execute `finalize_connection` hooks

**Example:**
```python
messages = [{"role": "user", "content": "Calculate 2 + 2"}]
response = await agent.run(messages=messages)

# With external tools
external_tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather for location",
        "parameters": {...}
    }
}]
response = await agent.run(messages=messages, tools=external_tools)
```

### Streaming Execution

```python
async def run_streaming(
    self,
    messages: List[Dict[str, Any]],
    tools: Optional[List[Dict[str, Any]]] = None,
    **kwargs
) -> AsyncGenerator[Dict[str, Any], None]
```

**Example:**
```python
async for chunk in agent.run_streaming(messages=messages):
    print(chunk.choices[0].delta.content, end="")
```

## Tool Execution

### Internal vs External Tools

BaseAgent distinguishes between internal (agent) tools and external (client) tools:

```python
# Internal tools (@tool decorated functions) - executed server-side
@tool
def calculate(self, expression: str) -> str:
    return str(eval(expression))

# External tools (from request) - returned to client for execution
external_tools = [{
    "type": "function", 
    "function": {"name": "get_weather", ...}
}]
```

### Tool Call Handling

```python
async def _handle_tool_calls(
    self, 
    llm_response: Dict[str, Any], 
    messages: List[Dict[str, Any]]
) -> Dict[str, Any]
```

**Flow:**
1. Extract tool calls from LLM response
2. Check if tools should be executed server-side
3. Execute agent tools with hooks
4. Return external tools to client
5. Continue conversation with tool results

## Scope-Based Access Control

### Scope Hierarchy

```python
scope_hierarchy = {
    "admin": 3,    # Highest access
    "owner": 2,    # Medium access  
    "all": 1       # Basic access
}
```

### Scope Filtering

```python
def get_tools_for_scope(self, auth_scope: str) -> List[Dict[str, Any]]
def get_prompts_for_scope(self, auth_scope: str) -> List[Dict[str, Any]]
```

**Example:**
```python
# Owner can access owner and all tools
owner_tools = agent.get_tools_for_scope("owner")

# Admin can access all tools
admin_tools = agent.get_tools_for_scope("admin")
```

## Hook Execution

### Hook Lifecycle

```python
async def _execute_hooks(self, event: str, context: Context) -> Context
```

**Hook Execution Order:**
1. Hooks sorted by priority (higher priority first)
2. Each hook receives and can modify context
3. Errors in hooks don't stop execution
4. Modified context passed to next hook

## Prompt Enhancement

### Dynamic Prompt System

```python
async def _enhance_messages_with_prompts(
    self, 
    messages: List[Dict[str, Any]], 
    context: Context
) -> List[Dict[str, Any]]
```

**Features:**
- Executes all prompt providers for current scope
- Combines prompts with system message
- Creates system message if none exists
- Maintains message order and structure

## Context Management

### Context Creation

```python
context = create_context(
    messages=messages,
    stream=stream
)
context.update_agent_context(self)
set_context(context)
```

### Context Access

```python
# Get current context
context = get_context()

# Set context values
context.set("key", "value")

# Get context values  
value = context.get("key", "default")
```

## Complete Example

```python
from robutler.agents import BaseAgent
from robutler.agents.skills import Skill, tool, hook, handoff, prompt

class CalculatorSkill(Skill):
    @tool(scope="all")
    def add(self, a: float, b: float) -> float:
        """Add two numbers"""
        return a + b
    
    @hook("on_connection", priority=10)
    async def setup_calculator(self, context):
        """Setup calculator context"""
        context.set("calculator_mode", "standard")
        return context
    
    @prompt(priority=50)
    def calculator_prompt(self) -> str:
        """Add calculator instructions"""
        return "You are a calculator assistant. Use the add tool for calculations."

class PaymentSkill(Skill):
    @tool(scope="owner")
    def process_payment(self, amount: float) -> str:
        """Process payment (owner only)"""
        return f"Payment processed: ${amount}"
    
    @handoff(target="payment-gateway")
    async def handoff_payment(self, payment_data: dict):
        """Handoff to payment gateway"""
        pass

# Create agent with multiple skills
agent = BaseAgent(
    name="calculator-payment-agent",
    instructions="You help with calculations and payments.",
    model="openai/gpt-4o",
    skills={
        "calculator": CalculatorSkill(),
        "payment": PaymentSkill()
    }
)

# Use agent
messages = [{"role": "user", "content": "Add 5 and 3, then process a $10 payment"}]
response = await agent.run(messages=messages)
```

## API Reference

::: robutler.agents.core.base_agent.BaseAgent 