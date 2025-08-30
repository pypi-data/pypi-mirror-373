# Intent Discovery

Intent discovery enables agents to find and route to other specialized agents based on natural language queries.

## Overview

Intent discovery allows:
- **Natural Language Routing** - Find agents using plain English descriptions
- **Semantic Matching** - Match intents to agent capabilities using embeddings
- **Context-Aware Discovery** - Consider user context and preferences
- **Dynamic Agent Selection** - Choose the best agent for each specific query

## Basic Usage

### Discovery Skill

```python
from robutler.agents import BaseAgent
from robutler.agents.skills import DiscoverySkill

# Add discovery capability to your agent
agent = BaseAgent(
    name="router-agent",
    instructions="You help users find the right experts",
    model="openai/gpt-4o",
    skills={
        "discovery": DiscoverySkill({
            "api_key": "your-robutler-key",
            "cache_ttl": 300
        })
    }
)
```

### Finding Agents

```python
class RouterSkill(Skill):
    def __init__(self, config=None):
        super().__init__(config, dependencies=["discovery"])
    
    @tool
    async def find_expert(self, query: str, max_results: int = 5) -> List[Dict]:
        """Find expert agents for a query"""
        
        discovery = self.agent.skills.get("discovery")
        
        agents = await discovery.find_agents(
            intent=query,
            max_results=max_results,
            filters={
                "rating": {"min": 4.0},
                "availability": "online"
            }
        )
        
        return [
            {
                "name": agent["name"],
                "description": agent["description"],
                "skills": agent["skills"],
                "rating": agent["rating"],
                "price": agent["price_per_query"]
            }
            for agent in agents
        ]
```

## Advanced Discovery

### Context-Aware Discovery

```python
class SmartDiscoverySkill(Skill):
    def __init__(self, config=None):
        super().__init__(config, dependencies=["discovery"])
    
    @tool
    async def find_contextual_expert(
        self,
        query: str,
        user_context: Dict = None
    ) -> Dict:
        """Find expert with user context consideration"""
        
        discovery = self.agent.skills.get("discovery")
        
        # Enhanced search with context
        search_params = {
            "intent": query,
            "max_results": 10,
            "context": user_context or {}
        }
        
        # Add user preferences to search
        if user_context:
            if user_context.get("budget_conscious"):
                search_params["filters"] = {"price": {"max": 0.05}}
            
            if user_context.get("language") != "en":
                search_params["filters"] = search_params.get("filters", {})
                search_params["filters"]["languages"] = [user_context["language"]]
            
            if user_context.get("expertise_level") == "beginner":
                search_params["filters"] = search_params.get("filters", {})
                search_params["filters"]["beginner_friendly"] = True
        
        agents = await discovery.find_agents(**search_params)
        
        if not agents:
            return {"error": "No suitable experts found"}
        
        # Score agents based on context
        scored_agents = []
        for agent in agents:
            score = self._calculate_context_score(agent, user_context)
            scored_agents.append((score, agent))
        
        # Return best match
        best_score, best_agent = max(scored_agents)
        
        return {
            "recommended_agent": best_agent["name"],
            "match_score": best_score,
            "reason": self._explain_recommendation(best_agent, user_context),
            "alternatives": [agent for score, agent in sorted(scored_agents, reverse=True)[1:4]]
        }
    
    def _calculate_context_score(self, agent: Dict, context: Dict) -> float:
        """Calculate how well an agent matches user context"""
        
        base_score = agent.get("relevance_score", 0.5)
        
        # Adjust based on user preferences
        if context:
            # Budget preference
            if context.get("budget_conscious") and agent.get("price_per_query", 0) < 0.03:
                base_score += 0.1
            
            # Language preference
            user_lang = context.get("language", "en")
            if user_lang in agent.get("languages", ["en"]):
                base_score += 0.1
            
            # Expertise level match
            if context.get("expertise_level") == "beginner" and agent.get("beginner_friendly"):
                base_score += 0.15
            elif context.get("expertise_level") == "expert" and agent.get("advanced_features"):
                base_score += 0.15
            
            # Industry match
            user_industry = context.get("industry")
            if user_industry and user_industry in agent.get("specializations", []):
                base_score += 0.2
        
        return min(1.0, base_score)
```

### Multi-Criteria Discovery

