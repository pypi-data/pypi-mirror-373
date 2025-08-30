# Exceptions

The API Client provides comprehensive error handling through custom exception classes that give detailed information about API errors and system failures.

## RobutlerAPIError

::: robutler.api.client.RobutlerAPIError

## Error Handling Patterns

### Basic Error Handling

```python
from robutler.api.client import RobutlerClient, RobutlerAPIError

async with RobutlerClient() as client:
    try:
        user_response = await client.get_user()
        if user_response.success:
            user = user_response.data
        else:
            print(f"API Error: {user_response.message}")
    except RobutlerAPIError as e:
        print(f"Exception: {e}")
        if e.status_code:
            print(f"Status Code: {e.status_code}")
        if e.response_data:
            print(f"Response Data: {e.response_data}")
```

### Status Code Handling

```python
try:
    result = await client.create_api_key("MyKey")
    if not result.success:
        print(f"API Error: {result.message}")
except RobutlerAPIError as e:
    if e.status_code == 401:
        print("Authentication failed - check your API key")
    elif e.status_code == 402:
        print("Insufficient credits or payment required")
    elif e.status_code == 429:
        print("Rate limit exceeded - please wait")
    elif e.status_code == 500:
        print("Server error - please try again later")
    else:
        print(f"Unexpected error: {e}")
```

### Credit and Usage Errors

```python
try:
    credits = await client.get_user_credits()
    if not credits.success:
        print(f"Credits error: {credits.message}")
except RobutlerAPIError as e:
    if e.status_code == 402:
        print("Payment required - insufficient credits")
    elif e.status_code == 404:
        print("User or credit information not found")
    else:
        print(f"Credits error: {e}")
```

### Integration Management Errors

```python
try:
    integration = await client.create_integration(
        name="My App",
        type="webhook",
        url="https://myapp.com/webhook"
    )
    if not integration.success:
        print(f"Integration error: {integration.message}")
except RobutlerAPIError as e:
    if e.status_code == 400:
        print("Invalid integration parameters")
    elif e.status_code == 409:
        print("Integration already exists")
    else:
        print(f"Integration error: {e}")
```

## Error Categories

### Authentication Errors (401)
- Invalid API key
- Missing ROBUTLER_API_KEY environment variable
- Expired or revoked API key

### Payment Errors (402)
- Insufficient credits for operation
- Credit limit exceeded
- Payment method required

### Client Errors (4xx)
- Bad request (400) - Invalid parameters
- Unauthorized (401) - Authentication failure
- Forbidden (403) - Permission denied
- Not found (404) - Resource not found
- Conflict (409) - Resource already exists
- Rate limiting (429) - Too many requests

### Server Errors (5xx)
- Internal server error (500)
- Service unavailable (503)
- Gateway timeout (504)

## Best Practices

### Retry Logic with Exponential Backoff

```python
import asyncio
from robutler.api.client import RobutlerAPIError

async def retry_api_call(api_func, max_retries=3, delay=1.0):
    """Retry API calls with exponential backoff for server errors."""
    for attempt in range(max_retries):
        try:
            result = await api_func()
            return result
        except RobutlerAPIError as e:
            # Retry on server errors
            if e.status_code >= 500 and attempt < max_retries - 1:
                wait_time = delay * (2 ** attempt)
                print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                raise
```

### Response Validation Pattern

```python
async def safe_api_call(client, operation_name, api_func):
    """Make API call with comprehensive error handling."""
    try:
        response = await api_func()
        
        if response.success:
            return response.data
        else:
            print(f"{operation_name} failed: {response.message}")
            return None
            
    except RobutlerAPIError as e:
        if e.status_code == 401:
            print(f"{operation_name}: Authentication required")
        elif e.status_code >= 500:
            print(f"{operation_name}: Service temporarily unavailable")
        else:
            print(f"{operation_name}: {e}")
        return None

# Usage example
async with RobutlerClient() as client:
    user_data = await safe_api_call(
        client, 
        "Get User Info", 
        client.get_user
    )
``` 