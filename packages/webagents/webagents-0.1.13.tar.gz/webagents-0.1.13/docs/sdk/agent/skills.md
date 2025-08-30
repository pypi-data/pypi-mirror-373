# Agent Skills

Skills are the building blocks of agent capabilities, providing modular functionality that can be mixed and matched.

## Working with Skills

### Adding Skills to Agents

```python
from robutler.agents import BaseAgent
from robutler.agents.skills import (
    ShortTermMemorySkill,
    DiscoverySkill,
    NLISkill
)

agent = BaseAgent(
    name="skilled-agent",
    model="openai/gpt-4o",
    skills={
        "memory": ShortTermMemorySkill({"max_messages": 50}),
        "discovery": DiscoverySkill(),
        "nli": NLISkill()
    }
)
```

### Skill Dependencies

Skills can declare dependencies that are automatically included:

```python
class MySkill(Skill):
    def __init__(self, config=None):
        super().__init__(
            config=config,
            dependencies=["memory", "auth"]  # Auto-included
        )
```

### Skill Scopes

Control who can use skills:

```python
# Public skill - available to all
public_skill = MySkill(scope="all")

# Owner only
owner_skill = AdminSkill(scope="owner")  

# System admin only
admin_skill = SystemSkill(scope="admin")
```

## Core Skills

### LLM Skills

```python
from robutler.agents.skills import (
    OpenAISkill,
    AnthropicSkill,
    LiteLLMSkill
)

# Direct provider access
openai = OpenAISkill({
    "api_key": "sk-...",
    "model": "gpt-4o",
    "temperature": 0.7
})

# Multi-provider routing
litellm = LiteLLMSkill({
    "model": "claude-3-sonnet",
    "fallback_models": ["gpt-4", "gpt-3.5-turbo"]
})
```

### Memory Skills

```python
from robutler.agents.skills import (
    ShortTermMemorySkill,
    LongTermMemorySkill,
    VectorMemorySkill
)

# Conversation context
short_term = ShortTermMemorySkill({
    "max_messages": 100,
    "summarize_after": 50
})

# Persistent facts
long_term = LongTermMemorySkill({
    "connection_string": "postgresql://...",
    "ttl_days": 30
})

# Semantic search
vector = VectorMemorySkill({
    "embedding_model": "text-embedding-3-small",
    "top_k": 5
})
```

## Platform Skills

### Discovery Skill

Find and connect with other agents:

```python
from robutler.agents.skills import DiscoverySkill

discovery = DiscoverySkill()

# In a tool or hook
agents = await discovery.find_agents(
    intent="financial advice",
    max_results=5
)

for agent in agents:
    print(f"{agent['name']}: {agent['description']}")
```

### NLI Skill

Natural language interface for agent communication:

```python
from robutler.agents.skills import NLISkill

nli = NLISkill()

# Query another agent
result = await nli.query_agent(
    agent_name="expert-agent",
    query="What's the weather like?",
    context={"location": "Paris"}
)

response = result.get("response")
```

### Payment Skill

Handle microtransactions:

```python
from robutler.agents.skills import PaymentSkill

payment = PaymentSkill({
    "default_amount": 0.01,
    "currency": "USD"
})

# Charge for service
success = await payment.charge_user(
    user_id="user123",
    amount=0.05,
    description="Premium analysis"
)
```

## Creating Custom Skills

### Basic Skill Structure

```python
from robutler.agents.skills import Skill
from robutler.agents.tools.decorators import tool
from robutler.agents.skills.decorators import hook

class WeatherSkill(Skill):
    def __init__(self, config=None):
        super().__init__(config)
        self.api_key = config.get("api_key")
    
    async def initialize(self, agent):
        """Initialize with agent reference"""
        await super().initialize(agent)
        # Setup any connections
    
    def get_prompts(self) -> List[str]:
        """Provide skill-specific prompts"""
        return [
            "You have access to real-time weather data.",
            "Always specify the location when discussing weather.",
            "Include temperature in both Celsius and Fahrenheit."
        ]
    
    @tool
    async def get_weather(self, location: str) -> Dict:
        """Get current weather for location"""
        # Implementation
        return {
            "location": location,
            "temperature": 22,
            "conditions": "Partly cloudy"
        }
    
    @hook("on_message")
    async def detect_weather_intent(self, context):
        """Auto-detect weather queries"""
        message = context.messages[-1]["content"]
        
        if "weather" in message.lower():
            context["detected_intent"] = "weather"
        
        return context
```

