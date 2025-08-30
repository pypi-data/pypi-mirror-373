# Custom Skills

Create modular capabilities for your agents using the Skills system. Skills combine tools, prompts, hooks, and handoffs to provide focused functionality that can be shared across agents.

Skills are the building blocks of agent capabilities - they encapsulate domain expertise, provide reusable functionality, and enable modular agent architectures.

## Overview

Custom skills extend agents with specialized capabilities:

**Core Components:**
- **🔧 Tools** - Executable functions for agent capabilities
- **📝 Prompts** - Dynamic system message enhancement
- **🪝 Hooks** - Event-driven lifecycle integration
- **🔄 Handoffs** - Agent-to-agent routing and delegation

**Key Benefits:**
- Modular and reusable across agents
- Scoped access control and security
- Automatic registration and discovery
- Context-aware and dynamic behavior

## Basic Skill Structure

### Simple Skill

```python
from robutler.agents.skills.base import Skill
from robutler.agents.tools.decorators import tool, prompt, hook, handoff

class WeatherSkill(Skill):
    """Provides weather information capabilities"""
    
    @prompt(priority=10)
    def get_prompt(self, context) -> str:
        """Guide LLM on weather capabilities"""
        return "You can provide real-time weather information. Always specify location when discussing weather."
    
    @tool(scope="all")
    def get_weather(self, location: str, units: str = "celsius") -> dict:
        """Get current weather for a location"""
        # Implementation here
        return {
            "location": location,
            "temperature": 22,
            "condition": "sunny",
            "units": units
        }
    
    @hook("on_message")
    async def enhance_weather_queries(self, context):
        """Add location context to weather queries"""
        message = context.messages[-1]
        
        if "weather" in message["content"].lower() and "in" not in message["content"]:
            # Try to infer location from user profile
            user_location = self.get_user_location(context.user_id)
            if user_location:
                message["content"] += f" in {user_location}"
        
        return context
    
    @handoff("detailed-weather")
    def needs_detailed_forecast(self, query: str) -> bool:
        """Route complex weather queries to specialist"""
        return any(term in query.lower() for term in ["forecast", "radar", "hurricane", "storm"])
```

### Using the Skill

```python
from robutler.agents import BaseAgent

agent = BaseAgent(
    name="weather-assistant",
    model="openai/gpt-4o",
    skills={"weather": WeatherSkill()}
)
```

## 🔧 Tools in Skills

Tools provide executable functions that extend agent capabilities.

### Basic Tool Implementation

```python
class CalculatorSkill(Skill):
    """Mathematical calculation capabilities"""
    
    @tool
    def add(self, a: float, b: float) -> float:
        """Add two numbers together"""
        return a + b
    
    @tool
    def multiply(self, x: float, y: float) -> float:
        """Multiply two numbers"""
        return x * y
    
    @tool(scope="owner")
    def advanced_calculation(self, expression: str) -> dict:
        """Execute advanced mathematical expressions (owner only)"""
        try:
            result = eval(expression, {"__builtins__": {}}, {
                "sin": math.sin, "cos": math.cos, "sqrt": math.sqrt
            })
            return {"result": result, "expression": expression}
        except Exception as e:
            return {"error": str(e), "expression": expression}
```

### Async Tools

```python
class APISkill(Skill):
    """External API integration capabilities"""
    
    @tool
    async def fetch_data(self, url: str) -> dict:
        """Fetch data from external API"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return {
                    "status": response.status,
                    "data": await response.json(),
                    "url": url
                }
    
    @tool
    async def parallel_requests(self, urls: list) -> list:
        """Process multiple API requests in parallel"""
        tasks = [self.fetch_data(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
```

### Tool Error Handling

