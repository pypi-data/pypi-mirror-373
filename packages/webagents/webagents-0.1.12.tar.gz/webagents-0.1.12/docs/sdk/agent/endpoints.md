# Agent Endpoints

Create custom HTTP API endpoints for your agents using the `@http` decorator. Endpoints provide RESTful access to agent capabilities and automatically integrate with FastAPI routing.

Endpoints support all HTTP methods, path parameters, query strings, and scope-based access control. They run in the same context as chat completions and can leverage all agent skills.

## Overview

HTTP endpoints extend your agent beyond chat completions, enabling direct API access to specific functions. They work alongside tools, prompts, and other agent capabilities.

**Key Features:**
- Automatic FastAPI route registration
- All HTTP methods (GET, POST, PUT, DELETE, etc.)
- Path parameters and query strings
- Scope-based access control
- JSON request/response handling
- Context injection support
- Error handling and status codes

## Basic Usage

### Simple Endpoint

```python
from robutler.agents.tools.decorators import http
from robutler.agents import BaseAgent

@http("/status")
def get_status() -> dict:
    """Simple status endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "uptime": "5h 23m"
    }

agent = BaseAgent(
    name="api-agent",
    model="openai/gpt-4o",
    http_handlers=[get_status]
)
```

**Available at:** `GET /api-agent/status`

### Direct Registration

You can also register HTTP endpoints directly on agent instances:

```python
agent = BaseAgent(name="my-agent", model="openai/gpt-4o")

@agent.http("/status")
def get_status() -> dict:
    """Agent status endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "uptime": "5h 23m"
    }

@agent.http("/metrics", method="get", scope="admin")
def get_metrics() -> dict:
    """Performance metrics endpoint"""
    return {
        "requests_per_second": 100,
        "response_time": "50ms",
        "error_rate": "0.1%"
    }
```

**Available at:**
- `GET /my-agent/status`
- `GET /my-agent/metrics` (admin only)

### HTTP Methods

```python
@http("/users", method="get")
def list_users() -> dict:
    return {"users": ["alice", "bob", "charlie"]}

@http("/users", method="post")
def create_user(data: dict) -> dict:
    return {"created": data["name"], "id": "user_123"}

@http("/users/{user_id}", method="get")
def get_user(user_id: str) -> dict:
    return {"id": user_id, "name": f"User {user_id}"}

@http("/users/{user_id}", method="put")
def update_user(user_id: str, data: dict) -> dict:
    return {"updated": user_id, "data": data}

@http("/users/{user_id}", method="delete")
def delete_user(user_id: str) -> dict:
    return {"deleted": user_id}
```

### Async Endpoints

```python
@http("/process", method="post")
async def process_data(data: dict) -> dict:
    """Async endpoint for long-running operations"""
    import asyncio
    await asyncio.sleep(1)  # Simulate processing
    
    return {
        "processed": data,
        "processing_time": "1s",
        "status": "completed"
    }
```

### HTTP Decorator Options

The `@http` decorator supports several configuration options:

```python
@http(
    subpath="/my-endpoint",      # URL path after agent name
    method="get",                # HTTP method (get, post, put, delete, etc.)
    scope="all"                  # Access scope ("all", "owner", "admin", or list)
)
def my_endpoint():
    return {"message": "Hello from custom endpoint"}
```

**Supported HTTP Methods:**
- `get` (default)
- `post`  
- `put`
- `delete`
- `patch`
- `head`
- `options`

**Scope-Based Access Control:**
- `"all"` - Public access (default)
- `"owner"` - Agent owner only
- `"admin"` - Admin users only
- `["owner", "admin"]` - Multiple scopes

### Capabilities Auto-Registration

Use the `capabilities` parameter to automatically register decorated HTTP functions:

```python
from robutler.agents.tools.decorators import http, tool

@http("/api/status")
def get_status() -> dict:
    return {"status": "healthy"}

@http("/api/data", method="post", scope="owner")
def post_data(data: dict) -> dict:
    return {"received": data}

@tool
def my_tool(input: str) -> str:
    return f"Processed: {input}"

# Auto-register all decorated functions
agent = BaseAgent(
    name="capable-agent",
    model="openai/gpt-4o",
    capabilities=[get_status, post_data, my_tool]  # Mixed decorators
)
```

The agent automatically categorizes HTTP endpoints and registers them appropriately.

