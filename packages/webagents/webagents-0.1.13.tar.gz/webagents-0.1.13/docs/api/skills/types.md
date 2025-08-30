# Skills Data Types

!!! warning "Beta Software Notice"  

    Robutler is currently in **beta stage**. While the core functionality is stable and actively used, APIs and features may change. We recommend testing thoroughly before deploying to critical environments.

## Base Types

See [Base Skill Interface](base.md) for Handoff and HandoffResult definitions.

## Core Skill Types

### Memory Types

#### MessageContext

::: robutler.agents.skills.core.memory.short_term_memory.skill.MessageContext

### MCP Types

#### MCPServerConfig

::: robutler.agents.skills.core.mcp.skill.MCPServerConfig

#### MCPTransport

::: robutler.agents.skills.core.mcp.skill.MCPTransport

#### MCPExecution

::: robutler.agents.skills.core.mcp.skill.MCPExecution

## Platform Skill Types

### Discovery Types

#### DiscoveryResult

::: robutler.agents.skills.robutler.discovery.skill.DiscoveryResult

### Auth Types

#### AuthScope

::: robutler.agents.skills.robutler.auth.skill.AuthScope

#### AuthContext

::: robutler.agents.skills.robutler.auth.skill.AuthContext

### Payment Types

#### PaymentContext

::: robutler.agents.skills.robutler.payments.skill.PaymentContext

### NLI Types

#### NLICommunication

::: robutler.agents.skills.robutler.nli.skill.NLICommunication

#### AgentEndpoint

::: robutler.agents.skills.robutler.nli.skill.AgentEndpoint

## Exception Types

### Base Exceptions

#### SkillError

Base exception for all skill-related errors.

```python
class SkillError(Exception):
    """Base exception for skill errors."""
    pass
```

### Auth Exceptions

#### AuthenticationError

::: robutler.agents.skills.robutler.auth.skill.AuthenticationError

#### AuthorizationError

::: robutler.agents.skills.robutler.auth.skill.AuthorizationError

### Payment Exceptions

#### PaymentValidationError

::: robutler.agents.skills.robutler.payments.exceptions.PaymentValidationError

#### PaymentChargingError

::: robutler.agents.skills.robutler.payments.exceptions.PaymentChargingError

#### InsufficientBalanceError

::: robutler.agents.skills.robutler.payments.exceptions.InsufficientBalanceError

#### PaymentRequiredError

::: robutler.agents.skills.robutler.payments.exceptions.PaymentRequiredError

## Usage Examples

### Working with Data Types

```python
from robutler.agents.skills.base import Handoff, HandoffResult
from robutler.agents.skills.robutler.discovery.skill import DiscoveryResult
from robutler.agents.skills.robutler.payments.skill import PaymentContext

# Create handoff configuration
handoff_config = Handoff(
    target="data-analyst",
    handoff_type="delegation",
    description="Hand off complex data analysis tasks",
    scope=["owner", "admin"],
    metadata={"priority": "high", "timeout": 60}
)

# Create discovery result
discovery_result = DiscoveryResult(
    agent_id="agent-123",
    intent="data analysis",
    agent_description="Specialized in data analysis",
    similarity=0.95,
    url="https://robutler.ai/agents/agent-123",
    rank=1
)

# Create payment context
payment_context = PaymentContext(
    user_id="user-456",
    credit_balance=5000,
    billing_plan="premium",
    usage_limits={"daily": 10000, "monthly": 100000}
)
```

### Error Handling Examples

```python
from robutler.agents.skills.robutler.auth.skill import AuthenticationError, AuthorizationError
from robutler.agents.skills.robutler.payments import InsufficientBalanceError

async def handle_skill_operations():
    try:
        # Perform agent operations
        response = await agent.run(messages=messages)
        return response
        
    except AuthenticationError as e:
        # Handle authentication failures
        print(f"Authentication failed: {e}")
        return {"error": "Please log in to continue"}
        
    except AuthorizationError as e:
        # Handle authorization failures
        print(f"Access denied: {e}")
        return {"error": "Insufficient permissions"}
        
    except InsufficientBalanceError as e:
        # Handle payment failures
        print(f"Payment required: {e}")
        return {"error": "Please add credits to continue"}
        
    except Exception as e:
        # Handle general errors
        print(f"Unexpected error: {e}")
        return {"error": "Service temporarily unavailable"}
```

### Type Validation

```python
from typing import Optional
from dataclasses import dataclass

@dataclass
class CustomSkillConfig:
    """Custom configuration for skill setup."""
    enabled: bool = True
    timeout: int = 30
    max_retries: int = 3
    error_handling: str = "graceful"
    metadata: Optional[dict] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
            
        # Validate configuration
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        if self.max_retries < 0:
            raise ValueError("Max retries cannot be negative")
        if self.error_handling not in ["strict", "graceful"]:
            raise ValueError("Invalid error handling mode")

# Usage
config = CustomSkillConfig(
    enabled=True,
    timeout=45,
    max_retries=5,
    error_handling="graceful",
    metadata={"version": "1.0", "priority": "high"}
)
```

## Type Definitions

### Enums

```python
from enum import Enum

class SkillScope(Enum):
    """Skill access scope enumeration."""
    ALL = "all"
    OWNER = "owner"
    ADMIN = "admin"

class HookPriority(Enum):
    """Hook execution priority levels."""
    HIGHEST = 1
    HIGH = 10
    NORMAL = 50
    LOW = 90
    LOWEST = 99

class SkillStatus(Enum):
    """Skill operational status."""
    INACTIVE = "inactive"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"
```

### Union Types

```python
from typing import Union, List, Dict, Any

# Common type aliases
SkillConfig = Dict[str, Any]
ToolFunction = callable
HookHandler = callable
MessageList = List[Dict[str, Any]]
SkillIdentifier = Union[str, type]
ScopeValue = Union[str, List[str]]
```

### Protocol Definitions

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class SkillProtocol(Protocol):
    """Protocol for skill-like objects."""
    
    async def initialize(self, agent) -> None:
        """Initialize the skill."""
        ...
    
    def register_tool(self, func: callable, scope: str = "all") -> None:
        """Register a tool function."""
        ...
    
    def register_hook(self, event: str, handler: callable, priority: int = 50) -> None:
        """Register a lifecycle hook."""
        ...

@runtime_checkable
class ToolProtocol(Protocol):
    """Protocol for tool functions."""
    
    def __call__(self, *args, **kwargs) -> Any:
        """Execute the tool."""
        ...
    
    @property
    def __name__(self) -> str:
        """Tool name."""
        ...
    
    @property
    def __doc__(self) -> str:
        """Tool description."""
        ...
```

## Next Steps

- **[Base Skill Interface](base.md)** - Core skill interface documentation
- **[Core Skills](core.md)** - Essential skill capabilities
- **[Platform Skills](platform.md)** - Platform integration skills 