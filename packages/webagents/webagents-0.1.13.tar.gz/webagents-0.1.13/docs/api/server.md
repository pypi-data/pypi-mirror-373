# Robutler Server API Reference

!!! warning "Beta Software Notice"  

    Robutler is currently in **beta stage**. While the core functionality is stable and actively used, APIs and features may change. We recommend testing thoroughly before deploying to critical environments.

## Overview

The **Robutler Server** provides **OpenAI-compatible APIs** with additional features including **multi-agent routing**, **dynamic agent creation**, **comprehensive monitoring**, and **enterprise middleware**.

**Base URL**: `http://your-server.com`  
**API Version**: `2.0.0`  
**OpenAI Compatibility**: OpenAI Chat Completions-compatible

---

## Authentication

Authentication is configurable per deployment. When `AuthSkill` is enabled on agents, requests must include a valid platform API key. Identity headers are standardized and read by `AuthSkill`.

```bash
# With API key (if server requires it)
curl -H "Authorization: Bearer your-api-key" http://server.com/assistant/chat/completions

# Without authentication (if server allows)
curl http://server.com/assistant/chat/completions
```

### Identity Headers

```bash
# User context headers for request tracking
-H "X-Origin-User-ID: <end-user-id>"
-H "X-Peer-User-ID: <peer-id>"
-H "X-Agent-Owner-User-ID: <owner-id>"
```

---

## Core Endpoints

### Server Discovery

#### Get Server Information
```http
GET /
```

**Response:**
```json
{
  "message": "Robutler V2 Server",
  "version": "2.0.0",
  "agents": ["assistant", "data-analyst", "support"],
  "endpoints": {
    "agent_info": "/{agent_name}",
    "chat_completions": "/{agent_name}/chat/completions",
    "health": "/health",
    "metrics": "/metrics"
  }
}
```

### Agent Information

#### Get Agent Details
```http
GET /{agent_name}
```

**Example:**
```bash
curl http://localhost:8000/assistant
```

**Response:**
```json
{
  "agent": "assistant",
  "description": "You are a helpful AI assistant that provides accurate...",
  "agent_data": {
    "name": "assistant",
    "capabilities": ["llm:gpt-4o-mini", "payment:billing", "discovery:search"],
    "skills": ["primary_llm", "payments", "discovery"],
    "tools": ["search_web", "get_weather", "calculate"],
    "model": "gpt-4o-mini",
    "pricing": {}
  },
  "endpoints": {
    "control": "/assistant",
    "info": "/assistant", 
    "chat": "/assistant/chat/completions"
  }
}
```

---

## Chat Completions API

### Non-Streaming Chat Completion

#### Create Chat Completion
```http
POST /{agent_name}/chat/completions
Content-Type: application/json
```

**Request Body:**
```json
{
  "model": "assistant",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
  "stream": false,
  "temperature": 0.7,
  "max_tokens": 1000,
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
          "type": "object", 
          "properties": {
            "location": {"type": "string"}
          },
          "required": ["location"]
        }
      }
    }
  ]
}
```

