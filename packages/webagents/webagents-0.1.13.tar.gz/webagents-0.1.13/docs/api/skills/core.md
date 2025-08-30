# Core Skills API Reference

!!! warning "Beta Software Notice"  

    Robutler is currently in **beta stage**. While the core functionality is stable and actively used, APIs and features may change. We recommend testing thoroughly before deploying to critical environments.

## LLM Skills

<!-- ### OpenAI Skill

::: robutler.agents.skills.core.llm.openai.skill.OpenAISkill

    options:
        members:
            - __init__
            - initialize
            - chat_completion
            - streaming_completion -->

### LiteLLM Skill

::: robutler.agents.skills.core.llm.litellm.skill.LiteLLMSkill

    options:
        members:
            - __init__
            - initialize
            - chat_completion
            - streaming_completion
            - get_available_models

## Memory Skills

### Short-Term Memory Skill

::: robutler.agents.skills.core.memory.short_term_memory.skill.ShortTermMemorySkill

    options:
        members:
            - __init__
            - initialize
            - process_message_memory
            - setup_memory_context
            - filter_messages
            - calculate_importance

### MessageContext

::: robutler.agents.skills.core.memory.short_term_memory.skill.MessageContext

## MCP Skill

### MCPSkill

::: robutler.agents.skills.core.mcp.skill.MCPSkill

    options:
        members:
            - __init__
            - initialize
            - start_server
            - stop_server
            - call_tool
            - get_resources
            - list_tools

### MCPServerConfig

::: robutler.agents.skills.core.mcp.skill.MCPServerConfig

### MCPTransport

::: robutler.agents.skills.core.mcp.skill.MCPTransport

### MCPExecution

::: robutler.agents.skills.core.mcp.skill.MCPExecution

## Usage Examples

### OpenAI Skill Usage

```python
from robutler.agents.skills.core.llm.openai.skill import OpenAISkill

# Basic usage
skill = OpenAISkill({
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 2000
})

agent = BaseAgent(
    name="openai-agent",
    instructions="You are an AI assistant.",
    skills={"llm": skill}
)

# Advanced configuration
advanced_skill = OpenAISkill({
    "model": "gpt-4o",
    "temperature": 0.3,
    "max_tokens": 4000,
    "top_p": 0.9,
    "frequency_penalty": 0.1,
    "presence_penalty": 0.1,
    "timeout": 60,
    "max_retries": 3
})
```

### Memory Skill Usage

```python
from robutler.agents.skills.core.memory.short_term_memory.skill import ShortTermMemorySkill

# Configure memory management
memory_skill = ShortTermMemorySkill({
    "max_messages": 50,
    "max_tokens": 4000,
    "importance_threshold": 0.3,
    "preserve_system": True,
    "preserve_last_n": 5
})

agent = BaseAgent(
    name="memory-agent",
    model="openai/gpt-4o-mini",
    skills={"memory": memory_skill}
)

# Memory automatically filters messages and manages context
response = await agent.run(messages=[
    {"role": "user", "content": "Remember my favorite color is blue"},
    {"role": "assistant", "content": "I'll remember that your favorite color is blue."},
    {"role": "user", "content": "What's my favorite color?"}
])
```

### MCP Skill Usage

```python
from robutler.agents.skills.core.mcp.skill import MCPSkill

# Configure MCP server
mcp_skill = MCPSkill({
    "server_command": ["node", "mcp-server.js"],
    "server_args": ["--port", "3000"],
    "timeout": 30,
    "auto_start": True
})

agent = BaseAgent(
    name="mcp-agent",
    model="openai/gpt-4o-mini",
    skills={
        "llm": OpenAISkill({"model": "gpt-4o-mini"}),
        "mcp": mcp_skill
    }
)

# Agent can now use MCP tools and resources
response = await agent.run(messages=[
    {"role": "user", "content": "Use the calculator tool to compute 2+2"}
])
```

### Multi-Skill Integration

```python
from robutler.agents.skills.core.llm.openai.skill import OpenAISkill
from robutler.agents.skills.core.memory.short_term_memory.skill import ShortTermMemorySkill
from robutler.agents.skills.core.mcp.skill import MCPSkill

# Create agent with multiple core skills
agent = BaseAgent(
    name="advanced-agent",
    instructions="You are an advanced AI with memory and MCP capabilities.",
    skills={
        "llm": OpenAISkill({"model": "gpt-4o-mini"}),
        "memory": ShortTermMemorySkill({
            "max_tokens": 4000,
            "importance_threshold": 0.2
        }),
        "mcp": MCPSkill({
            "server_command": ["python", "mcp_server.py"],
            "timeout": 30
        })
    }
)

# Skills work together automatically:
# 1. Memory skill filters and manages conversation context
# 2. MCP skill provides additional tools and resources  
# 3. LLM skill handles completion generation
response = await agent.run(messages=[
    {"role": "user", "content": "Calculate the fibonacci sequence for n=10 and remember the result"}
])
```

