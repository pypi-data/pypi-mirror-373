# Agent Communication

Learn how agents communicate with users and other agents through various protocols and interfaces.

Communication primitives are OpenAI-compatible by default (messages, tools, streaming). For inter-agent scenarios, add the `NLISkill` and optionally `DiscoverySkill` to find and contact peers.

## Communication Protocols

### OpenAI-Compatible API

The primary communication interface:

```python
# Standard chat completion
response = await agent.run([
    {"role": "user", "content": "Hello!"}
])

# Streaming response
async for chunk in agent.run_streaming([
    {"role": "user", "content": "Tell me a story"}
]):
    print(chunk.choices[0].delta.content, end="")
```

### Natural Language Interface (NLI)

Agent-to-agent communication:

```python
from robutler.agents.skills import NLISkill

class CollaborativeSkill(Skill):
    def __init__(self):
        super().__init__()
        self.nli = NLISkill()
    
    @tool
    async def ask_expert(self, topic: str, question: str) -> str:
        """Ask an expert agent"""
        
        # Find expert for topic
        expert = await self.find_expert(topic)
        
        # Communicate via NLI
        response = await self.nli.query_agent(
            agent_name=expert,
            query=question,
            context={
                "requester": self.agent.name,
                "topic": topic
            }
        )
        
        return response.get("response", "No response from expert")
```

## Message Formats

### User Messages

```python
# Text message
{
    "role": "user",
    "content": "What's the weather?"
}

# Message with name
{
    "role": "user", 
    "name": "alice",
    "content": "Help me plan a trip"
}

# Message with images (future)
{
    "role": "user",
    "content": [
        {"type": "text", "text": "What's in this image?"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
    ]
}
```

### Assistant Messages

```python
# Simple response
{
    "role": "assistant",
    "content": "I'll help you with that."
}

# Response with tool calls
{
    "role": "assistant",
    "content": "Let me check the weather for you.",
    "tool_calls": [{
        "id": "call_123",
        "type": "function",
        "function": {
            "name": "get_weather",
            "arguments": '{"location": "Paris"}'
        }
    }]
}
```

### Tool Messages

```python
# Tool result
{
    "role": "tool",
    "tool_call_id": "call_123",
    "content": '{"temperature": 22, "conditions": "Sunny"}'
}
```

## Multi-Modal Communication

### Rich Responses

```python
class RichResponseSkill(Skill):
    @tool
    async def create_report(self, topic: str) -> Dict:
        """Create a rich media report"""
        
        # Generate different content types
        text_summary = await self.generate_summary(topic)
        data_table = await self.generate_data_table(topic)
        chart_url = await self.generate_chart(topic)
        
        # Return structured response
        return {
            "type": "report",
            "topic": topic,
            "sections": [
                {
                    "type": "text",
                    "title": "Summary",
                    "content": text_summary
                },
                {
                    "type": "table",
                    "title": "Data Analysis",
                    "headers": ["Metric", "Value", "Change"],
                    "rows": data_table
                },
                {
                    "type": "chart",
                    "title": "Trends",
                    "url": chart_url,
                    "alt_text": "Trend chart for " + topic
                }
            ]
        }
```

### Structured Data

```python
@tool
def get_product_info(self, product_id: str) -> Dict:
    """Return structured product data"""
    
    return {
        "product_id": product_id,
        "name": "Premium Widget",
        "price": {
            "amount": 99.99,
            "currency": "USD"
        },
        "availability": {
            "in_stock": True,
            "quantity": 42
        },
        "metadata": {
            "category": "Electronics",
            "tags": ["premium", "bestseller"]
        }
    }
```

## Communication Patterns

### Request-Response

Basic synchronous pattern:

```python
# Client request
request = {
    "messages": [{"role": "user", "content": "Calculate 42 * 17"}],
    "model": "gpt-4o"
}

# Agent response
response = await agent.run(request["messages"])
print(response.choices[0].message.content)  # "42 * 17 = 714"
```

### Streaming

Asynchronous chunked responses:

```python
async def stream_response(messages):
    async for chunk in agent.run_streaming(messages):
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
        
        # Check for tool calls in stream
        if chunk.choices[0].delta.tool_calls:
            await handle_streaming_tool_call(chunk)
```

### Conversational

Multi-turn dialogue:

