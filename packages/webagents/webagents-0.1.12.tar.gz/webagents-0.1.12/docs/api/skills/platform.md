# Platform Skills API Reference

!!! warning "Beta Software Notice"  

    Robutler is currently in **beta stage**. While the core functionality is stable and actively used, APIs and features may change. We recommend testing thoroughly before deploying to critical environments.

## Discovery Skill

### DiscoverySkill

::: robutler.agents.skills.robutler.discovery.skill.DiscoverySkill

    options:
        members:
            - __init__
            - initialize
            - discovery_tool
            - publish_intents_tool
            - get_dependencies

### DiscoveryResult

::: robutler.agents.skills.robutler.discovery.skill.DiscoveryResult



## Payment Skill

### PaymentSkill

::: robutler.agents.skills.robutler.payments.skill.PaymentSkill

    options:
        members:
            - __init__
            - initialize
            - track_usage
            - charge_credits
            - validate_balance

### PaymentContext

::: robutler.agents.skills.robutler.payments.skill.PaymentContext

## Auth Skill

### AuthSkill

::: robutler.agents.skills.robutler.auth.skill.AuthSkill

    options:
        members:
            - __init__
            - initialize
            - validate_token
            - check_permissions
            - get_user_context

### AuthScope

::: robutler.agents.skills.robutler.auth.skill.AuthScope

### AuthContext

::: robutler.agents.skills.robutler.auth.skill.AuthContext

## NLI Skill

### NLISkill

::: robutler.agents.skills.robutler.nli.skill.NLISkill

    options:
        members:
            - __init__
            - initialize
            - communicate_with_agent
            - broadcast_message
            - parse_communication

### NLICommunication

::: robutler.agents.skills.robutler.nli.skill.NLICommunication

### AgentEndpoint

::: robutler.agents.skills.robutler.nli.skill.AgentEndpoint

## Usage Examples

### Discovery Skill Usage

```python
from robutler.agents.skills.robutler.discovery.skill import DiscoverySkill

# Basic discovery setup
discovery_skill = DiscoverySkill({
    "search_scope": "public",
    "max_results": 10,
    "cache_duration": 300
})

agent = BaseAgent(
    name="coordinator",
    model="openai/gpt-4o-mini",
    skills={
        "llm": OpenAISkill({"model": "gpt-4o-mini"}),
        "discovery": discovery_skill
    }
)

# Agent can now discover other agents
response = await agent.run(messages=[
    {"role": "user", "content": "Find an agent that can help with data analysis"}
])
```

### Payment Skill Usage

```python
from robutler.agents.skills.robutler.payments.skill import PaymentSkill

# Configure payment tracking
payment_skill = PaymentSkill({
    "credits_per_token": 10,
    "auto_billing": True,
    "payment_required": True,
    "minimum_balance": 1000
})

agent = BaseAgent(
    name="premium-agent",
    model="openai/gpt-4o-mini",
    skills={
        "llm": OpenAISkill({"model": "gpt-4o-mini"}),
        "payments": payment_skill
    }
)

# Payment tracking is automatic
response = await agent.run(messages=[
    {"role": "user", "content": "Perform complex analysis"}
])
# Credits are automatically deducted
```

### Auth Skill Usage

```python
from robutler.agents.skills.robutler.auth.skill import AuthSkill

# Configure authentication
auth_skill = AuthSkill({
    "required_scopes": ["agent.chat", "agent.tools"],
    "verify_tokens": True,
    "admin_required": False
})

agent = BaseAgent(
    name="secure-agent",
    model="openai/gpt-4o-mini",
    skills={
        "llm": OpenAISkill({"model": "gpt-4o-mini"}),
        "auth": auth_skill
    }
)

# Authentication is enforced automatically via hooks
```

### NLI Skill Usage

```python
from robutler.agents.skills.robutler.nli.skill import NLISkill

# Configure agent communication
nli_skill = NLISkill({
    "communication_protocol": "natural",
    "auto_routing": True,
    "message_formatting": "conversational"
})

agent = BaseAgent(
    name="communicator",
    model="openai/gpt-4o-mini",
    skills={
        "llm": OpenAISkill({"model": "gpt-4o-mini"}),
        "nli": nli_skill
    }
)

# Agent can communicate with other agents
response = await agent.run(messages=[
    {"role": "user", "content": "Ask the data analyst agent to process this CSV file"}
])
```

## Skill Integration Examples

### Complete Platform Integration

```python
from robutler.agents.skills.core.llm.openai.skill import OpenAISkill
from robutler.agents.skills.robutler.discovery.skill import DiscoverySkill
from robutler.agents.skills.robutler.payments.skill import PaymentSkill
from robutler.agents.skills.robutler.auth.skill import AuthSkill
from robutler.agents.skills.robutler.nli.skill import NLISkill

# Create agent with full platform integration
agent = BaseAgent(
    name="platform-agent",
    instructions="You are a fully integrated platform agent.",
    skills={
        # Core capability
        "llm": OpenAISkill({"model": "gpt-4o-mini"}),
        
        # Platform integration
        "discovery": DiscoverySkill(),
        "payments": PaymentSkill({"credits_per_token": 5}),
        "auth": AuthSkill({"required_scopes": ["chat"]}),
        "nli": NLISkill()
    }
)

# Execution flow:
# 1. AuthSkill validates user credentials (on_request hook)
# 2. DiscoverySkill enables agent discovery capabilities
# 3. PaymentSkill tracks usage and charges credits
# 4. NLISkill enables communication with other agents
# 5. LLMSkill generates responses
```

### Custom Platform Tools

