# Skill Dependencies

Skills can declare dependencies on other skills, enabling automatic inclusion of required capabilities.

Dependencies are resolved at agent construction time. If a skill requires another (e.g., payments depends on auth), it will be included automatically unless you provide a custom replacement under the same key.

## Understanding Dependencies

Dependencies allow skills to:
- Automatically include required functionality
- Build on other skills' capabilities  
- Create modular, composable architectures
- Avoid duplicating functionality

## Declaring Dependencies

### Basic Dependencies

```python
from robutler.agents.skills import Skill

class DataAnalysisSkill(Skill):
    def __init__(self, config=None):
        super().__init__(
            config=config,
            dependencies=["memory", "auth"]  # Required skills
        )
```

### Dependency Resolution

When an agent includes a skill with dependencies, all dependent skills are automatically included:

```python
from robutler.agents import BaseAgent

# Only specify DataAnalysisSkill
agent = BaseAgent(
    name="analyst",
    model="openai/gpt-4o",
    skills={
        "analysis": DataAnalysisSkill()
    }
)

# Agent automatically includes:
# - memory skill
# - auth skill  
# - analysis skill
```

## Dependency Types

### Core Dependencies

Skills that depend on core functionality:

```python
class DatabaseSkill(Skill):
    def __init__(self, config=None):
        super().__init__(
            config=config,
            dependencies=["auth", "memory"]  # Core dependencies
        )
    
    @tool
    def query_database(self, sql: str) -> List[Dict]:
        """Query database with auth and memory"""
        
        # Access auth skill
        auth = self.agent.skills.get("auth")
        if not auth.is_authorized(self.get_context().peer_user_id):
            return {"error": "Unauthorized"}
        
        # Access memory for caching
        memory = self.agent.skills.get("memory")
        cached = memory.get_cached_query(sql)
        if cached:
            return cached
        
        # Execute query
        result = self.execute_sql(sql)
        memory.cache_query(sql, result)
        
        return result
```

### Platform Dependencies

Skills that depend on Robutler platform features:

```python
class CollaborativeSkill(Skill):
    def __init__(self, config=None):
        super().__init__(
            config=config,
            dependencies=["nli", "discovery", "payment"]
        )
    
    @tool
    async def consult_expert(self, topic: str, question: str) -> str:
        """Consult external expert (requires platform skills)"""
        
        # Find expert using discovery
        discovery = self.agent.skills.get("discovery")
        experts = await discovery.find_agents(intent=question, max_results=3)
        
        if not experts:
            return "No experts found"
        
        # Check payment
        payment = self.agent.skills.get("payment")
        cost = experts[0].get("cost", 0.01)
        
        if not await payment.charge_user(self.get_context().peer_user_id, cost):
            return "Payment required"
        
        # Consult via NLI
        nli = self.agent.skills.get("nli")
        result = await nli.query_agent(experts[0]["name"], question)
        
        return result.get("response", "No response")
```

## Dependency Patterns

### Layered Dependencies

```python
# Base layer
class BaseDataSkill(Skill):
    def __init__(self, config=None):
        super().__init__(config, dependencies=["auth"])

# Analysis layer  
class AnalyticsSkill(Skill):
    def __init__(self, config=None):
        super().__init__(config, dependencies=["base_data", "memory"])

# Visualization layer
class VisualizationSkill(Skill):
    def __init__(self, config=None):
        super().__init__(config, dependencies=["analytics"])

# Agent gets all layers automatically
agent = BaseAgent(
    name="data-viz",
    model="openai/gpt-4o", 
    skills={
        "visualization": VisualizationSkill()
        # Also includes: analytics, base_data, memory, auth
    }
)
```

### Optional Dependencies

```python
class FlexibleSkill(Skill):
    def __init__(self, config=None):
        # Base dependencies
        deps = ["memory"]
        
        # Optional enhanced features
        if config.get("enable_payments"):
            deps.append("payment")
        
        if config.get("enable_collaboration"):
            deps.extend(["nli", "discovery"])
        
        super().__init__(config=config, dependencies=deps)
    
    @tool
    def enhanced_function(self, query: str) -> str:
        """Function with optional enhancements"""
        
        # Base functionality
        result = self.basic_processing(query)
        
        # Optional payment features
        payment = self.agent.skills.get("payment")
        if payment:
            result += " [Premium features enabled]"
        
        # Optional collaboration
        nli = self.agent.skills.get("nli")
        if nli and "expert" in query:
            expert_input = await nli.quick_consult("general-expert", query)
            result += f" Expert says: {expert_input}"
        
        return result
```

