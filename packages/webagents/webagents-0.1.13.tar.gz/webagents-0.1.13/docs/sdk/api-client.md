# API Client

The Robutler API client provides programmatic access to the Robutler platform with a modern object-oriented design, hierarchical resources, and typed model objects for agent discovery, management, and communication.

## Installation

```bash
pip install robutler[client]
```

## Basic Usage

### Client Setup

```python
from robutler.api.client import RobutlerClient

# Initialize client
client = RobutlerClient(
    api_key="your-api-key",
    base_url="https://robutler.ai"  # Optional, defaults to portal
)
```

### Environment Configuration

```bash
# Set environment variables
export ROBUTLER_API_KEY="your-api-key"
export ROBUTLER_API_URL="https://robutler.ai"
```

```python
# Client automatically uses environment variables
client = RobutlerClient()
```

## Object-Oriented API Design

The new API client features clean, hierarchical access with typed model objects:

```python
# Modern usage - no more dictionary access!
async with RobutlerClient() as client:
    # Get typed objects directly
    agents = await client.agents.list()          # List[Agent]
    user = await client.user.get()               # UserProfile
    files = await client.content.list()          # List[ContentFile]
    api_keys = await client.api_keys.list()      # List[ApiKeyInfo]
    
    # Clean attribute access
    for agent in agents:
        print(f"Agent: {agent.name}")           # agent.name, not agent.get("name")
        print(f"Model: {agent.model}")          # Type-safe, IDE-friendly
        print(f"Instructions: {agent.instructions}")
```

## Agent Discovery & Management

### Finding Agents

```python
# List all available agents
async with RobutlerClient() as client:
    agents = await client.agents.list()
    
    for agent in agents:
        print(f"🤖 {agent.name}")
        print(f"📝 {agent.instructions[:100]}...")
        print(f"⚙️ Model: {agent.model}")
        print(f"🎯 Intents: {', '.join(agent.intents)}")
        print(f"💬 Can use other agents: {agent.can_use_other_agents}")
        print("---")
```

### Agent Information & API Keys

```python
# Get detailed agent information and API key
async with RobutlerClient() as client:
    agents = await client.agents.list()
    
    for agent in agents:
        if agent.name == "finance-expert":
            # Get API key for this agent
            api_key = await client.agents.get(agent.id).api_key()
            
            print(f"Agent: {agent.name}")
            print(f"ID: {agent.id}")
            print(f"Model: {agent.model}")
            print(f"API Key: {api_key}")
            break
```

### Creating & Managing Agents

```python
# Create a new agent
async with RobutlerClient() as client:
    new_agent = await client.agents.create({
        "name": "my-assistant",
        "instructions": "You are a helpful assistant specialized in customer support",
        "model": "gpt-4o-mini",
        "intents": ["customer_support", "help_desk"],
        "canTalkToOtherAgents": True
    })
    
    print(f"Created agent: {new_agent.name}")
    print(f"Agent ID: {new_agent.id}")
    
    # Update the agent
    updated_agent = await client.agents.update(new_agent.id, {
        "instructions": "Updated instructions for better performance"
    })
    
    print(f"Updated agent: {updated_agent.name}")
```

## Agent Communication

### Chat Completions

```python
# Send chat completion to specific agent
async with RobutlerClient() as client:
    # Get an agent
    agents = await client.agents.list()
    finance_agent = next(agent for agent in agents if "finance" in agent.name.lower())
    
    # Send chat completion
    completion = await client.agents.get(finance_agent.id).chat_completion({
        "messages": [
            {"role": "user", "content": "What's the best investment strategy for someone in their 30s?"}
        ],
        "model": finance_agent.model,
        "temperature": 0.7
    })
    
    print(f"Agent Response: {completion.content}")
    print(f"Usage: {completion.usage}")
```

## User Management

### User Profile & Credits

```python
# Get comprehensive user information
async with RobutlerClient() as client:
    # Get user profile
    user = await client.user.get()
    
    print(f"👤 User: {user.name} ({user.email})")
    print(f"📋 Role: {user.role}")
    print(f"💳 Plan: {user.plan_name}")
    print(f"💰 Total Credits: {user.total_credits}")
    print(f"💸 Used Credits: {user.used_credits}")
    print(f"✅ Available Credits: {user.available_credits}")
    print(f"🎫 Referral Code: {user.referral_code}")
```

### Transaction History

```python
# Get recent transactions
async with RobutlerClient() as client:
    transactions = await client.user.transactions(limit=20)
    
    print(f"💳 Recent Transactions ({len(transactions)}):")
    for tx in transactions:
        sign = "+" if tx.type == "credit" else "-"
        print(f"  {sign}{tx.amount} credits - {tx.description}")
        print(f"    {tx.created_at} (Status: {tx.status})")
```

### API Key Management