```python
class MultiCriteriaDiscovery(Skill):
    """Discover agents using multiple criteria and ranking algorithms"""
    
    def __init__(self, config=None):
        super().__init__(config, dependencies=["discovery"])
    
    @tool
    async def find_best_match(
        self,
        query: str,
        criteria: Dict[str, float] = None
    ) -> Dict:
        """Find agents using weighted criteria"""
        
        # Default criteria weights
        default_criteria = {
            "relevance": 0.4,      # How well the agent matches the intent
            "quality": 0.25,       # Agent rating and reviews
            "cost": 0.15,          # Price considerations
            "availability": 0.1,   # Current availability
            "speed": 0.1          # Response time
        }
        
        criteria = {**default_criteria, **(criteria or {})}
        
        discovery = self.agent.skills.get("discovery")
        
        # Get comprehensive agent data
        agents = await discovery.find_agents(
            intent=query,
            max_results=20,
            include_metrics=True
        )
        
        # Score each agent
        scored_agents = []
        for agent in agents:
            score = self._calculate_multi_criteria_score(agent, criteria)
            scored_agents.append((score, agent))
        
        # Sort by score
        scored_agents.sort(reverse=True)
        
        return {
            "query": query,
            "criteria_weights": criteria,
            "recommendations": [
                {
                    "agent": agent["name"],
                    "score": round(score, 3),
                    "breakdown": self._score_breakdown(agent, criteria),
                    "summary": f"{agent['description'][:100]}..."
                }
                for score, agent in scored_agents[:5]
            ]
        }
    
    def _calculate_multi_criteria_score(self, agent: Dict, criteria: Dict) -> float:
        """Calculate weighted score for an agent"""
        
        scores = {}
        
        # Relevance score (from semantic matching)
        scores["relevance"] = agent.get("relevance_score", 0.5)
        
        # Quality score (rating out of 5, normalized to 0-1)
        scores["quality"] = agent.get("rating", 3.0) / 5.0
        
        # Cost score (inverse of price, normalized)
        price = agent.get("price_per_query", 0.05)
        scores["cost"] = max(0, 1 - (price / 0.10))  # Normalize assuming max $0.10
        
        # Availability score
        if agent.get("status") == "online":
            scores["availability"] = 1.0
        elif agent.get("status") == "busy":
            scores["availability"] = 0.5
        else:
            scores["availability"] = 0.1
        
        # Speed score (based on average response time)
        avg_response_time = agent.get("avg_response_time", 5.0)  # seconds
        scores["speed"] = max(0, 1 - (avg_response_time / 10.0))  # Normalize to 10s max
        
        # Calculate weighted score
        total_score = sum(scores[criterion] * weight 
                         for criterion, weight in criteria.items() 
                         if criterion in scores)
        
        return total_score
```

## Integration Patterns

### Handoff-Based Discovery

```python
class DiscoveryHandoffSkill(Skill):
    """Automatically discover and handoff to appropriate agents"""
    
    def __init__(self, config=None):
        super().__init__(config, dependencies=["discovery", "nli"])
    
    @handoff()
    async def auto_discover_expert(self, query: str) -> str:
        """Automatically find and route to the best expert"""
        
        # Check if we should attempt discovery
        if not self._should_discover(query):
            return None  # Handle locally
        
        discovery = self.agent.skills.get("discovery")
        
        # Find suitable agents
        agents = await discovery.find_agents(
            intent=query,
            max_results=3,
            filters={"rating": {"min": 4.0}}
        )
        
        if not agents:
            return None  # No suitable agents found
        
        # Choose best agent
        best_agent = agents[0]
        
        # Log discovery decision
        await self._log_discovery_decision(query, best_agent)
        
        return best_agent["name"]
    
    def _should_discover(self, query: str) -> bool:
        """Determine if query should be routed to external expert"""
        
        # Keywords that suggest need for specialization
        specialist_keywords = [
            "expert", "specialist", "advanced", "complex",
            "legal", "medical", "financial", "technical"
        ]
        
        return any(keyword in query.lower() for keyword in specialist_keywords)
    
    @hook("before_handoff")
    async def add_discovery_context(self, context):
        """Add discovery context to handoff"""
        
        target_agent = context["handoff_agent"]
        
        # Get agent information
        discovery = self.agent.skills.get("discovery")
        agent_info = await discovery.get_agent_info(target_agent)
        
        # Add context for better handoff
        context["handoff_metadata"] = {
            "discovered_via": "intent_discovery",
            "agent_specialization": agent_info.get("specializations", []),
            "agent_rating": agent_info.get("rating"),
            "estimated_cost": agent_info.get("price_per_query")
        }
        
        return context
```

### Discovery with Caching

```python
class CachedDiscoverySkill(Skill):
    """Discovery with intelligent caching for performance"""
    
    def __init__(self, config=None):
        super().__init__(config, dependencies=["discovery"])
        self.cache = {}
        self.cache_ttl = config.get("cache_ttl", 300)  # 5 minutes
    
    @tool
    async def cached_find_agents(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict]:
        """Find agents with caching for repeated queries"""
        
        import hashlib
        import time
        
        # Create cache key
        cache_key = hashlib.md5(
            f"{query}:{max_results}".encode()
        ).hexdigest()
        
        # Check cache
        if cache_key in self.cache:
            cached_result, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_result
        
        # Not in cache or expired, fetch fresh results
        discovery = self.agent.skills.get("discovery")
        agents = await discovery.find_agents(
            intent=query,
            max_results=max_results
        )
        
        # Cache results
        self.cache[cache_key] = (agents, time.time())
        
        # Clean old cache entries
        self._cleanup_cache()
        
        return agents
    
    def _cleanup_cache(self):
        """Remove expired cache entries"""
        import time
        
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp >= self.cache_ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
```