## Configuration Reference

### OpenAI Skill Configuration

```python
openai_config = {
    # Model selection
    "model": "gpt-4o-mini",  # Required
    
    # Generation parameters
    "temperature": 0.7,      # 0.0 to 2.0
    "max_tokens": 2000,      # Max response tokens
    "top_p": 1.0,            # 0.0 to 1.0
    "frequency_penalty": 0.0, # -2.0 to 2.0
    "presence_penalty": 0.0,  # -2.0 to 2.0
    
    # API configuration
    "api_key": "your-key",   # Optional, uses OPENAI_API_KEY env var
    "organization": "org-id", # Optional organization ID
    "timeout": 60,           # Request timeout in seconds
    "max_retries": 3,        # Max retry attempts
    
    # Advanced options
    "response_format": "text", # "text" or "json_object"
    "seed": None,            # Deterministic responses
    "stream": False          # Enable streaming (handled automatically)
}
```

### Memory Skill Configuration

```python
memory_config = {
    # Context management
    "max_messages": 50,      # Max messages to store
    "max_tokens": 4000,      # Max tokens in context
    "preserve_system": True, # Always keep system messages
    "preserve_last_n": 5,    # Always keep last N messages
    
    # Message filtering
    "importance_threshold": 0.3, # Min importance score (0.0-1.0)
    "keyword_boost": 0.2,    # Boost for important keywords
    "question_boost": 0.3,   # Boost for questions
    "user_boost": 0.1,       # Boost for user messages
    
    # Summarization
    "auto_summarize": True,  # Enable auto-summarization
    "summary_trigger": 20,   # Messages before summarization
    "summary_model": "gpt-3.5-turbo", # Model for summarization
    "summary_length": 200    # Max summary length
}
```

### MCP Skill Configuration

```python
mcp_config = {
    # Server configuration
    "server_command": ["node", "server.js"], # Required: command to start server
    "server_args": ["--port", "3000"],       # Additional server arguments
    "working_directory": "/path/to/server",  # Working directory for server
    
    # Connection settings
    "transport": "stdio",    # "stdio", "http", or "websocket"
    "timeout": 30,          # Connection timeout in seconds
    "auto_start": True,     # Auto-start server on initialization
    "auto_restart": True,   # Auto-restart server on failure
    
    # Tool configuration
    "allowed_tools": None,  # List of allowed tools (None = all)
    "tool_timeout": 15,     # Individual tool call timeout
    "max_concurrent": 5,    # Max concurrent tool calls
    
    # Resource configuration
    "resource_cache": True, # Enable resource caching
    "cache_ttl": 300       # Cache TTL in seconds
}
```

## Error Handling

### Skill-Specific Errors

```python
# Catch skill-specific errors
try:
    response = await agent.run(messages=messages)
except Exception as e:
    if "openai" in str(e).lower():
        print(f"OpenAI skill error: {e}")
    elif "memory" in str(e).lower():
        print(f"Memory skill error: {e}")
    elif "mcp" in str(e).lower():
        print(f"MCP skill error: {e}")
    else:
        print(f"General skill error: {e}")
```

### Graceful Degradation

```python
class RobustAgent(BaseAgent):
    """Agent with robust error handling."""
    
    async def run(self, messages, **kwargs):
        try:
            return await super().run(messages, **kwargs)
        except Exception as e:
            if "mcp" in str(e).lower():
                # Disable MCP skill and retry
                self.disable_skill("mcp")
                return await super().run(messages, **kwargs)
            elif "memory" in str(e).lower():
                # Reset memory skill
                self.reset_skill("memory")
                return await super().run(messages, **kwargs)
            else:
                raise
```

## Performance Considerations

### Memory Optimization

```python
# Optimize memory usage
memory_skill = ShortTermMemorySkill({
    "max_tokens": 2000,      # Smaller context window
    "importance_threshold": 0.5, # Higher threshold
    "preserve_last_n": 3,    # Fewer preserved messages
    "auto_summarize": True   # Enable summarization
})
```

### Concurrent Processing

```python
# Enable concurrent tool calls in MCP
mcp_skill = MCPSkill({
    "max_concurrent": 10,    # Higher concurrency
    "tool_timeout": 10,      # Shorter timeouts
    "async_tools": True      # Enable async tool execution
})
```

## Next Steps

- **[Platform Skills](platform.md)** - Robutler platform integration skills
- **[Base Skill Interface](base.md)** - Core skill interface documentation
- **[Data Types](types.md)** - Skill-related data types and structures 