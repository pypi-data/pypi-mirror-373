# Payment Token Validation in RobutlerAgent

This document explains how to use payment token validation with RobutlerAgent to ensure users have sufficient credits before processing requests, and how tokens are automatically charged after usage.

## Overview

RobutlerAgent now supports payment token validation and automatic charging through the `min_balance` parameter. The system works in two phases:

### 1. Pre-Request Validation
When `min_balance > 0`, the agent will:
1. Check for an `X-Payment-Token` header in incoming requests
2. Validate the token with the Robutler Portal API
3. Verify the token has sufficient balance to meet the minimum requirement
4. Return a 402 Payment Required error if validation fails

### 2. Post-Request Charging
After successful agent execution, the system will:
1. Extract usage information (tokens used, calls made)
2. Calculate total credits consumed based on agent pricing
3. Automatically charge the payment token for actual usage
4. Log the charge and remaining balance

## Usage

### Creating an Agent with Payment Requirements

```python
from robutler.agent import RobutlerAgent

# Create an agent that requires payment tokens
paid_agent = RobutlerAgent(
    name="PremiumAssistant",
    instructions="You are a premium AI assistant",
    min_balance=1000,        # Requires at least 1000 credits
    credits_per_call=100,    # Fixed cost per call
    credits_per_token=2,     # Additional cost per token
    model="gpt-4o-mini"
)

# Create a free agent (no payment required)
free_agent = RobutlerAgent(
    name="BasicAssistant", 
    instructions="You are a basic AI assistant",
    min_balance=0,  # Default: no payment required
    credits_per_token=1,
    intents=["basic help"]
)
```

### Making Requests with Payment Tokens

```bash
curl -X POST "http://localhost:8000/PremiumAssistant/chat/completions" \
  -H "Content-Type: application/json" \
  -H "X-Payment-Token: your-token-uuid:your-secret" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'

# Call a free agent (no token needed)
curl http://localhost:8000/BasicAssistant/chat/completions \
  -X POST \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "BasicAssistant", 
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Automatic Charging Process

The charging process happens automatically after each successful request:

1. **Usage Extraction**: System extracts token usage from the AI response
2. **Cost Calculation**: Calculates total cost based on:
   - Fixed cost per call (`credits_per_call`)
   - Variable cost per token (`credits_per_token × total_tokens`)
3. **Token Charging**: Calls the portal API to charge the payment token using the agent's API key for authentication
4. **Balance Logging**: Logs the charge amount and remaining balance

### Authentication

The system uses the agent's API key (from `ROBUTLER_API_KEY` environment variable) to authenticate with the Robutler Portal when:
- Validating payment tokens (pre-request)
- Charging payment tokens (post-request)

This ensures that only authorized agents can validate and charge payment tokens.

### Example Usage Log

```
💰 Agent Usage - 2024-01-15 10:30:45
   Agent: PremiumAssistant (Agent)
   Request: POST /PremiumAssistant/chat/completions -> 200 (1.234s)
   User: Hello, how are you?
   AI: I'm doing well, thank you for asking!
   Prompt tokens: 15
   Completion tokens: 12
   Total tokens: 27
   💳 Cost Breakdown:
      Call cost: 100 credits
      Token cost: 54 credits (27 tokens)
      Total cost: 154 credits
💳 Payment token charged: 154 credits
   Remaining balance: 2846 credits
   Streaming: No
   ────────────────────────────────────────────────────────────
```

## Error Responses

### 402 Payment Required - No Token Provided

When a paid agent is called without a payment token:

```json
{
  "detail": "Payment token required. Minimum balance: 1000 credits. Include X-Payment-Token header."
}
```

### 402 Payment Required - Invalid Token

When an invalid or expired token is provided:

```json
{
  "detail": "Invalid payment token"
}
```

### 402 Payment Required - Insufficient Balance

When the token doesn't have enough credits:

```json
{
  "detail": "Insufficient token balance. Available: 500, Required: 1000"
}
```

### 500 Internal Server Error

When token validation fails due to service issues:

```json
{
  "detail": "Payment token validation failed: Connection error"
}
```

## Configuration

### Environment Variables

- `ROBUTLER_API_URL`: URL of the Robutler Portal API (default: `http://localhost:3000`)
- `ROBUTLER_API_KEY`: API key for authenticating with the portal (used for token validation)

### Agent Parameters

- `min_balance` (int): Minimum token balance required (default: 0)
  - `0`: No payment required (free agent)
  - `> 0`: Payment token required with at least this balance

### Agent Data Population

Both static and dynamic endpoints now populate `agent_data` with:

- `name`: Agent name
- `api_key`: API key from `ROBUTLER_API_KEY` environment variable (via settings)
- `min_balance`: Minimum balance requirement
- `credits_per_token`: Cost per token
- `model`: AI model being used
- `instructions`: Agent system instructions
- `intents`: Supported intents

This ensures consistent behavior between static and dynamic agent endpoints.

### Authentication

Payment token validation uses the agent's API key for authentication:

1. **Agent API Key**: Uses the API key from `agent_data.api_key` 
2. **Fallback**: Uses `ROBUTLER_API_KEY` from settings if agent data unavailable
3. **Authorization Header**: Sends `Authorization: Bearer {api_key}` to portal

This allows proper attribution of token validation requests to the correct agent/user.

## Payment Token Format

Payment tokens use the format: `{uuid}:{secret}`

- The UUID identifies the token in the database
- The secret is used for authentication
- Tokens have expiration dates and spending limits
- Tokens can be partially consumed and reused until depleted

## Context Storage

When a valid payment token is provided, the following information is stored in the request context:

- `payment_token`: The full token string
- `token_info`: Full token details from the portal
- `available_balance`: Current available balance

This information can be accessed in agent handlers for custom billing logic.

## Integration with Robutler Portal

The payment token validation integrates with the Robutler Portal's token management system:

- Tokens are validated against `/api/tokens/validate`
- The portal handles token creation, expiration, and balance tracking
- Agents automatically check token balance before processing requests
- No additional billing logic needed in agent code

## Best Practices

1. **Set appropriate minimum balances** based on your agent's cost per request
2. **Use environment variables** for portal URL configuration
3. **Handle 402 errors gracefully** in client applications
4. **Monitor token usage** through the portal dashboard
5. **Set reasonable token expiration times** to balance security and usability

## Example Server Setup

```python
from robutler.agent import RobutlerAgent
from robutler.server import Server

# Create agents with different payment requirements
agents = [
    RobutlerAgent(
        name="Free",
        instructions="Free assistant", 
        min_balance=0
    ),
    RobutlerAgent(
        name="Basic", 
        instructions="Basic paid assistant",
        min_balance=100,
        credits_per_token=2
    ),
    RobutlerAgent(
        name="Premium",
        instructions="Premium assistant", 
        min_balance=1000,
        credits_per_token=10
    )
]

# Start server
app = Server(agents=agents)
```

This creates three tiers of service with automatic payment validation based on the `min_balance` setting.