```python
from robutler.agents.tools.decorators import tool
from robutler.server.context.context_vars import get_context

@tool
def find_and_communicate(query: str, target_agent: str) -> str:
    """Find information and communicate with another agent."""
    context = get_context()
    
    # Use discovery skill to find agents
    discovery_skill = context.agent_skills.get("discovery")
    if discovery_skill:
        agents = discovery_skill.search_agents(query)
        
        # Use NLI skill to communicate
        nli_skill = context.agent_skills.get("nli")
        if nli_skill and target_agent:
            response = nli_skill.communicate_with_agent(
                target_agent, 
                f"Please help with: {query}"
            )
            return response
    
    return "Unable to find or communicate with agents"

@tool
def check_credits_and_upgrade() -> str:
    """Check credit balance and suggest upgrades."""
    context = get_context()
    
    # Use payment skill to check balance
    payment_skill = context.agent_skills.get("payments")
    if payment_skill:
        balance = payment_skill.get_credit_balance(context.user_id)
        
        if balance < 1000:
            return f"Low balance: {balance} credits. Consider upgrading your plan."
        else:
            return f"Credit balance: {balance} credits. You're all set!"
    
    return "Unable to check credit balance"
```

## Configuration Reference

### Discovery Skill Configuration

```python
discovery_config = {
    # Search settings
    "search_scope": "public",    # "public", "private", "all"
    "max_results": 10,           # Max agents to return
    "cache_duration": 300,       # Cache results for 5 minutes
    
    # Intent matching
    "intent_matching": True,     # Enable intent-based discovery
    "similarity_threshold": 0.7, # Min similarity for matches
    "fuzzy_matching": True,      # Enable fuzzy string matching
    
    # Filtering
    "category_filter": None,     # List of categories to include
    "exclude_offline": True,     # Exclude offline agents
    "verified_only": False       # Only include verified agents
}
```

### Payment Skill Configuration

```python
payment_config = {
    # Billing settings
    "credits_per_token": 10,     # Credits charged per token
    "auto_billing": True,        # Automatic billing
    "payment_required": True,    # Require payment for usage
    "minimum_balance": 1000,     # Minimum balance required
    
    # Rate limiting
    "daily_limit": 100000,       # Daily credit limit
    "hourly_limit": 10000,       # Hourly credit limit
    "burst_limit": 1000,         # Burst credit limit
    
    # Notifications
    "low_balance_warning": 500,  # Warn when balance is low
    "send_notifications": True,  # Send balance notifications
    "notification_threshold": 0.1 # Notify at 10% remaining
}
```

### Auth Skill Configuration

```python
auth_config = {
    # Authentication
    "verify_tokens": True,       # Verify JWT tokens
    "required_scopes": ["chat"], # Required OAuth scopes
    "admin_required": False,     # Require admin access
    "api_key_auth": True,        # Support API key auth
    
    # Authorization
    "role_based_access": True,   # Enable role-based access
    "permission_model": "rbac",  # "rbac" or "simple"
    "default_permissions": ["read"], # Default permissions
    
    # Session management
    "session_timeout": 3600,     # Session timeout in seconds
    "refresh_tokens": True,      # Support refresh tokens
    "max_sessions": 5           # Max concurrent sessions
}
```

### NLI Skill Configuration

```python
nli_config = {
    # Communication protocol
    "protocol": "natural",       # "natural" or "structured"
    "auto_routing": True,        # Auto-route to appropriate agents
    "message_formatting": "conversational", # Message format
    
    # Agent discovery
    "discover_agents": True,     # Auto-discover available agents
    "agent_registry": "platform", # "platform" or "local"
    "cache_agents": True,        # Cache agent information
    
    # Message handling
    "queue_messages": True,      # Queue messages for offline agents
    "retry_failed": True,        # Retry failed communications
    "max_retries": 3,            # Max retry attempts
    "timeout": 30                # Communication timeout
}
```

## Error Handling

### Platform-Specific Errors

```python
from robutler.agents.skills.robutler.auth.skill import AuthenticationError, AuthorizationError
from robutler.agents.skills.robutler.payments import PaymentValidationError, InsufficientBalanceError

try:
    response = await agent.run(messages=messages)
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except AuthorizationError as e:
    print(f"Authorization failed: {e}")
except PaymentValidationError as e:
    print(f"Payment validation failed: {e}")
except InsufficientBalanceError as e:
    print(f"Insufficient credits: {e}")
```

### Graceful Platform Degradation

```python
class PlatformAgent(BaseAgent):
    """Agent with platform fallbacks."""
    
    async def run(self, messages, **kwargs):
        try:
            return await super().run(messages, **kwargs)
        except AuthenticationError:
            # Use anonymous mode
            self.disable_skill("auth")
            return await super().run(messages, **kwargs)
        except InsufficientBalanceError:
            # Use free tier
            self.configure_skill("payments", {"free_tier": True})
            return await super().run(messages, **kwargs)
```

## Environment Variables

```bash
# Platform Integration
export ROBUTLER_API_KEY="your-robutler-api-key"
export ROBUTLER_API_URL="https://robutler.ai"

# Authentication
export JWT_SECRET_KEY="your-jwt-secret"
export OAUTH_CLIENT_ID="your-oauth-client-id"

# Payment Processing
export STRIPE_API_KEY="your-stripe-key"
export PAYMENT_WEBHOOK_SECRET="your-webhook-secret"

# Discovery Service
export DISCOVERY_SERVICE_URL="https://discovery.robutler.ai"
export AGENT_REGISTRY_URL="https://registry.robutler.ai"
```

## Next Steps

- **[Core Skills](core.md)** - Essential core capabilities
- **[Base Skill Interface](base.md)** - Core skill interface
- **[Data Types](types.md)** - Platform skill data types 