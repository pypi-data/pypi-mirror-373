# Core Client

The core API client provides comprehensive access to all Robutler backend services using a modern object-oriented design with hierarchical resources and typed model objects.

## Quick Start

```python
from robutler.api.client import RobutlerClient, RobutlerAPIError

# Modern object-oriented usage
async with RobutlerClient() as client:
    try:
        # Get user information - returns UserProfile object
        user = await client.user.get()
        print(f"Welcome {user.name} ({user.email})!")
        print(f"Plan: {user.plan_name}")
        print(f"Available credits: {user.available_credits}")
        
        # List agents - returns List[Agent]
        agents = await client.agents.list()
        for agent in agents:
            print(f"Agent: {agent.name} (Model: {agent.model})")
        
        # Get content files - returns List[ContentFile]
        content_files = await client.content.list()
        for file in content_files:
            print(f"File: {file.name} ({file.size_formatted})")
        
    except RobutlerAPIError as e:
        print(f"API Error: {e} (Status: {e.status_code})")
```

## Environment Configuration

```bash
# Set environment variables
export ROBUTLER_API_KEY="your-api-key"
export ROBUTLER_API_URL="https://robutler.ai"
```

## Hierarchical API Structure

The new API client provides clean, intuitive access through hierarchical resources:

```python
# Agent management
client.agents.list() → List[Agent]
client.agents.get(agent_id) → AgentResource
client.agents.create(data) → Agent
client.agents.update(agent_id, data) → Agent
client.agents.delete(agent_id) → bool

# User management  
client.user.get() → UserProfile
client.user.credits() → Decimal
client.user.transactions(limit=50) → List[TransactionInfo]

# Content management
client.content.list() → List[ContentFile]
client.content.agent_access() → List[ContentFile]
client.content.upload(data, filename) → ContentFile
client.content.delete(file_id) → bool

# API key management
client.api_keys.list() → List[ApiKeyInfo]
client.api_keys.create(name) → ApiKeyInfo
client.api_keys.delete(key_id) → bool
```

## Model Objects

All API responses return typed model objects with clean attribute access:

### Agent Object
```python
agent = await client.agents.get("agent-id")
print(agent.name)           # Direct attribute access
print(agent.id)             # No more .get() calls
print(agent.model)          # Type-safe access
print(agent.instructions)   # IDE autocompletion
```

### UserProfile Object
```python
user = await client.user.get()
print(user.name)                # User's display name
print(user.email)               # User's email
print(user.available_credits)   # Calculated available credits
print(user.plan_name)           # Subscription plan
```

### ContentFile Object
```python
files = await client.content.list()
for file in files:
    print(file.name)            # Original filename
    print(file.size_formatted)  # Human-readable size (e.g., "1.2MB")
    print(file.url)             # Download URL
    print(file.visibility)      # "public" or "private"
```

## Integration Examples

### User Management

```python
async def get_account_summary():
    async with RobutlerClient() as client:
        # Get user profile (single call, typed object)
        user = await client.user.get()
        
        # Get transaction history (typed objects)
        transactions = await client.user.transactions(limit=10)
        
        # Get API keys (typed objects)
        api_keys = await client.api_keys.list()
        
        return {
            "user": {
                "name": user.name,
                "email": user.email,
                "plan": user.plan_name,
                "credits": str(user.available_credits)
            },
            "recent_transactions": len(transactions),
            "api_keys": len(api_keys)
        }
```

### Agent Operations

```python
async def manage_agents():
    async with RobutlerClient() as client:
        # List all agents
        agents = await client.agents.list()
        print(f"Found {len(agents)} agents")
        
        # Get API key for specific agent
        for agent in agents:
            if agent.name == "my-assistant":
                api_key = await client.agents.get(agent.id).api_key()
                print(f"API key for {agent.name}: {api_key}")
                break
        
        # Create new agent
        new_agent = await client.agents.create({
            "name": "new-assistant",
            "instructions": "You are a helpful assistant",
            "model": "gpt-4o-mini"
        })
        print(f"Created agent: {new_agent.name} (ID: {new_agent.id})")
```

### Content Management

```python
async def upload_and_list_content():
    async with RobutlerClient() as client:
        # Upload a file
        with open("document.pdf", "rb") as f:
            content_file = await client.content.upload(
                file_data=f.read(),
                filename="document.pdf",
                visibility="private"
            )
        
        print(f"Uploaded: {content_file.name} ({content_file.size_formatted})")
        
        # List all content
        files = await client.content.list()
        for file in files:
            print(f"📄 {file.name} - {file.size_formatted}")
        
        # Get agent-accessible content only
        agent_files = await client.content.agent_access(visibility="public")
        print(f"Agent can access {len(agent_files)} public files")
```

## Error Handling

The client automatically handles API responses and raises exceptions on errors:

```python
try:
    user = await client.user.get()
    print(f"User: {user.name}")
except RobutlerAPIError as e:
    print(f"API Error: {e}")
    print(f"Status Code: {e.status_code}")
    print(f"Response Data: {e.response_data}")
```

## Benefits of the New Design

- ✅ **Type Safety**: All responses are typed objects with proper attributes
- ✅ **IDE Support**: Full autocompletion and IntelliSense
- ✅ **Clean Code**: No more `response.success` checks or `.get()` calls
- ✅ **Hierarchical**: Intuitive resource organization
- ✅ **Error Handling**: Automatic exception raising on API errors
- ✅ **Future-Proof**: Easy to extend with new resources and methods 