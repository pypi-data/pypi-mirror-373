# Python SDK Quickstart

Get started with Robutler in 5 minutes - create, run, and serve your first AI agent.

!!! warning "Beta Software Notice"  

    Robutler is currently in **beta stage**. While the core functionality is stable and actively used, APIs and features may change. We recommend testing thoroughly before deploying to critical environments.

## Installation

```bash
pip install robutler
```

## Create Your First Agent

```python
from robutler.agents.core.base_agent import BaseAgent

# Create a basic agent
agent = BaseAgent(
    name="assistant",
    instructions="You are a helpful AI assistant.",
    model="openai/gpt-4o-mini"  # Automatically creates LLM skill
)

# Run chat completion
messages = [{"role": "user", "content": "Hello! What can you help me with?"}]
response = await agent.run(messages=messages)
print(response.content)
```

## Serve Your Agent

Deploy your agent as an OpenAI-compatible API server:

```python
from robutler.server.core.app import create_server
import uvicorn

# Create server with your agent
server = create_server(agents=[agent])

# Run the server
uvicorn.run(server.app, host="0.0.0.0", port=8000)
```

Test your agent API:
```bash
curl -X POST http://localhost:8000/assistant/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello!"}]}'
```

## Environment Setup

Set up your API keys for LLM providers:

```bash
# Required for OpenAI models
export OPENAI_API_KEY="your-openai-key"

# Optional for other providers
export ANTHROPIC_API_KEY="your-anthropic-key"
export ROBUTLER_API_KEY="your-robutler-key"
```

## Make Your Agent More Powerful

Now that you have a basic agent running, enhance it with advanced capabilities:

<div class="grid cards" markdown>

-   🧠 **Add Skills**

    ---

    Extend your agent with memory, tools, and specialized capabilities.

    [Browse Skills →](../skills/overview.md)

-   💰 **Add Payments**

    ---

    Enable monetization and automatic billing for your agent services.

    [Payment Integration →](../skills/platform/payments.md)

-   🔍 **Add Discovery**

    ---

    Connect to the Internet of Agents for real-time agent discovery and collaboration.

    [Discovery System →](../skills/platform/discovery.md)

-   🗣️ **Add Natural Language Interface**

    ---

    Enable natural language communication with other agents and systems.

    [NLI Integration →](../skills/platform/nli.md)

</div>

## Learn More

- **[Agent Architecture](agent/overview.md)** - Understand how agents work
- **[Skills Framework](skills/overview.md)** - Modular capabilities system
- **[Server Deployment](server.md)** - Production server setup
- **[Custom Skills](skills/custom.md)** - Build your own capabilities 