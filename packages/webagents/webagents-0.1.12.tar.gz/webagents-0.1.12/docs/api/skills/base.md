# Base Skill Interface

!!! warning "Beta Software Notice"  

    Robutler is currently in **beta stage**. While the core functionality is stable and actively used, APIs and features may change. We recommend testing thoroughly before deploying to critical environments.

## Base Skill Class

::: robutler.agents.skills.base.Skill

    options:
        members:
            - __init__
            - initialize
            - register_tool
            - register_hook
            - register_handoff
            - get_context
            - get_tools
            - get_dependencies

## Data Types

### Handoff

::: robutler.agents.skills.base.Handoff

### HandoffResult

::: robutler.agents.skills.base.HandoffResult

## Usage Example

### Custom Skill Implementation

```python
from robutler.agents.skills.base import Skill
from robutler.agents.tools.decorators import tool, hook

class WeatherSkill(Skill):
    """Custom weather skill with hooks and tools."""
    
    def __init__(self, config=None):
        super().__init__(config, scope="all")
        self.api_key = config.get("api_key") if config else None
        self.cache = {}
    
    async def initialize(self, agent):
        """Initialize skill with agent."""
        self.agent = agent
        
        # Register tools
        self.register_tool(self.get_weather)
        self.register_tool(self.get_forecast)
        
        # Register hooks
        self.register_hook("on_connection", self.setup_weather_context)
        self.register_hook("before_toolcall", self.validate_location)
    
    @hook("on_connection", priority=10)
    async def setup_weather_context(self, context):
        """Setup weather-specific context."""
        context.weather_service = "active"
        return context
    
    @hook("before_toolcall", priority=15)
    async def validate_location(self, context):
        """Validate location before weather calls."""
        if context.tool_name in ["get_weather", "get_forecast"]:
            location = context.tool_args.get("location")
            if not location:
                context.tool_args["location"] = "New York"  # Default
        return context
    
    @tool
    def get_weather(self, location: str) -> str:
        """Get current weather for location."""
        # Check cache first
        if location in self.cache:
            return self.cache[location]
        
        # Simulate API call
        weather = f"Weather in {location}: 72°F, sunny"
        self.cache[location] = weather
        return weather
    
    @tool
    def get_forecast(self, location: str, days: int = 5) -> str:
        """Get weather forecast for location."""
        return f"{days}-day forecast for {location}: Mostly sunny"
```

### Skill with Dependencies

```python
class AdvancedWeatherSkill(Skill):
    """Weather skill that depends on other skills."""
    
    def __init__(self, config=None):
        super().__init__(
            config,
            dependencies=["llm", "memory"]  # Requires LLM and memory skills
        )
    
    async def initialize(self, agent):
        """Initialize with dependency validation."""
        self.agent = agent
        
        # Dependencies are automatically available
        self.llm_skill = agent.get_skill("llm")
        self.memory_skill = agent.get_skill("memory")
        
        if not self.llm_skill:
            raise RuntimeError("AdvancedWeatherSkill requires an LLM skill")
        
        # Register capabilities
        self.register_tool(self.analyze_weather_trends)
    
    @tool
    async def analyze_weather_trends(self, location: str) -> str:
        """Analyze weather trends using LLM."""
        # Get historical data from memory
        historical_data = self.memory_skill.search_memories(f"weather {location}")
        
        # Use LLM to analyze trends
        analysis_prompt = f"Analyze weather trends for {location}: {historical_data}"
        result = await self.llm_skill.complete([
            {"role": "user", "content": analysis_prompt}
        ])
        
        return result
```

### Dynamic Tool Registration

```python
class ConditionalSkill(Skill):
    """Skill that registers tools based on conditions."""
    
    async def initialize(self, agent):
        """Register tools based on configuration."""
        self.agent = agent
        
        # Always register basic tools
        self.register_tool(self.basic_function)
        
        # Conditionally register premium tools
        if self.config.get("premium_features", False):
            self.register_tool(self.premium_function)
            self.register_tool(self.advanced_analysis)
        
        # Register tools based on agent capabilities
        if agent.has_skill("payments"):
            self.register_tool(self.paid_service)
    
    @hook("before_toolcall", priority=20)
    async def check_access(self, context):
        """Dynamically enable/disable tools based on runtime conditions."""
        if context.tool_name == "premium_function":
            if not self.user_has_premium(context.user):
                # Disable premium tool for this request
                context.tool_available = False
                context.error_message = "Premium subscription required"
        
        return context
    
    def user_has_premium(self, user):
        """Check if user has premium access."""
        return user.get("subscription") == "premium"
```

## Best Practices

### 1. Skill Initialization
- Always call `super().__init__()` with appropriate parameters
- Set dependencies early in constructor
- Register capabilities in `initialize()` method

### 2. Hook Usage
- Use appropriate priorities (lower = earlier execution)
- Return modified context from hooks
- Handle errors gracefully in hooks

### 3. Tool Registration  
- Register tools in `initialize()` method
- Use meaningful tool names and descriptions
- Implement proper error handling in tools

### 4. Context Access
- Use `get_context()` to access request context
- Access agent capabilities through context
- Modify context appropriately in hooks

### 5. Error Handling
- Validate configuration in constructor
- Check dependencies in `initialize()`
- Implement graceful fallbacks for external services 