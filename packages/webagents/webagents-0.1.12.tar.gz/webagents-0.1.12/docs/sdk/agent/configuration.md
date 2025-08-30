# Agent Configuration

Comprehensive guide to configuring BaseAgent with all available options.

## Constructor Parameters

```python
BaseAgent(
    name: str,                    # Unique agent identifier
    instructions: str = None,     # System instructions
    model: str | Skill = None,   # Smart model parameter
    skills: Dict[str, Skill] = None,  # Skill instances
    tools: List[Dict] = None,     # Additional external tools (OpenAI schema)
    temperature: float = None,    # Default temperature
    max_tokens: int = None,       # Max response tokens
    metadata: Dict = None         # Custom metadata
)
```

## Model Configuration

### Using Model String

```python
# Format: "provider/model"
agent = BaseAgent(
    name="my-agent",
    model="openai/gpt-4o"  # Auto-creates OpenAISkill
)
```

Supported providers:
- `openai/` - Direct OpenAI API
- `anthropic/` - Anthropic Claude models
- `litellm/` - LiteLLM proxy routing
- `xai/` - xAI Grok models

### Using Skill Instance

```python
from robutler.agents.skills import OpenAISkill

agent = BaseAgent(
    name="my-agent",
    model=OpenAISkill({
        "api_key": "sk-...",
        "base_url": "https://api.openai.com/v1",
        "temperature": 0.7,
        "max_tokens": 1000,
        "organization": "org-..."
    })
)
```

## Skill Configuration

### Basic Skills

```python
from robutler.agents.skills import (
    ShortTermMemorySkill,
    LongTermMemorySkill,
    VectorMemorySkill
)

agent = BaseAgent(
    name="memory-agent",
    model="openai/gpt-4o",
    skills={
        "short_term": ShortTermMemorySkill({
            "max_messages": 50,
            "filter_system": True
        }),
        "long_term": LongTermMemorySkill({
            "connection_string": "postgresql://...",
            "table_name": "agent_memory"
        }),
        "vector": VectorMemorySkill({
            "milvus_host": "localhost",
            "milvus_port": 19530,
            "collection_name": "agent_vectors"
        })
    }
)
```

### Platform Skills

```python
from robutler.agents.skills import (
    NLISkill,
    DiscoverySkill,
    PaymentSkill,
    AuthSkill
)

agent = BaseAgent(
    name="platform-agent",
    model="openai/gpt-4o",
    skills={
        "nli": NLISkill({
            "api_key": "robutler-key",
            "base_url": "https://api.robutler.ai"
        }),
        "discovery": DiscoverySkill({
            "cache_ttl": 300,
            "max_agents": 10
        }),
        "auth": AuthSkill(),
        "payments": PaymentSkill({
          "enable_billing": True,
          "agent_pricing_percent": 20,
          "minimum_balance": 1.0
        })
    }
)
```

## Tool Configuration

### External Tools

```python
agent = BaseAgent(
    name="tool-agent",
    model="openai/gpt-4o",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather for location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]
)
```

### Tool Implementation

```python
# External tools are executed by the client. For internal tools, use @tool in a skill.
```

## Advanced Configuration

### With Dependencies

```python
# Skills can declare dependencies
class MySkill(Skill):
    def __init__(self, config=None):
        super().__init__(
            config=config,
            dependencies=["memory", "auth"]  # Auto-included
        )
```

### With Scopes

```python
# Control access levels
class AdminSkill(Skill):
    def __init__(self, config=None):
        super().__init__(
            config=config,
            scope="admin"  # Only for admins
        )
    
    @tool(scope="admin")
    def admin_function(self):
        return "Admin only"
```

### Environment Variables

```python
import os

agent = BaseAgent(
    name="env-agent",
    model=f"openai/{os.getenv('OPENAI_MODEL', 'gpt-4o')}",
    skills={
        "memory": ShortTermMemorySkill({
            "max_messages": int(os.getenv('MAX_MEMORY', '50'))
        })
    }
)
```

## Complete Example

```python
from robutler.agents import BaseAgent
from robutler.agents.skills import (
    ShortTermMemorySkill,
    DiscoverySkill,
    NLISkill
)

# Production-ready agent
agent = BaseAgent(
    name="production-assistant",
    instructions="""You are a production assistant with:
    - Memory of conversations
    - Ability to find other agents
    - Multi-agent collaboration
    Always be helpful and accurate.""",
    model="openai/gpt-4o",
    temperature=0.7,
    max_tokens=2000,
    skills={
        "memory": ShortTermMemorySkill({
            "max_messages": 100,
            "filter_system": True
        }),
        "discovery": DiscoverySkill({
            "cache_ttl": 600
        }),
        "nli": NLISkill({
            "timeout": 30
        })
    },
    metadata={
        "version": "1.0.0",
        "environment": "production",
        "tags": ["assistant", "memory", "collaborative"]
    }
) 