## Path Parameters

Use dynamic path segments with automatic type conversion:

```python
@http("/users/{user_id}/posts/{post_id}")
def get_user_post(user_id: str, post_id: str) -> dict:
    return {
        "user_id": user_id,
        "post_id": post_id,
        "title": f"Post {post_id} by User {user_id}"
    }

@http("/items/{item_id}")
def get_item(item_id: int, include_details: bool = False) -> dict:
    """Path params + query params"""
    item = {"id": item_id, "name": f"Item {item_id}"}
    
    if include_details:
        item["details"] = "Extended item information"
    
    return item
```

**Usage:**
- `GET /api-agent/users/123/posts/456`
- `GET /api-agent/items/789?include_details=true`

## Scope-Based Access Control

Control endpoint access with scopes:

```python
@http("/public", scope="all")
def public_endpoint() -> dict:
    """Anyone can access"""
    return {"message": "Public data"}

@http("/private", scope="owner")
def owner_endpoint() -> dict:
    """Only agent owners"""
    return {"private": "owner data"}

@http("/admin", scope="admin")
def admin_endpoint() -> dict:
    """Admin users only"""
    return {"admin": "sensitive data"}

@http("/premium", scope=["premium", "enterprise"])
def premium_endpoint() -> dict:
    """Multiple scopes"""
    return {"premium": "exclusive features"}
```

## Request Handling

### Query Parameters

```python
@http("/search")
def search_items(query: str, limit: int = 10, sort: str = "name") -> dict:
    """Query parameters with defaults"""
    return {
        "query": query,
        "limit": limit,
        "sort": sort,
        "results": [f"Item matching '{query}'"]
    }
```

**Usage:** `GET /api-agent/search?query=python&limit=5&sort=date`

### JSON Request Body

```python
@http("/analyze", method="post")
def analyze_data(request_data: dict) -> dict:
    """Handle JSON request body"""
    dataset = request_data.get("dataset", [])
    options = request_data.get("options", {})
    
    return {
        "analyzed": len(dataset),
        "options": options,
        "result": "Analysis complete"
    }
```

**Usage:**
```bash
curl -X POST /api-agent/analyze \
  -H "Content-Type: application/json" \
  -d '{"dataset": [1,2,3], "options": {"method": "linear"}}'
```

### FastAPI Request Object

```python
from fastapi import Request

@http("/advanced", method="post")
async def advanced_endpoint(request: Request) -> dict:
    """Access full FastAPI request object"""
    body = await request.json()
    headers = dict(request.headers)
    
    return {
        "body": body,
        "headers": headers,
        "method": request.method,
        "url": str(request.url)
    }
```

## Context Integration

Access request context for user information and skills:

```python
@http("/user-info", scope="owner")
def get_user_info(context) -> dict:
    """Access request context"""
    user_id = getattr(context, 'user_id', 'anonymous')
    auth_scope = getattr(context, 'auth_scope', 'all')
    
    return {
        "user_id": user_id,
        "scope": auth_scope,
        "timestamp": context.created_at.isoformat()
    }

@http("/balance", scope="owner")
async def get_balance(context) -> dict:
    """Use payment skills in endpoints"""
    # Access agent skills through context
    balance = await get_user_balance(context.user_id)
    return {"balance": balance, "currency": "USD"}
```

## Skill Integration

Use agent skills within endpoints:

```python
from robutler.agents.skills.base import Skill

class APISkill(Skill):
    """Skill that provides HTTP endpoints"""
    
    @http("/data", method="get")
    def get_data(self) -> dict:
        """Skill-based endpoint"""
        return {"data": self.fetch_data()}
    
    @http("/process", method="post", scope="owner")
    async def process_request(self, data: dict) -> dict:
        """Async skill endpoint"""
        result = await self.process_data(data)
        return {"processed": result}
    
    def fetch_data(self) -> str:
        return "skill data"
    
    async def process_data(self, data: dict) -> dict:
        return {"processed": True, "input": data}

# Use in agent
agent = BaseAgent(
    name="skill-agent",
    model="openai/gpt-4o",
    skills={"api": APISkill()}
)
```

## Error Handling

Handle errors gracefully with proper HTTP status codes:

