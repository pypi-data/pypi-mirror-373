# OpenAI Compatibility

Robutler agents are fully compatible with OpenAI's chat completions API, allowing seamless integration with existing applications.

## API Endpoints

### Chat Completions

```
POST /agents/{agent_name}/chat/completions
```

Full compatibility with OpenAI's `/chat/completions` endpoint.

## Request Format

### Basic Request

```json
{
  "model": "gpt-4o",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ]
}
```

### Full Request Options

```json
{
  "model": "gpt-4o",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What's the weather like?"}
  ],
  "temperature": 0.7,
  "max_tokens": 1000,
  "top_p": 1.0,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0,
  "stop": ["\n"],
  "stream": false,
  "user": "user_123"
}
```

## Response Format

### Standard Response

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1699896916,
  "model": "gpt-4o",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 12,
    "total_tokens": 22
  }
}
```

### Tool Call Response

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1699896916,
  "model": "gpt-4o",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "I'll check the weather for you.",
        "tool_calls": [
          {
            "id": "call_abc123",
            "type": "function",
            "function": {
              "name": "get_weather",
              "arguments": "{\"location\": \"San Francisco\"}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ],
  "usage": {
    "prompt_tokens": 82,
    "completion_tokens": 18,
    "total_tokens": 100
  }
}
```

## Streaming

### Streaming Request

```json
{
  "model": "gpt-4o",
  "messages": [
    {"role": "user", "content": "Tell me a story"}
  ],
  "stream": true
}
```

### Streaming Response

Server-Sent Events format:

```
data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1699896916,"model":"gpt-4o","choices":[{"index":0,"delta":{"role":"assistant","content":""},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1699896916,"model":"gpt-4o","choices":[{"index":0,"delta":{"content":"Once"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1699896916,"model":"gpt-4o","choices":[{"index":0,"delta":{"content":" upon"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1699896916,"model":"gpt-4o","choices":[{"index":0,"delta":{"content":" a"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1699896916,"model":"gpt-4o","choices":[{"index":0,"delta":{},"finish_reason":"stop"}],"usage":{"prompt_tokens":10,"completion_tokens":15,"total_tokens":25}}

data: [DONE]
```

## Client SDK Usage

### OpenAI Python SDK

```python
import openai

# Configure client for Robutler agent
client = openai.OpenAI(
    base_url="http://localhost:8000/agents/my-assistant",
    api_key="your-api-key"
)

# Standard usage - works exactly like OpenAI
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)
```

### OpenAI Node.js SDK

```javascript
import OpenAI from 'openai';

const client = new OpenAI({
  baseURL: 'http://localhost:8000/agents/my-assistant',
  apiKey: 'your-api-key',
});

const response = await client.chat.completions.create({
  model: 'gpt-4o',
  messages: [
    { role: 'user', content: 'Hello!' }
  ],
});

console.log(response.choices[0].message.content);
```

### curl Examples

```bash
# Basic request
curl -X POST "http://localhost:8000/agents/my-assistant/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'

# Streaming request
curl -X POST "http://localhost:8000/agents/my-assistant/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {"role": "user", "content": "Count from 1 to 10"}
    ],
    "stream": true
  }'
```

## Tool Calling

### External Tool Definition

```python
# External tools are defined in the tools parameter following OpenAI standard
external_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "description": "Temperature unit (celsius or fahrenheit)",
                        "enum": ["celsius", "fahrenheit"]
                    }
                },
                "required": ["location"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather like in Boston?"}],
    tools=external_tools
)
```

### Handling Tool Calls

```python
# Agent response with tool calls
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather like in Boston?"}],
    tools=external_tools
)

assistant_message = response.choices[0].message

if assistant_message.tool_calls:
    # Execute each tool call
    for tool_call in assistant_message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        # Execute the tool based on name
        if function_name == "get_current_weather":
            result = get_weather_api(arguments["location"])
        
        # Add tool result to conversation
        messages.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [tool_call]
        })
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result
        })
        
        # Get final response
        final_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=external_tools
        )
        return final_response.choices[0].message.content

def get_weather_api(location):
    """Your weather API implementation"""
    return f"Sunny, 72°F in {location}"

# Usage with proper tool definitions
external_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

messages = [{"role": "user", "content": "What's the weather in New York?"}]
result = handle_external_tools(messages, external_tools)
print(result)
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "message": "Invalid API key provided",
    "type": "invalid_request_error",
    "param": null,
    "code": "invalid_api_key"
  }
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `invalid_api_key` | Invalid authentication |
| `invalid_request_error` | Malformed request |
| `rate_limit_exceeded` | Too many requests |
| `model_not_found` | Agent not available |
| `insufficient_quota` | Usage limits exceeded |
| `server_error` | Internal server error |

### Error Handling Example

```python
try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello!"}]
    )