**Response:**
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1706178345,
  "model": "assistant",
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
    "prompt_tokens": 15,
    "completion_tokens": 10,
    "total_tokens": 25
  }
}
```

### Streaming Chat Completion

#### Create Streaming Chat Completion
```http
POST /{agent_name}/chat/completions
Content-Type: application/json
```

**Request Body:**
```json
{
  "model": "assistant",
  "messages": [
    {"role": "user", "content": "Count to 5"}
  ],
  "stream": true
}
```

**Response (Server-Sent Events):**
```
Content-Type: text/plain; charset=utf-8

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1706178345,"model":"assistant","choices":[{"index":0,"delta":{"role":"assistant"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1706178345,"model":"assistant","choices":[{"index":0,"delta":{"content":"1"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1706178345,"model":"assistant","choices":[{"index":0,"delta":{"content":"2"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1706178345,"model":"assistant","choices":[{"index":0,"delta":{},"finish_reason":"stop"}],"usage":{"prompt_tokens":10,"completion_tokens":5,"total_tokens":15}}

data: [DONE]
```

### Tool Calls

#### Request with External Tools
```json
{
  "model": "assistant",
  "messages": [
    {"role": "user", "content": "What's the weather in New York?"}
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {"type": "string"}
          },
          "required": ["location"]
        }
      }
    }
  ]
}
```

**Response with Tool Calls:**
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1706178345,
  "model": "assistant",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": null,
        "tool_calls": [
          {
            "id": "call_abc123",
            "type": "function", 
            "function": {
              "name": "get_weather",
              "arguments": "{\"location\": \"New York\"}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 15,
    "total_tokens": 35
  }
}
```

---

## Health & Monitoring

### Basic Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2024-01-15T10:30:45.123Z"
}
```

### Detailed Health Check
```http
GET /health/detailed
```

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0", 
  "timestamp": "2024-01-15T10:30:45.123Z",
  "agents": {
    "assistant": {
      "status": "healthy",
      "skills": 3,
      "tools": 5
    },
    "dynamic_agent_factory": {
      "status": "healthy",
      "cache_size": 10,
      "service_token_configured": true
    }
  }
}
```

### Kubernetes Probes

#### Readiness Probe
```http
GET /ready
```

Returns `200` if ready, `503` if not ready:
```json
{
  "status": "ready",
  "timestamp": "2024-01-15T10:30:45.123Z",
  "details": {
    "assistant": "ready",
    "dynamic_agent_factory": "ready"
  }
}
```

#### Liveness Probe
```http
GET /live
```

**Response:**
```json
{
  "status": "alive",
  "timestamp": "2024-01-15T10:30:45.123Z",
  "uptime_seconds": 3600.5
}
```

---

## Performance & Statistics

### Server Statistics
```http
GET /stats
```

**Response:**
```json
{
  "server_info": {
    "version": "2.0.0",
    "static_agents": 2,
    "dynamic_agents_enabled": true,
    "uptime_seconds": 3600.5,
    "monitoring_enabled": true,
    "prometheus_enabled": true,
    "request_timeout": 300.0,
    "rate_limiting_enabled": true
  },
  "performance": {
    "total_requests": 1250,
    "requests_last_minute": 15, 
    "active_requests": 3,
    "average_response_time_ms": 245.7,
    "error_rate": 0.02,
    "last_updated": 1706178345.123
  },
  "rate_limiting": {
    "default_limits": {
      "requests_per_minute": 60,
      "requests_per_hour": 1000,
      "requests_per_day": 10000,
      "burst_limit": 10
    },
    "custom_user_rules": 5
  },
  "dynamic_agent_factory": {
    "caching_enabled": true,
    "cache_ttl": 300,
    "agent_data_cache_size": 8,
    "agent_instance_cache_size": 12,
    "service_token_configured": true
  }
}
```

### Prometheus Metrics
```http
GET /metrics
```

**Response (Prometheus format):**
```prometheus
# HELP robutler_http_requests_total Total HTTP requests
# TYPE robutler_http_requests_total counter
robutler_http_requests_total{method="POST",path="/assistant/chat/completions",status_code="200",agent_name="assistant"} 1250

# HELP robutler_http_request_duration_seconds HTTP request duration
# TYPE robutler_http_request_duration_seconds histogram
robutler_http_request_duration_seconds_bucket{method="POST",path="/assistant/chat/completions",agent_name="assistant",le="0.1"} 100

# HELP robutler_agent_requests_total Total requests per agent
# TYPE robutler_agent_requests_total counter  
robutler_agent_requests_total{agent_name="assistant",stream="false"} 800
robutler_agent_requests_total{agent_name="assistant",stream="true"} 450

# HELP robutler_tokens_used_total Total tokens used
# TYPE robutler_tokens_used_total counter
robutler_tokens_used_total{agent_name="assistant",model="gpt-4o-mini"} 125000

# HELP robutler_active_agents Number of active agents
# TYPE robutler_active_agents gauge
robutler_active_agents 5
```

---

## Error Responses

### Standard Error Format

All errors follow OpenAI-compatible format:

```json
{
  "error": {
    "type": "invalid_request_error",
    "code": "agent_not_found", 
    "message": "Agent 'nonexistent-agent' not found",
    "param": null
  }
}
```

### Common Error Codes

#### 400 Bad Request
```json
{
  "error": {
    "type": "invalid_request_error",
    "code": "invalid_request",
    "message": "Invalid request format",
    "param": "messages"
  }
}
```

#### 404 Not Found
```json
{
  "error": {
    "type": "invalid_request_error", 
    "code": "agent_not_found",
    "message": "Agent 'unknown-agent' not found"
  }
}
```

#### 429 Rate Limited
```json
{
  "error": {
    "type": "rate_limit_exceeded",
    "code": "too_many_requests",
    "message": "Rate limit exceeded (60 requests per minute)",
    "retry_after": 45
  }
}
```

**Response Headers:**
```
Retry-After: 45
X-RateLimit-Limit-Minute: 60
X-RateLimit-Remaining-Minute: 0
```

#### 500 Internal Server Error
```json
{
  "error": {
    "type": "server_error",
    "code": "internal_error", 
    "message": "An unexpected error occurred"
  }
}
```

#### 503 Service Unavailable
```json
{
  "error": {
    "type": "server_error",
    "code": "service_unavailable",
    "message": "Server is not ready to accept requests"
  }
}
```

---

## Request/Response Headers

### Standard Headers

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer your-api-key (optional)
X-User-ID: user123 (optional)
X-Request-ID: custom-request-id (optional)
```

**Response Headers:**
```
Content-Type: application/json
X-Request-ID: req_abc123
X-RateLimit-Limit-Minute: 60
X-RateLimit-Remaining-Minute: 45
```

### Streaming Headers

**Streaming Response Headers:**
```
Content-Type: text/plain; charset=utf-8
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no
```

---

## Multi-Agent Routing

### Static Agents

Agents defined at server startup:

```bash
# Route to specific agents by name
curl http://server.com/assistant/chat/completions    # General assistant
curl http://server.com/data-analyst/chat/completions # Data specialist  
curl http://server.com/support/chat/completions      # Customer support
```

### Dynamic Agents

Agents created on-demand from configurations:

```bash
# Any agent name - created from portal if configured
curl http://server.com/my-custom-agent/chat/completions
curl http://server.com/domain-expert/chat/completions
curl http://server.com/specialized-bot/chat/completions
```

### Agent Precedence

1. **Static agents** (defined at startup) take precedence  
2. **Dynamic agents** (from portal/resolver) used if no static match
3. **404 error** if no agent found in either source

---

## Rate Limiting

### Default Limits

- **Per minute**: 60 requests
- **Per hour**: 1,000 requests  
- **Per day**: 10,000 requests
- **Burst**: 10 requests per second

### Rate Limit Headers

**Response includes rate limit information:**
```
X-RateLimit-Limit-Minute: 60
X-RateLimit-Remaining-Minute: 45
X-RateLimit-Limit-Hour: 1000
X-RateLimit-Remaining-Hour: 856
X-RateLimit-Limit-Day: 10000
X-RateLimit-Remaining-Day: 8234
```

### Client Identification

Rate limits applied based on:
1. **User ID** (X-User-ID header) - highest priority
2. **API Key** (Authorization header) - if provided
3. **IP Address** - fallback identification

---

## Usage Examples

### Python (OpenAI SDK)
```python
import openai

client = openai.OpenAI(base_url="http://localhost:8000")

response = client.chat.completions.create(
    model="assistant",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### cURL  
```bash
curl -X POST http://localhost:8000/assistant/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello!"}]}'
```

### JavaScript (Fetch)
```javascript
const response = await fetch('http://localhost:8000/assistant/chat/completions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    messages: [{ role: 'user', content: 'Hello!' }]
  })
});

const data = await response.json();
```

### Streaming Example
```bash
curl -X POST http://localhost:8000/assistant/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Count to 5"}], "stream": true}'
```

---

## OpenAI Compatibility

### Supported Parameters

| Parameter | Supported | Notes |
|-----------|-----------|-------|
| `model` | ✅ | Mapped to agent name |
| `messages` | ✅ | Full OpenAI format |
| `stream` | ✅ | SSE streaming |
| `tools` | ✅ | External tools only |
| `temperature` | ✅ | Passed to underlying model |
| `max_tokens` | ✅ | Passed to underlying model |
| `top_p` | ✅ | Passed to underlying model |
| `frequency_penalty` | ✅ | Passed to underlying model |
| `presence_penalty` | ✅ | Passed to underlying model |
| `stop` | ✅ | Passed to underlying model |

### Response Compatibility

- ✅ **Identical format** to OpenAI ChatCompletions
- ✅ **Same field names** and structure
- ✅ **Compatible error codes** and messages
- ✅ **Usage tracking** with token counts
- ✅ **Streaming chunks** with proper SSE format

---

## Next Steps

- **[Server Guide](../sdk/server.md)** - Complete setup guide
- **[OpenAI Compatibility Guide](../sdk/openai-compatibility.md)** - Using with OpenAI clients  
- **[Dynamic Agents Guide](../sdk/dynamic-agents.md)** - Multi-agent configuration
- **[Server Guide](../sdk/server.md)** - Server setup and monitoring 