```python
from fastapi import HTTPException

@http("/users/{user_id}")
def get_user_safe(user_id: str) -> dict:
    """Endpoint with error handling"""
    if not user_id.isdigit():
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"id": user_id, "name": user["name"]}

@http("/validate", method="post")
def validate_data(data: dict) -> dict:
    """Validation with custom errors"""
    required_fields = ["name", "email"]
    missing = [f for f in required_fields if f not in data]
    
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required fields: {', '.join(missing)}"
        )
    
    return {"valid": True, "data": data}
```

## Advanced Patterns

### Middleware Integration

```python
@http("/protected", scope="owner")
async def protected_endpoint(context) -> dict:
    """Endpoint with custom middleware logic"""
    # Custom authentication check
    if not hasattr(context, 'authenticated_user'):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Rate limiting check
    if await is_rate_limited(context.user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    return {"message": "Access granted", "user": context.authenticated_user}
```

### File Upload/Download

```python
from fastapi import UploadFile, File
from fastapi.responses import FileResponse

@http("/upload", method="post", scope="owner")
async def upload_file(file: UploadFile = File(...)) -> dict:
    """File upload endpoint"""
    content = await file.read()
    filename = f"uploads/{file.filename}"
    
    # Save file logic here
    save_file(filename, content)
    
    return {
        "filename": file.filename,
        "size": len(content),
        "content_type": file.content_type
    }

@http("/download/{filename}")
def download_file(filename: str) -> FileResponse:
    """File download endpoint"""
    file_path = f"uploads/{filename}"
    if not file_exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path, filename=filename)
```

### WebSocket Support

```python
from fastapi import WebSocket

@http("/ws", method="websocket")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint"""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            response = f"Echo: {data}"
            await websocket.send_text(response)
    except Exception:
        await websocket.close()
```

## Best Practices

### Keep Endpoints Focused
```python
# ✅ Good - single responsibility
@http("/users/{user_id}")
def get_user(user_id: str) -> dict:
    return get_user_data(user_id)

# ❌ Avoid - too many responsibilities
@http("/everything")
def do_everything(action: str, data: dict) -> dict:
    if action == "user": return get_user(data["id"])
    elif action == "post": return create_post(data)
    # ... too many different actions
```

### Use Appropriate HTTP Methods
```python
# ✅ Good - RESTful design
@http("/users", method="get")     # List users
@http("/users", method="post")    # Create user
@http("/users/{id}", method="get")    # Get user
@http("/users/{id}", method="put")    # Update user
@http("/users/{id}", method="delete") # Delete user

# ❌ Avoid - wrong methods
@http("/create-user", method="get")   # Should be POST
@http("/delete-user", method="post")  # Should be DELETE
```

### Handle Errors Properly
```python
# ✅ Good - proper error handling
@http("/users/{user_id}")
def get_user(user_id: str) -> dict:
    try:
        user = find_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

# ❌ Avoid - unhandled errors
@http("/users/{user_id}")
def get_user_unsafe(user_id: str) -> dict:
    return find_user(user_id)  # Could raise unhandled exceptions
```

## Integration Examples

### With Authentication Skills
```python
@http("/profile", scope="owner")
def get_profile(context) -> dict:
    """Get authenticated user profile"""
    user = getattr(context, 'authenticated_user')
    return {
        "name": user["name"],
        "email": user["email"],
        "role": user["role"]
    }
```

### With Payment Skills
```python
@http("/purchase", method="post", scope="owner")
async def make_purchase(item_id: str, context) -> dict:
    """Purchase item with automatic billing"""
    item = get_item(item_id)
    
    # Charge user through payment skill
    charge_result = await charge_user(
        context.user_id, 
        item["price"], 
        f"Purchase: {item['name']}"
    )
    
    if charge_result["success"]:
        return {"purchased": item, "transaction": charge_result["transaction_id"]}
    else:
        raise HTTPException(status_code=402, detail="Payment failed")
```

### With Discovery Skills
```python
@http("/agents/search")
async def search_agents(query: str) -> dict:
    """Search for agents in the network"""
    agents = await discover_agents(query)
    return {
        "query": query,
        "found": len(agents),
        "agents": [{"name": a.name, "description": a.description} for a in agents]
    }
```

## See Also

- **[Tools](tools.md)** - Executable functions for agents
- **[Prompts](prompts.md)** - Dynamic system prompt enhancement
- **[Hooks](hooks.md)** - Event-driven processing
- **[Skills](skills.md)** - Modular agent capabilities
