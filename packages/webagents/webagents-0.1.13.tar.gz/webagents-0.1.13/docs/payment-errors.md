# Payment Error System - Robutler V2.0

The Robutler payment system provides comprehensive error handling with specific error codes, subcodes, and detailed context information to distinguish between different 402 payment failure scenarios.

## 🎯 Overview

All payment errors inherit from the base `PaymentError` class and include:
- **Error Code**: Primary classification (e.g., `PAYMENT_TOKEN_INVALID`)
- **Subcode**: Specific variant (e.g., `TOKEN_EXPIRED`)
- **Context**: Additional data (balances, amounts, etc.)
- **User Message**: User-friendly error description
- **Technical Message**: Detailed information for logging/debugging

## 📋 Error Types

### 1. PaymentTokenRequiredError
**Code**: `PAYMENT_TOKEN_REQUIRED`

Raised when a payment token is required but not provided.

```python
# Context includes:
{
    'agent_name': 'MyAgent'  # Optional
}
```

### 2. PaymentTokenInvalidError
**Code**: `PAYMENT_TOKEN_INVALID`

Raised when a payment token is invalid or expired.

**Subcodes**:
- `TOKEN_EXPIRED` - Token has expired
- `TOKEN_NOT_FOUND` - Token doesn't exist
- `TOKEN_MALFORMED` - Invalid token format

```python
# Context includes:
{
    'token_prefix': 'abc123...',  # First 20 chars
    'validation_error': 'Token expired'
}
```

### 3. InsufficientBalanceError
**Code**: `INSUFFICIENT_BALANCE`

Raised when token balance is below the minimum required.

```python
# Context includes:
{
    'current_balance': 5.50,
    'required_balance': 10.00,
    'shortfall': 4.50,
    'token_prefix': 'abc123...'
}
```

### 4. PaymentChargingError
**Code**: `PAYMENT_CHARGING_FAILED`

Raised when charging/redeeming a payment token fails.

**Subcodes**:
- `INSUFFICIENT_FUNDS` - Not enough balance for charge
- `TOKEN_EXPIRED_DURING_CHARGE` - Token expired during transaction
- `SPENDING_LIMIT_EXCEEDED` - Account spending limit reached

```python
# Context includes:
{
    'charge_amount': 2.50,
    'token_prefix': 'abc123...',
    'charge_error': 'Insufficient funds'
}
```

### 5. PaymentPlatformUnavailableError
**Code**: `PAYMENT_PLATFORM_UNAVAILABLE`

Raised when the payment platform is temporarily unavailable.

```python
# Context includes:
{
    'attempted_operation': 'token validation'
}
```

### 6. PaymentConfigurationError
**Code**: `PAYMENT_CONFIG_ERROR`

Raised when payment system configuration is invalid.

```python
# Context includes:
{
    'config_issue': 'Missing API key',
    'details': 'ROBUTLER_API_KEY not set'
}
```

## 🔧 Usage Examples

### Basic Error Handling

```python
from robutler.agents.skills.robutler.payments.exceptions import (
    PaymentError,
    PaymentTokenRequiredError,
    InsufficientBalanceError
)

try:
    # Your payment operation
    await some_payment_operation()
    
except PaymentTokenRequiredError as e:
    print(f"❌ {e.user_message}")
    print("💡 Please add a payment token to continue")
    
except InsufficientBalanceError as e:
    balance_info = e.context
    shortfall = balance_info['shortfall']
    print(f"💰 Add ${shortfall:.2f} more credits")
    
except PaymentError as e:
    print(f"💳 Payment error: {e.user_message}")
    print(f"🔧 Error code: {e.error_code}")
    if e.subcode:
        print(f"📊 Subcode: {e.subcode}")
```

### API Response Handling

```python
from robutler.agents.skills.robutler.payments.exceptions import PaymentError

try:
    result = await payment_operation()
    return {'success': True, 'result': result}
    
except PaymentError as e:
    # Convert to structured API response using built-in method
    error_dict = e.to_dict()
    return {
        'success': False,
        'error_type': 'payment_error',
        'retry_possible': True,
        **error_dict
    }
    # Returns:
    # {
    #     'success': False,
    #     'error_type': 'payment_error',
    #     'error': 'INSUFFICIENT_BALANCE',
    #     'subcode': None,
    #     'message': 'INSUFFICIENT_BALANCE: Insufficient balance...',
    #     'user_message': 'Insufficient credits. You have $5.50 but need $10.00...',
    #     'status_code': 402,
    #     'retry_possible': True,
    #     'context': {'current_balance': 5.50, 'required_balance': 10.00, ...}
    # }
```

### Error Context Access

```python
try:
    await charge_token(token, amount)
    
except InsufficientBalanceError as e:
    # Access specific context
    current = e.context['current_balance']
    required = e.context['required_balance']
    shortfall = e.context['shortfall']
    
    print(f"Current balance: ${current:.2f}")
    print(f"Required: ${required:.2f}")
    print(f"Need: ${shortfall:.2f} more")
    
except PaymentChargingError as e:
    # Check subcode for specific handling
    if e.subcode == 'SPENDING_LIMIT_EXCEEDED':
        print("Daily spending limit reached")
        print("Try again tomorrow or contact support")
    else:
        print(f"Charge failed: {e.user_message}")
```

## 🚀 Quick Reference

| Error Type | Code | Common Subcodes | Retry Safe? |
|------------|------|-----------------|-------------|
| Token Required | `PAYMENT_TOKEN_REQUIRED` | - | ✅ |
| Token Invalid | `PAYMENT_TOKEN_INVALID` | `TOKEN_EXPIRED`, `TOKEN_NOT_FOUND` | ✅ |
| Insufficient Balance | `INSUFFICIENT_BALANCE` | - | ✅ |
| Charging Failed | `PAYMENT_CHARGING_FAILED` | `INSUFFICIENT_FUNDS`, `SPENDING_LIMIT_EXCEEDED` | ⚠️ |
| Platform Unavailable | `PAYMENT_PLATFORM_UNAVAILABLE` | - | ✅ |
| Config Error | `PAYMENT_CONFIG_ERROR` | - | ❌ |

## 🔄 Migration from Legacy Errors

The new system maintains backward compatibility:

```python
# Old way (still works for compatibility)
from robutler.agents.skills.robutler.payments import PaymentValidationError

# New way (recommended)
from robutler.agents.skills.robutler.payments.exceptions import PaymentTokenInvalidError

# Legacy exceptions inherit from new ones
try:
    # ...
except PaymentValidationError as e:  # Catches PaymentTokenInvalidError too
    pass
```

## 📊 Error Response Format

All payment errors can be converted to a standard dictionary format:

```python
error.to_dict()
# Returns:
{
    'error': 'INSUFFICIENT_BALANCE',
    'subcode': None,
    'message': 'INSUFFICIENT_BALANCE: Insufficient balance: $5.50 < $10.00 required',
    'user_message': 'Insufficient credits. You have $5.50 but need $10.00...',
    'status_code': 402,
    'context': {
        'current_balance': 5.50,
        'required_balance': 10.00,
        'shortfall': 4.50,
        'token_prefix': 'abc123...'
    }
}
```

This comprehensive error system makes it easy to provide specific, actionable feedback to users while maintaining detailed technical information for debugging and monitoring. 