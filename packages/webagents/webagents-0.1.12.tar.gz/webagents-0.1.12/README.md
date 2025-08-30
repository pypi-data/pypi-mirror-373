# Robutler

Build discoverable and monetizable AI agents. 


## Installation

```bash
pip install robutler
```

## Quick Start

### AI Agent Server

Create AI agents with OpenAI-compatible endpoints:

```python
from robutler.server import RobutlerServer, pricing
from robutler.agent import RobutlerAgent

# Create tools with pricing
@pricing(credits_per_call=100)
def get_weather(location: str) -> str:
    """Get current weather for a location"""
    return f"Weather in {location}: Sunny, 72°F"

# Create an agent with intents
agent = RobutlerAgent(
    name="assistant",
    instructions="You are a helpful AI assistant.",
    credits_per_token=5,
    model="gpt-4o-mini",
    tools=[get_weather],
    intents=["help with weather", "provide assistance", "answer questions"]
)

# Create server with automatic endpoint creation
app = RobutlerServer(agents=[agent])

# Endpoints are automatically created:
# POST /assistant/chat/completions - OpenAI-compatible chat
# GET  /assistant                  - Agent info
```

Run the server:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### API Client

```python
from robutler.api import RobutlerApi

async with RobutlerApi() as api:
    user = await api.get_user_info()
    credits = await api.get_user_credits()
```

## Documentation

For comprehensive documentation, visit: [docs.robutler.ai](https://docs.robutler.ai)

## Environment Variables

```bash
ROBUTLER_API_KEY=your_api_key
```