```python
class ConversationManager:
    def __init__(self, agent):
        self.agent = agent
        self.history = []
    
    async def chat(self, user_input: str):
        # Add user message
        self.history.append({
            "role": "user",
            "content": user_input
        })
        
        # Get response
        response = await self.agent.run(self.history)
        
        # Add to history
        assistant_msg = response.choices[0].message
        self.history.append(assistant_msg.dict())
        
        # Handle tool calls if any
        if assistant_msg.tool_calls:
            for tool_call in assistant_msg.tool_calls:
                result = await self.execute_tool(tool_call)
                self.history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
            
            # Get final response after tools
            response = await self.agent.run(self.history)
            self.history.append(response.choices[0].message.dict())
        
        return response
```

## Inter-Agent Communication

### Direct Communication

```python
class TeamworkSkill(Skill):
    @tool
    async def collaborate(self, task: str) -> str:
        """Collaborate with team of agents"""
        
        # Define team
        team = {
            "researcher": "research-agent",
            "writer": "writing-agent",
            "reviewer": "review-agent"
        }
        
        # Research phase
        research = await self.nli.query_agent(
            team["researcher"],
            f"Research information about: {task}"
        )
        
        # Writing phase
        draft = await self.nli.query_agent(
            team["writer"],
            f"Write content based on this research: {research['response']}"
        )
        
        # Review phase
        final = await self.nli.query_agent(
            team["reviewer"],
            f"Review and improve this content: {draft['response']}"
        )
        
        return final["response"]
```

### Broadcast Communication

```python
class BroadcastSkill(Skill):
    @tool
    async def survey_experts(self, question: str) -> Dict:
        """Get opinions from multiple experts"""
        
        # Find relevant experts
        experts = await self.discovery.find_agents(
            intent=question,
            max_results=5
        )
        
        # Query all experts in parallel
        tasks = []
        for expert in experts:
            task = self.nli.query_agent(
                expert["name"],
                question,
                timeout=10  # Don't wait too long
            )
            tasks.append(task)
        
        # Gather responses
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process responses
        results = {}
        for expert, response in zip(experts, responses):
            if isinstance(response, Exception):
                results[expert["name"]] = "No response"
            else:
                results[expert["name"]] = response.get("response", "Error")
        
        return results
```

## Error Communication

### Graceful Error Handling

```python
class ErrorHandlingSkill(Skill):
    @tool
    async def safe_operation(self, params: Dict) -> Dict:
        """Operation with comprehensive error handling"""
        
        try:
            # Validate inputs
            if not self.validate_params(params):
                return {
                    "success": False,
                    "error": "Invalid parameters",
                    "details": self.get_validation_errors(params)
                }
            
            # Perform operation
            result = await self.perform_operation(params)
            
            return {
                "success": True,
                "result": result
            }
            
        except RateLimitError as e:
            return {
                "success": False,
                "error": "Rate limit exceeded",
                "retry_after": e.retry_after,
                "message": "Please try again later"
            }
            
        except ExternalAPIError as e:
            return {
                "success": False,
                "error": "External service error",
                "service": e.service,
                "message": "The external service is temporarily unavailable"
            }
            
        except Exception as e:
            # Log unexpected errors
            await self.log_error(e, params)
            
            return {
                "success": False,
                "error": "Unexpected error",
                "message": "An unexpected error occurred. Support has been notified."
            }
```

## Communication Middleware

### Message Transformation

```python
class MessageTransformSkill(Skill):
    @hook("on_message", priority=1)
    async def transform_input(self, context):
        """Transform user messages"""
        
        message = context.messages[-1]
        
        if message["role"] == "user":
            # Expand abbreviations
            content = self.expand_abbreviations(message["content"])
            
            # Fix common typos
            content = self.fix_typos(content)
            
            # Add context
            if self.needs_context(content):
                content = self.add_context(content, context)
            
            context.messages[-1]["content"] = content
        
        return context
    
    @hook("on_chunk", priority=1)
    async def transform_output(self, context):
        """Transform assistant output"""
        
        content = context.get("content", "")
        
        # Apply user preferences
        if self.user_prefers_formal(context.peer_user_id):
            content = self.make_formal(content)
        
        # Localize response
        user_locale = self.get_user_locale(context.peer_user_id)
        if user_locale != "en":
            content = self.localize(content, user_locale)
        
        context["chunk"]["choices"][0]["delta"]["content"] = content
        
        return context
```

## Best Practices

1. **Clear Protocols** - Use standard formats (OpenAI API)
2. **Error Handling** - Always handle communication failures
3. **Timeouts** - Set appropriate timeouts for inter-agent calls
4. **Context Preservation** - Maintain conversation context
5. **Async Communication** - Use async/await for scalability 