### Advanced Skill Features

```python
class AdvancedSkill(Skill):
    def __init__(self, config=None):
        super().__init__(
            config=config,
            scope="owner",  # Owner-only skill
            dependencies=["memory", "auth"]  # Required skills
        )
    
    @tool(scope="owner")
    async def owner_tool(self, param: str) -> str:
        """Owner-only tool"""
        return f"Owner action: {param}"
    
    @hook("on_connection", priority=1)
    async def setup_advanced_features(self, context):
        """Initialize advanced features"""
        
        # Conditional tool registration
        if context.peer_user_id in self.power_users:
            self.register_tool(self.power_tool)
        
        # Dynamic configuration
        user_prefs = await self.get_user_preferences(context.peer_user_id)
        self.configure_for_user(user_prefs)
        
        return context
    
    def power_tool(self, action: str) -> str:
        """Dynamically registered power tool"""
        return f"Power action: {action}"
```

## Skill Composition

### Combining Skills

```python
class CompositeSkill(Skill):
    """Skill that combines multiple capabilities"""
    
    def __init__(self, config=None):
        super().__init__(config)
        
        # Compose from other skills
        self.weather = WeatherSkill(config.get("weather", {}))
        self.search = SearchSkill(config.get("search", {}))
    
    @tool
    async def travel_assistant(self, destination: str) -> Dict:
        """Provide travel information"""
        
        # Use multiple skills
        weather = await self.weather.get_weather(destination)
        attractions = await self.search.search_attractions(destination)
        
        return {
            "destination": destination,
            "weather": weather,
            "attractions": attractions,
            "recommendation": self.generate_recommendation(weather, attractions)
        }
```

### Skill Inheritance

```python
class BaseAnalyticsSkill(Skill):
    """Base skill for analytics"""
    
    @hook("on_connection")
    async def start_tracking(self, context):
        context["analytics_start"] = time.time()
        return context
    
    @hook("finalize_connection")
    async def send_analytics(self, context):
        duration = time.time() - context.get("analytics_start", time.time())
        await self.record_analytics(duration, context)
        return context

class CustomAnalyticsSkill(BaseAnalyticsSkill):
    """Extended analytics with custom metrics"""
    
    @hook("on_message")
    async def track_sentiment(self, context):
        """Add sentiment tracking"""
        message = context.messages[-1]
        context["sentiment"] = self.analyze_sentiment(message["content"])
        return context
```

## Best Practices

### Skill Design

1. **Single Responsibility** - Each skill should have one clear purpose
2. **Configuration** - Make skills configurable via constructor
3. **Dependencies** - Declare dependencies explicitly
4. **Prompts** - Provide clear prompts for LLM guidance
5. **Error Handling** - Handle errors gracefully

### Performance

```python
class OptimizedSkill(Skill):
    def __init__(self, config=None):
        super().__init__(config)
        self.cache = {}  # Simple cache
    
    @tool
    async def expensive_operation(self, key: str) -> str:
        """Cached expensive operation"""
        
        # Check cache
        if key in self.cache:
            return self.cache[key]
        
        # Perform operation
        result = await self.perform_expensive_operation(key)
        
        # Cache result
        self.cache[key] = result
        
        return result
```

### Testing Skills

```python
import pytest
from robutler.agents import BaseAgent

class TestWeatherSkill:
    @pytest.mark.asyncio
    async def test_weather_tool(self):
        # Create agent with skill
        agent = BaseAgent(
            name="test-agent",
            model="openai/gpt-4o",
            skills={"weather": WeatherSkill({"api_key": "test"})}
        )
        
        # Test tool directly
        weather_skill = agent.skills["weather"]
        result = await weather_skill.get_weather("London")
        
        assert result["location"] == "London"
        assert "temperature" in result
    
    @pytest.mark.asyncio
    async def test_weather_intent(self):
        # Test with conversation
        response = await agent.run([
            {"role": "user", "content": "What's the weather in Paris?"}
        ])
        
        # Should use weather tool
        assert "Paris" in response.choices[0].message.content
```

## Skill Marketplace

Skills can be shared and reused:

```python
# Install community skill
# pip install robutler-skill-translator

from robutler_skill_translator import TranslatorSkill

agent = BaseAgent(
    name="polyglot",
    model="openai/gpt-4o",
    skills={
        "translator": TranslatorSkill({
            "target_languages": ["es", "fr", "de"]
        })
    }
) 