```python
class RobustSkill(Skill):
    """Skill with robust error handling"""
    
    @tool
    def safe_divide(self, a: float, b: float) -> dict:
        """Division with comprehensive error handling"""
        try:
            if b == 0:
                return {
                    "success": False,
                    "error": "Division by zero",
                    "suggestion": "Please provide a non-zero divisor"
                }
            
            result = a / b
            return {
                "success": True,
                "result": result,
                "calculation": f"{a} ÷ {b} = {result}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "suggestion": "Please check your inputs"
            }
```

## 📝 Prompts in Skills

Prompts provide dynamic system message enhancement to guide LLM behavior.

### Basic Prompt Implementation

```python
class DatabaseSkill(Skill):
    """Database query capabilities with guidance"""
    
    @prompt(priority=5)
    def get_database_prompt(self, context) -> str:
        """Provide database usage guidance"""
        return """You have access to a SQL database through the query_database tool.
        
Guidelines:
- Always validate SQL queries before execution
- Use SELECT queries for data retrieval only
- Never use DROP, DELETE, or TRUNCATE commands
- Format query results in readable tables"""
    
    @tool(scope="owner")
    def query_database(self, sql: str) -> list:
        """Execute read-only SQL query"""
        # Validate query safety
        if any(dangerous in sql.upper() for dangerous in ["DROP", "DELETE", "TRUNCATE", "ALTER"]):
            return {"error": "Dangerous SQL operations not allowed"}
        
        # Execute query (implementation here)
        return [{"id": 1, "name": "Sample Data"}]
```

### Dynamic Context-Aware Prompts

```python
class AdaptiveSkill(Skill):
    """Skill that adapts prompts based on context"""
    
    @prompt(priority=10)
    def get_adaptive_prompt(self, context) -> str:
        """Generate context-aware prompts"""
        user_type = getattr(context, 'user_type', 'standard')
        
        if user_type == "technical":
            return """You're assisting a technical user:
            - Provide detailed technical explanations
            - Include code examples when relevant
            - Use precise technical terminology"""
        else:
            return """You're assisting a general user:
            - Explain concepts in simple terms
            - Avoid technical jargon
            - Use analogies and examples"""
    
    @prompt(priority=20, scope="owner")
    def get_owner_prompt(self, context) -> str:
        """Additional context for owners"""
        return f"Owner mode: You have access to advanced features and administrative tools."
```

### Domain-Specific Prompts

```python
class MedicalSkill(Skill):
    """Medical information skill with safety prompts"""
    
    @prompt(priority=1)  # High priority for safety
    def get_safety_prompt(self, context) -> str:
        """Critical safety disclaimers"""
        return """IMPORTANT MEDICAL DISCLAIMER:
        - You are NOT a licensed medical professional
        - This is for informational purposes only
        - Always advise consulting healthcare providers
        - Never diagnose conditions or prescribe treatments"""
    
    @prompt(priority=10)
    def get_capability_prompt(self, context) -> str:
        """Define medical information capabilities"""
        return """You can provide:
        - General health information
        - Medical term explanations
        - When to seek medical attention
        - Publicly available health resources"""
```

## 🪝 Hooks in Skills

Hooks integrate with the agent's request lifecycle for event-driven processing.

### Available Hook Events

| Hook | When Called | Purpose |
|------|------------|---------|
| `on_connection` | Request starts | Initialize request state |
| `on_message` | Each message processed | Analyze/modify messages |
| `before_toolcall` | Before tool execution | Validate/modify tool calls |
| `after_toolcall` | After tool execution | Process tool results |
| `on_chunk` | Each streaming chunk | Modify streaming output |
| `before_handoff` | Before agent handoff | Prepare handoff context |
| `after_handoff` | After agent handoff | Process handoff results |
| `finalize_connection` | Request ends | Cleanup and finalization |

### Message Processing Hooks