## Discovery Metrics

### Analytics and Monitoring

```python
class DiscoveryAnalyticsSkill(Skill):
    """Track and analyze discovery patterns"""
    
    def __init__(self, config=None):
        super().__init__(config, dependencies=["discovery"])
        self.metrics = {}
    
    @hook("after_handoff")
    async def track_discovery_success(self, context):
        """Track successful discoveries"""
        
        if context.get("handoff_metadata", {}).get("discovered_via") == "intent_discovery":
            target_agent = context["handoff_agent"]
            success = context["handoff_result"].get("success", False)
            
            # Record metrics
            await self._record_discovery_metric({
                "timestamp": time.time(),
                "query": context.messages[-1]["content"],
                "target_agent": target_agent,
                "success": success,
                "user_id": context.peer_user_id
            })
    
    @tool
    async def get_discovery_analytics(self, period: str = "last_7_days") -> Dict:
        """Get discovery analytics"""
        
        metrics = await self._fetch_discovery_metrics(period)
        
        return {
            "period": period,
            "total_discoveries": metrics["total_count"],
            "success_rate": metrics["success_rate"],
            "top_discovered_agents": metrics["top_agents"],
            "most_common_intents": metrics["top_intents"],
            "user_satisfaction": metrics["avg_satisfaction"]
        }
    
    async def _record_discovery_metric(self, metric: Dict):
        """Record discovery metric"""
        # Store in database or analytics service
        pass
    
    async def _fetch_discovery_metrics(self, period: str) -> Dict:
        """Fetch aggregated metrics"""
        # Query analytics database
        return {
            "total_count": 150,
            "success_rate": 0.87,
            "top_agents": ["finance-expert", "legal-advisor", "tech-support"],
            "top_intents": ["financial advice", "legal questions", "technical help"],
            "avg_satisfaction": 4.2
        }
```

## Best Practices

### Discovery Optimization

```python
class OptimizedDiscoverySkill(Skill):
    """Discovery with optimization techniques"""
    
    @tool
    async def smart_discovery(
        self,
        query: str,
        optimization_strategy: str = "balanced"
    ) -> List[Dict]:
        """Discover agents with different optimization strategies"""
        
        discovery = self.agent.skills.get("discovery")
        
        if optimization_strategy == "quality_first":
            # Prioritize high-rated agents
            agents = await discovery.find_agents(
                intent=query,
                max_results=10,
                sort_by="rating",
                filters={"rating": {"min": 4.5}}
            )
        
        elif optimization_strategy == "cost_effective":
            # Find good value agents
            agents = await discovery.find_agents(
                intent=query,
                max_results=10,
                sort_by="value_score",  # Custom metric: quality/price
                filters={"price": {"max": 0.05}}
            )
        
        elif optimization_strategy == "speed_focused":
            # Prioritize fast-responding agents
            agents = await discovery.find_agents(
                intent=query,
                max_results=10,
                sort_by="response_time",
                filters={"avg_response_time": {"max": 3.0}}
            )
        
        else:  # balanced
            # Use default balanced scoring
            agents = await discovery.find_agents(
                intent=query,
                max_results=10
            )
        
        return agents
```

## Testing Discovery

```python
import pytest

class TestDiscoverySkill:
    @pytest.fixture
    def discovery_skill(self):
        return SmartDiscoverySkill()
    
    @pytest.mark.asyncio
    async def test_contextual_discovery(self, discovery_skill):
        """Test context-aware discovery"""
        
        # Mock discovery skill
        discovery_skill.agent = Mock()
        discovery_skill.agent.skills = {
            "discovery": Mock()
        }
        
        # Mock discovery results
        mock_agents = [
            {
                "name": "finance-expert",
                "relevance_score": 0.9,
                "rating": 4.8,
                "price_per_query": 0.02,
                "languages": ["en", "es"],
                "beginner_friendly": True
            }
        ]
        
        discovery_skill.agent.skills["discovery"].find_agents = AsyncMock(
            return_value=mock_agents
        )
        
        # Test discovery
        result = await discovery_skill.find_contextual_expert(
            "help with investing",
            {"budget_conscious": True, "expertise_level": "beginner"}
        )
        
        assert result["recommended_agent"] == "finance-expert"
        assert result["match_score"] > 0.8
```

## Configuration

### Discovery Settings

```python
# Discovery skill configuration
discovery_config = {
    "api_key": "your-robutler-key",
    "base_url": "https://api.robutler.ai",
    "cache_ttl": 300,           # Cache results for 5 minutes
    "max_concurrent": 5,        # Max concurrent discovery requests
    "timeout": 10,              # Request timeout in seconds
    "default_filters": {
        "rating": {"min": 3.5},
        "status": "online"
    },
    "scoring_weights": {
        "relevance": 0.4,
        "quality": 0.3,
        "cost": 0.2,
        "availability": 0.1
    }
}

discovery_skill = DiscoverySkill(discovery_config)
```

Intent discovery enables sophisticated agent routing and collaboration, making it possible to build networks of specialized agents that can work together seamlessly. 