```python
# Manage API keys
async with RobutlerClient() as client:
    # List existing API keys
    api_keys = await client.api_keys.list()
    
    print(f"🔑 Your API Keys ({len(api_keys)}):")
    for key in api_keys:
        last_used = key.last_used or "Never"
        print(f"  • {key.name} (Created: {key.created_at})")
        print(f"    Last used: {last_used}")
    
    # Create new API key
    new_key = await client.api_keys.create(
        name="My New Integration",
        permissions={"agents": ["read", "write"], "content": ["read"]}
    )
    
    print(f"🆕 Created API Key: {new_key.name}")
    print(f"🔐 Key: {new_key.key}")
```

## Content Management

### File Operations

```python
# Upload and manage content files
async with RobutlerClient() as client:
    # Upload a file
    with open("training_data.json", "rb") as f:
        content_file = await client.content.upload(
            file_data=f.read(),
            filename="training_data.json",
            visibility="private"
        )
    
    print(f"📤 Uploaded: {content_file.name}")
    print(f"📏 Size: {content_file.size_formatted}")
    print(f"🔗 URL: {content_file.url}")
    
    # List all content
    files = await client.content.list(visibility="private")
    
    print(f"📁 Your Files ({len(files)}):")
    for file in files:
        print(f"  📄 {file.name} ({file.size_formatted})")
        print(f"     Visibility: {file.visibility}")
```

### Agent-Accessible Content

```python
# Get content that agents can access
async with RobutlerClient() as client:
    # Get public content available to agents
    public_files = await client.content.agent_access(visibility="public")
    
    print(f"🤖 Agent-Accessible Files ({len(public_files)}):")
    for file in public_files:
        print(f"  📄 {file.name} ({file.size_formatted})")
        print(f"     URL: {file.url}")
```

## Advanced Usage

### Resource Chaining

```python
# Chain resource operations efficiently
async with RobutlerClient() as client:
    # Get agent and immediately access its API key
    agents = await client.agents.list()
    my_agent = agents[0]
    
    api_key = await client.agents.get(my_agent.id).api_key()
    
    # Send a chat completion to the same agent
    result = await client.agents.get(my_agent.id).chat_completion({
        "messages": [{"role": "user", "content": "Hello!"}],
        "model": my_agent.model
    })
    
    print(f"Agent {my_agent.name} responded: {result.content}")
```

### Batch Operations

```python
# Perform multiple operations efficiently
async with RobutlerClient() as client:
    # Get all data in parallel (if needed)
    user = await client.user.get()
    agents = await client.agents.list()
    files = await client.content.list()
    
    # Process all data
    print(f"User: {user.name} has {len(agents)} agents and {len(files)} files")
    
    total_file_size = sum(file.size for file in files)
    print(f"Total content size: {total_file_size / (1024*1024):.1f}MB")
```

## Error Handling

```python
from robutler.api.client import RobutlerAPIError

# Comprehensive error handling
async with RobutlerClient() as client:
    try:
        agents = await client.agents.list()
        print(f"Found {len(agents)} agents")
        
    except RobutlerAPIError as e:
        print(f"API Error: {e}")
        print(f"Status Code: {e.status_code}")
        
        # Handle specific error cases
        if e.status_code == 401:
            print("Authentication failed - check your API key")
        elif e.status_code == 403:
            print("Permission denied - insufficient permissions")
        elif e.status_code == 429:
            print("Rate limit exceeded - please wait")
        else:
            print(f"Unexpected error: {e.response_data}")
```

## Migration from Old API

If you're migrating from the old dictionary-based API:

### Before (Old Way)
```python
# ❌ Old dictionary-based approach
response = await client._make_request('GET', '/api/agents')
if response.success:
    agents = response.data.get("agents", [])
    for agent in agents:
        name = agent.get("name")
        model = agent.get("model", "unknown")
```

### After (New Way)
```python
# ✅ New object-oriented approach  
agents = await client.agents.list()  # List[Agent] directly
for agent in agents:
    name = agent.name               # Direct attribute access
    model = agent.model             # Type-safe, IDE-friendly
```

## Benefits of the New Design

- ✅ **Type Safety**: All responses are properly typed objects
- ✅ **IDE Support**: Full autocompletion and IntelliSense support
- ✅ **Clean Code**: No more `response.success` checks or `.get()` dictionary access
- ✅ **Hierarchical**: Intuitive resource organization (`client.agents.list()`)
- ✅ **Error Handling**: Automatic exception raising on API errors
- ✅ **Future-Proof**: Easy to extend with new resources and methods
- ✅ **Developer Friendly**: Much more readable and maintainable code

## Summary

The new Robutler API client provides a modern, type-safe interface for all platform operations. With hierarchical resource organization and typed model objects, it's easier than ever to build robust integrations with the Robutler platform. 