## Dependency Configuration

### Passing Configuration to Dependencies

```python
class ConfiguredSkill(Skill):
    def __init__(self, config=None):
        super().__init__(
            config=config,
            dependencies=["memory", "auth"]
        )
    
    async def initialize(self, agent):
        await super().initialize(agent)
        
        # Configure dependency skills
        memory_skill = agent.skills.get("memory")
        if memory_skill:
            memory_skill.configure({
                "max_items": self.config.get("memory_size", 100),
                "ttl": self.config.get("memory_ttl", 3600)
            })
        
        auth_skill = agent.skills.get("auth")
        if auth_skill:
            auth_skill.configure({
                "required_scope": self.config.get("auth_scope", "user")
            })
```

### Dependency Versions

```python
class VersionedSkill(Skill):
    def __init__(self, config=None):
        super().__init__(
            config=config,
            dependencies=[
                "memory>=2.0",      # Minimum version
                "auth==1.5",        # Exact version
                "nli>=1.0,<2.0"     # Version range
            ]
        )
```

## Circular Dependencies

### Avoiding Circular Dependencies

```python
# BAD: Circular dependency
class SkillA(Skill):
    def __init__(self, config=None):
        super().__init__(config, dependencies=["skill_b"])

class SkillB(Skill):  
    def __init__(self, config=None):
        super().__init__(config, dependencies=["skill_a"])  # Circular!

# GOOD: Use composition or interfaces
class SharedUtilitySkill(Skill):
    """Shared functionality both skills need"""
    pass

class SkillA(Skill):
    def __init__(self, config=None):
        super().__init__(config, dependencies=["shared_utility"])

class SkillB(Skill):
    def __init__(self, config=None):
        super().__init__(config, dependencies=["shared_utility"])
```

## Runtime Dependencies

### Dynamic Dependency Loading

```python
class AdaptiveSkill(Skill):
    def __init__(self, config=None):
        # Start with minimal dependencies
        super().__init__(config, dependencies=["memory"])
    
    @hook("on_connection")
    async def load_dynamic_dependencies(self, context):
        """Load dependencies based on request context"""
        
        # Check if user needs premium features
        if context.get("user_tier") == "premium":
            # Dynamically load premium dependencies
            await self.load_skill("premium_analytics")
            await self.load_skill("advanced_visualization")
        
        # Load based on query type
        query = context.messages[-1]["content"]
        if "collaboration" in query:
            await self.load_skill("nli")
            await self.load_skill("discovery")
        
        return context
    
    async def load_skill(self, skill_name: str):
        """Dynamically load a skill"""
        if skill_name not in self.agent.skills:
            skill_class = self.get_skill_class(skill_name)
            skill_instance = skill_class()
            self.agent.add_skill(skill_name, skill_instance)
```

## Dependency Injection

### Interface-Based Dependencies

```python
from abc import ABC, abstractmethod

class StorageInterface(ABC):
    @abstractmethod
    async def store(self, key: str, value: Any) -> bool:
        pass
    
    @abstractmethod
    async def retrieve(self, key: str) -> Any:
        pass

class DatabaseStorage(Skill, StorageInterface):
    async def store(self, key: str, value: Any) -> bool:
        # Database implementation
        pass
    
    async def retrieve(self, key: str) -> Any:
        # Database implementation  
        pass

class CacheStorage(Skill, StorageInterface):
    async def store(self, key: str, value: Any) -> bool:
        # Cache implementation
        pass
    
    async def retrieve(self, key: str) -> Any:
        # Cache implementation
        pass

class DataProcessingSkill(Skill):
    def __init__(self, config=None, storage: StorageInterface = None):
        super().__init__(config)
        self.storage = storage or DatabaseStorage()
    
    @tool
    async def process_and_store(self, data: str) -> str:
        """Process data and store result"""
        processed = self.process_data(data)
        await self.storage.store(f"result_{time.time()}", processed)
        return processed
```

## Best Practices

1. **Declare All Dependencies** - Be explicit about what your skill needs
2. **Use Interfaces** - Depend on abstractions, not concrete implementations
3. **Avoid Circular Dependencies** - Use shared utilities instead
4. **Test with Mocks** - Mock dependencies for isolated testing
5. **Document Dependencies** - Explain why each dependency is needed
6. **Version Dependencies** - Specify version requirements when needed
7. **Keep Dependencies Minimal** - Only depend on what you actually use 