```python
class AnalyticsSkill(Skill):
    """Analytics and tracking capabilities"""
    
    @hook("on_connection", priority=1)
    async def start_tracking(self, context):
        """Initialize analytics for request"""
        context.request_id = context.completion_id
        context.start_time = time.time()
        context.events = []
        return context
    
    @hook("on_message", priority=10)
    async def analyze_message(self, context):
        """Analyze each message"""
        message = context.messages[-1]
        
        if message["role"] == "user":
            # Detect intent and entities
            intent = self.detect_intent(message["content"])
            entities = self.extract_entities(message["content"])
            
            # Add to context
            context.detected_intent = intent
            context.entities = entities
            
            # Track event
            context.events.append({
                "type": "message_analyzed",
                "intent": intent,
                "entities": entities,
                "timestamp": time.time()
            })
        
        return context
    
    @hook("finalize_connection")
    async def send_analytics(self, context):
        """Send analytics when request completes"""
        duration = time.time() - context.start_time
        
        await self.send_to_analytics({
            "request_id": context.request_id,
            "duration": duration,
            "events": context.events,
            "intent": getattr(context, 'detected_intent', None),
            "tokens": getattr(context, 'usage', {})
        })
        
        return context
```

### Tool Validation Hooks

```python
class SecuritySkill(Skill):
    """Security and validation capabilities"""
    
    @hook("before_toolcall", priority=1)
    async def validate_tool_call(self, context):
        """Validate tool calls for security"""
        tool_call = context.tool_call
        function_name = tool_call["function"]["name"]
        
        # Security check
        if not self.is_tool_allowed(function_name, context.user_id):
            context.tool_call = {
                "id": tool_call["id"],
                "type": "function",
                "function": {
                    "name": "permission_denied",
                    "arguments": json.dumps({
                        "requested_tool": function_name,
                        "reason": "Insufficient permissions"
                    })
                }
            }
        
        return context
```

## 🔄 Handoffs in Skills

Handoffs enable routing queries to specialized agents when expertise is needed.

### Basic Handoff Implementation

```python
class RouterSkill(Skill):
    """Intelligent query routing capabilities"""
    
    @handoff("finance-expert")
    def needs_finance_expert(self, query: str) -> bool:
        """Route finance questions to specialist"""
        finance_terms = ["stock", "investment", "portfolio", "trading", "finance", "market"]
        return any(term in query.lower() for term in finance_terms)
    
    @handoff("legal-advisor")
    def needs_legal_expert(self, query: str) -> bool:
        """Route legal questions to specialist"""
        legal_terms = ["contract", "legal", "law", "compliance", "regulation", "lawsuit"]
        return any(term in query.lower() for term in legal_terms)
```

## Complete Skill Example

```python
class ComprehensiveSkill(Skill):
    """Skill demonstrating all components working together"""
    
    @prompt(priority=5)
    def get_system_prompt(self, context) -> str:
        return "You are a comprehensive assistant with multiple capabilities."
    
    @tool
    def process_data(self, input_data: str) -> dict:
        return {"result": f"Processed: {input_data}"}
    
    @hook("on_message")
    async def enhance_messages(self, context):
        # Add context enhancement
        return context
    
    @handoff("domain-expert")
    def needs_expert(self, query: str) -> bool:
        return "complex" in query.lower()
```

## Best Practices

### Skill Design
1. **Single Responsibility** - Each skill should have a focused purpose
2. **Clear Naming** - Use descriptive names for skills, tools, and functions
3. **Comprehensive Documentation** - Include docstrings and examples
4. **Error Handling** - Handle errors gracefully and provide helpful messages
5. **Security First** - Use appropriate scopes and validate inputs

### Performance
1. **Async Operations** - Use async for I/O operations
2. **Efficient Hooks** - Keep hook processing fast
3. **Caching** - Cache expensive operations when appropriate
4. **Resource Management** - Clean up resources in finalize hooks

## See Also

- **[Skills Overview](overview.md)** - Understanding the skills system
- **[Agent Tools](../agent/tools.md)** - Tools in agent context
- **[Agent Prompts](../agent/prompts.md)** - Prompts in agent context
- **[Agent Hooks](../agent/hooks.md)** - Hooks in agent context
- **[Dependencies](dependencies.md)** - Managing skill dependencies