except openai.AuthenticationError:
    print("Invalid API key")
except openai.RateLimitError:
    print("Rate limit exceeded")
except openai.APIError as e:
    print(f"API error: {e}")
```

## Model Parameter

### Agent Model Selection

The `model` parameter is handled by the agent's configuration:

```python
# Agent with specific model
agent = BaseAgent(
    name="gpt4-agent",
    model="openai/gpt-4o"  # Actual model used
)

# Client request (model parameter is informational)
response = client.chat.completions.create(
    model="any-value",  # Ignored - agent's model is used
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Model Information

```python
# Get agent info
response = requests.get("http://localhost:8000/agents/my-agent/info")
agent_info = response.json()

print(f"Agent uses model: {agent_info['model']}")
print(f"Available tools: {agent_info['tools']}")
```

## Differences from OpenAI

### Enhanced Features

1. **Skills System** - Agents have built-in capabilities beyond tools
2. **Multi-Agent Handoffs** - Automatic routing to specialized agents  
3. **Persistent Memory** - Available when you add a memory skill
4. **Custom Hooks** - Lifecycle event handling
5. **Scope-Based Access** - Fine-grained permission control

### Agent-Specific Behavior

```python
# OpenAI: Stateless
response1 = openai_client.chat.completions.create(...)
response2 = openai_client.chat.completions.create(...)  # No memory

# Robutler: Agent with memory skill remembers (when added)
response1 = robutler_client.chat.completions.create(...)
response2 = robutler_client.chat.completions.create(...)  # Has memory
```

### Internal vs External Tools

```python
# External tools - defined in messages
messages = [
    {
        "role": "system", 
        "content": "You have access to: get_weather(location: str) -> str"
    },
    {
        "role": "user", 
        "content": "What's the weather in Paris?"
    }
]
response = client.chat.completions.create(messages=messages)
# You handle parsing and executing the tools the agent references

# Internal tools (Robutler extension)
# Handled automatically by agent skills - no tool definitions needed
response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Calculate 42 * 17"}]
)
# Agent automatically uses internal calculator skill
```

## Migration from OpenAI

### Simple Migration

```python
# Before: Direct OpenAI
import openai
client = openai.OpenAI(api_key="sk-...")

# After: Robutler agent
import openai
client = openai.OpenAI(
    base_url="http://localhost:8000/agents/my-assistant",
    api_key="your-robutler-key"
)

# Same code works!
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Advanced Migration

```python
# Add Robutler-specific features gradually
from robutler.agents import BaseAgent
from robutler.agents.skills import ShortTermMemorySkill

# Create enhanced agent
agent = BaseAgent(
    name="enhanced-assistant",
    instructions="You are a helpful assistant with memory",
    model="openai/gpt-4o",
    skills={
        "memory": ShortTermMemorySkill()
    }  # Added memory - client code unchanged
)
```

## Testing Compatibility

```python
import pytest
import openai

@pytest.fixture
def client():
    return openai.OpenAI(
        base_url="http://localhost:8000/agents/test-agent",
        api_key="test-key"
    )

def test_basic_completion(client):
    """Test basic OpenAI compatibility"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    
    # Standard OpenAI response format
    assert response.id
    assert response.object == "chat.completion"
    assert response.model
    assert len(response.choices) == 1
    assert response.choices[0].message.role == "assistant"
    assert response.choices[0].message.content
    assert response.usage.total_tokens > 0

def test_streaming_completion(client):
    """Test streaming compatibility"""
    stream = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Count to 3"}],
        stream=True
    )
    
    chunks = list(stream)
    
    # Standard streaming format
    assert len(chunks) > 0
    assert chunks[0].object == "chat.completion.chunk"
    assert chunks[-1].choices[0].finish_reason == "stop"

def test_external_tools(client):
    """Test external tool handling"""
    messages = [
        {
            "role": "system",
            "content": "You have access to: test_tool(input: str) -> str"
        },
        {
            "role": "user", 
            "content": "Use the test tool with input 'hello'"
        }
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    
    # Should reference the external tool
    content = response.choices[0].message.content
    assert "test_tool" in content
    assert response.choices[0].finish_reason == "stop"
``` 