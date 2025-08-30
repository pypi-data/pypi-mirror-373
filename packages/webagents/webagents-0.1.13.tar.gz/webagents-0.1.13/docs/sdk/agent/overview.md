# Agent Overview

BaseAgent is the core class for creating AI agents in Robutler. It provides a flexible, skill-based architecture for building agents with exactly the capabilities you need. Agents speak OpenAI’s Chat Completions dialect, so existing clients work out of the box, while the skill system adds powerful platform features like authentication, payments, discovery, and multi-agent collaboration.

## Creating Agents

### Basic Agent

```python
from robutler.agents import BaseAgent

agent = BaseAgent(
    name="my-assistant",
    instructions="You are a helpful assistant",
    model="openai/gpt-4o"  # Smart model parameter
)
```

### Agent with Skills

```python
from robutler.agents import BaseAgent
from robutler.agents.skills import ShortTermMemorySkill, DiscoverySkill

agent = BaseAgent(
    name="advanced-assistant",
    instructions="You are an advanced assistant with memory",
    model="openai/gpt-4o",
    skills={
        "memory": ShortTermMemorySkill({"max_messages": 50}),
        "discovery": DiscoverySkill()  # Find other agents
    }
)
```

## Smart Model Parameter

The `model` parameter supports multiple formats. When a provider prefix is used (e.g., `openai/`), the correct LLM skill is provisioned automatically. You can always pass a fully configured skill instance if you need custom behavior.

```python
# Explicit skill/model format
agent = BaseAgent(model="openai/gpt-4o")         # OpenAI GPT-4o
agent = BaseAgent(model="anthropic/claude-3")    # Anthropic Claude
agent = BaseAgent(model="litellm/gpt-4")         # Via LiteLLM proxy
agent = BaseAgent(model="xai/grok-beta")         # xAI Grok

# Custom skill instance
from robutler.agents.skills import OpenAISkill
agent = BaseAgent(model=OpenAISkill({
    "api_key": "sk-...",
    "temperature": 0.7
}))
```

## Running Agents

### Basic Conversation

```python
response = await agent.run([
    {"role": "user", "content": "Hello!"}
])
print(response.choices[0].message.content)
```

### Streaming Response

```python
async for chunk in agent.run_streaming([
    {"role": "user", "content": "Tell me a story"}
]):
    print(chunk.choices[0].delta.content, end="")
```

### With Tools

```python
# External tools can be passed per request
response = await agent.run(
    messages=[{"role": "user", "content": "Calculate 42 * 17"}],
    tools=[{
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Calculate math expressions",
            "parameters": {...}
        }
    }]
)
```

## Agent Capabilities

### Skills

Skills provide modular capabilities:

- **LLM Skills** - Language model providers
- **Memory Skills** - Conversation persistence
- **Platform Skills** - Robutler platform integration
- **Extra Skills** - Database, filesystem, web, etc.

### Tools

Tools are executable functions:

```python
from robutler.agents.tools.decorators import tool

class MySkill(Skill):
    @tool
    def my_function(self, param: str) -> str:
        """Tool description"""
        return f"Result: {param}"
```

### Hooks

Lifecycle hooks for request processing:

```python
from robutler.agents.skills.decorators import hook

class MySkill(Skill):
    @hook("on_message")
    async def process_message(self, context):
        """Process each message"""
        return context
```

### Handoffs

Route to specialized agents:

```python
from robutler.agents.skills.decorators import handoff

class MySkill(Skill):
    @handoff("expert-agent")
    def needs_expert(self, query: str) -> bool:
        """Determine if expert needed"""
        return "complex" in query
```

## Context Management

Agents maintain a unified context object throughout execution via `contextvars`. Skills read and write to this thread-safe structure, avoiding globals while remaining fully async-compatible.

```python
# Within a skill
context = self.get_context()
user_id = context.peer_user_id
messages = context.messages
streaming = context.stream
```

## Agent Registration

Register agents with the server:

```python
from robutler.server import app

app.register_agent(agent)

# Or multiple agents
app.register_agent(agent1)
app.register_agent(agent2)
```

## Best Practices

1. **Start Simple** - Begin with a basic agent, add skills as you go
2. **Use Dependencies** - Some skills auto-require others (e.g., payments depends on auth)
3. **Scope Appropriately** - Use tool scopes for access control
4. **Test Thoroughly** - Treat skills as units; test hooks and tools independently
5. **Monitor Performance** - Track usage and latency; payments will use `context.usage`