"""
Example usage of ServerBase - Clean context access for inner functions

This example demonstrates ServerBase using:
- FastAPI dependency injection for agent handlers
- get_context() for inner function access to request context

Features:
* Agent handlers use FastAPI dependency injection
* Inner functions (tools) use get_context() for clean access
* Simple, intuitive API for context access
"""

from fastapi import Request, Depends
from agents import Agent, Runner
from webagents.server.base import ServerBase, RequestState, get_request_state, get_context

# Create the server
app = ServerBase()

# Example tool function that needs context access
def search_web(query: str) -> str:
    """Tool function that accesses request context."""
    # Inner functions can access context cleanly
    context = get_context()
    
    if context:
        user_id = context.get("user_id", "anonymous")
        
        # Track usage with simplified API
        context.track_usage(
            credits=25,
            reason=f"Performed web search for query: '{query}'",
            metadata={
                "query": query,
                "query_length": len(query),
                "search_type": "web",
                "provider": "search_engine_api"
            }
        )
        
        print(f"🔍 Web search by user {user_id}: {query}")
        return f"Search results for '{query}' (searched by {user_id})"
    else:
        print("⚠️ No context available in tool")
        return f"Search results for '{query}'"

def get_user_data() -> dict:
    """Another tool that accesses context."""
    context = get_context()
    
    if context:
        user_id = context.get("user_id", "anonymous")
        session_data = context.get("session_data", {})
        
        # Track usage with simplified API
        context.track_usage(
            credits=10,
            reason=f"Retrieved user profile and preferences for user {user_id}",
            metadata={
                "user_id": user_id,
                "data_types": ["profile", "preferences", "session"],
                "cache_hit": False
            }
        )
        
        return {
            "user_id": user_id,
            "session": session_data.get("session_id", "unknown"),
            "preferences": f"preferences for {user_id}"
        }
    
    return {"user_id": "anonymous", "session": "unknown", "preferences": "default"}

# Example 1: Agent with tools that access context
@app.agent("search_assistant")
async def search_assistant(messages, stream=False, request: Request = Depends()):
    """Assistant with tools that can access request context."""
    user_id = getattr(request.state, 'user_id', 'anonymous')
    print(f"🤖 Search assistant serving user: {user_id}")
    
    # Create agent with tools
    agent = Agent(
        name="search_assistant",
        instructions="You are a helpful assistant with web search capabilities. Use search_web when users ask for current information.",
        model="gpt-4o-mini",
        tools=[search_web, get_user_data]  # Tools can access context via get_context()
    )
    
    # Configure model settings to include usage information
    from agents import RunConfig, ModelSettings
    model_settings = ModelSettings(include_usage=True)
    run_config = RunConfig(model_settings=model_settings)
    
    if stream:
        return await Runner.run_streamed(agent, messages, run_config=run_config)
    else:
        result = await Runner.run(agent, messages, run_config=run_config)
        return result.final_output

# Example 2: Agent with state dependency + tools with context
@app.agent("data_assistant") 
async def data_assistant(messages, stream=False, state: RequestState = Depends(get_request_state)):
    """Assistant using state dependency with tools that access context."""
    user_id = state.get("user_id", "anonymous")
    print(f"📊 Data assistant serving user: {user_id}")
    
    # Store some data for tools to access
    state.set("assistant_type", "data_specialist")
    state.set("session_start", state.request.state.start_time)
    
    def analyze_data(data_type: str) -> str:
        """Tool that accesses the stored context."""
        context = get_context()
        if context:
            user_id = context.get("user_id", "anonymous")
            assistant_type = context.get("assistant_type", "unknown")
            
            # Track usage with simplified API
            context.track_usage(
                credits=40,
                reason=f"Performed {data_type} analysis for user {user_id}",
                metadata={
                    "data_type": data_type,
                    "analyst_type": assistant_type,
                    "analysis_complexity": "medium",
                    "processing_time_estimate": "2-3 seconds"
                }
            )
            
            return f"Data analysis of {data_type} by {assistant_type} for user {user_id}"
        return f"Basic analysis of {data_type}"
    
    agent = Agent(
        name="data_assistant",
        instructions="You are a data analysis specialist. Use analyze_data to help with data questions.",
        model="gpt-4o-mini", 
        tools=[analyze_data, get_user_data]
    )
    
    # Configure model settings to include usage information
    from agents import RunConfig, ModelSettings
    model_settings = ModelSettings(include_usage=True)
    run_config = RunConfig(model_settings=model_settings)
    
    if stream:
        return await Runner.run_streamed(agent, messages, run_config=run_config)
    else:
        result = await Runner.run(agent, messages, run_config=run_config)
        return result.final_output

# Example 3: Complex tool with context access
def complex_processing(task: str, priority: str = "normal") -> str:
    """Complex tool that heavily uses context."""
    context = get_context()
    
    if not context:
        return f"Processed {task} with {priority} priority (no context)"
    
    # Access request details via context.request
    user_agent = context.request.headers.get("user-agent", "unknown")
    ip = context.request.client.host if context.request.client else "unknown"
    
    # Access stored state via helper methods
    user_id = context.get("user_id", "anonymous")
    session_data = context.get("session_data", {})
    assistant_type = context.get("assistant_type", "general")
    
    # Track different usage based on priority using payment skill
    payment_skill = context.agent.skills.get('payment') if context.agent else None
    if payment_skill and hasattr(payment_skill, 'track_usage'):
        if priority == "high":
            payment_skill.track_usage(
                credits=100,
                description=f"High-priority processing of '{task}' with enhanced resources",
                metadata={
                    "task": task,
                    "priority": priority,
                    "resources_allocated": "enhanced",
                    "processing_tier": "premium",
                    "estimated_completion": "1-2 minutes",
                    "cpu_intensive": True
                }
            )
        else:
            payment_skill.track_usage(
                credits=50,
                description=f"Standard processing of '{task}' with normal resources",
                metadata={
                    "task": task,
                    "priority": priority,
                    "resources_allocated": "standard",
                    "processing_tier": "basic",
                    "estimated_completion": "3-5 minutes",
                    "cpu_intensive": False
                }
            )
    
    # Store processing result
    context.set("last_processing", {
        "task": task,
        "priority": priority,
        "user_id": user_id,
        "timestamp": context.request.state.start_time.isoformat()
    })
    
    return f"""Complex processing complete:
    Task: {task}
    Priority: {priority}
    User: {user_id}
    Session: {session_data.get('session_id', 'unknown')}
    Assistant: {assistant_type}
    Client: {user_agent[:50]}...
    IP: {ip}"""

@app.agent("processor")
async def processor_agent(
    messages, 
    stream=False, 
    request: Request = Depends(),
    state: RequestState = Depends(get_request_state)
):
    """Agent with complex tools that access full context."""
    user_id = state.get("user_id", "anonymous")
    print(f"⚙️ Processor agent serving user: {user_id}")
    
    # Set up context for tools
    state.set("assistant_type", "processor")
    state.set("capabilities", ["analysis", "processing", "optimization"])
    
    agent = Agent(
        name="processor",
        instructions="You are a processing specialist. Use complex_processing for any processing tasks.",
        model="gpt-4o-mini",
        tools=[complex_processing, get_user_data]
    )
    
    # Configure model settings to include usage information
    from agents import RunConfig, ModelSettings
    model_settings = ModelSettings(include_usage=True)
    run_config = RunConfig(model_settings=model_settings)
    
    if stream:
        return await Runner.run_streamed(agent, messages, run_config=run_config)
    else:
        result = await Runner.run(agent, messages, run_config=run_config)
        return result.final_output

# Example 4: Dynamic agent with context-aware tools
def resolve_specialist(name: str):
    """Resolve specialist by name."""
    specialists = {
        "researcher": {
            "agent": Agent(
                name="researcher",
                instructions="You are a research specialist. Use search_web for research tasks.",
                model="gpt-4o-mini",
                tools=[search_web, get_user_data]
            ),
            "specialty": "research and information gathering"
        },
        "analyst": {
            "agent": Agent(
                name="analyst", 
                instructions="You are a data analyst. Use complex_processing for analysis tasks.",
                model="gpt-4o-mini",
                tools=[complex_processing, get_user_data]
            ),
            "specialty": "data analysis and processing"
        }
    }
    
    return specialists.get(name, False)

@app.agent(resolve_specialist)
async def specialist_agent(
    messages, 
    stream=False, 
    agent_data=None, 
    state: RequestState = Depends(get_request_state)
):
    """Dynamic specialist with context-aware tools."""
    if not agent_data:
        return "Specialist not available"
    
    user_id = state.get("user_id", "anonymous")
    specialty = agent_data["specialty"]
    
    print(f"🎯 {specialty} specialist serving user: {user_id}")
    
    # Set context for tools
    state.set("assistant_type", "specialist")
    state.set("specialty", specialty)
    
    agent = agent_data["agent"]
    
    # Configure model settings to include usage information
    from agents import RunConfig, ModelSettings
    model_settings = ModelSettings(include_usage=True)
    run_config = RunConfig(model_settings=model_settings)
    
    if stream:
        return await Runner.run_streamed(agent, messages, run_config=run_config)
    else:
        result = await Runner.run(agent, messages, run_config=run_config)
        return result.final_output

# Lifecycle hooks
@app.agent.before_request
async def setup_context(request):
    """Setup request context."""
    user_id = request.headers.get("X-User-ID", "anonymous")
    session_id = request.headers.get("X-Session-ID", "new-session")
    
    # Store in FastAPI request.state
    request.state.user_id = user_id
    request.state.session_data = {
        "session_id": session_id,
        "start_time": request.state.start_time
    }
    
    print(f"🔍 Context setup for user {user_id} (session: {session_id})")

@app.agent.finalize_request
async def log_final_usage(request, response):
    """Log final usage with simplified receipt."""
    state = RequestState(request)
    user_id = state.get("user_id", "unknown")
    
    duration = state.get_duration()
    usage = state.usage
    last_processing = state.get("last_processing")
    
    print(f"✅ Request completed for user {user_id}")
    print(f"   Duration: {duration:.2f}s")
    print(f"   Total: {usage['total_credits']} credits")
    print(f"   Operations: {usage['total_operations']}")
    
    # Show receipt
    receipt = usage["receipt"]
    print(f"\n📋 Usage Receipt:")
    print(f"   Request ID: {receipt['request_id']}")
    print(f"   User: {receipt['user_id']}")
    print(f"   Session: {receipt['session_id']}")
    print(f"   Started: {receipt['started_at']}")
    print(f"   Completed: {receipt['completed_at']}")
    
    # Show cost breakdown
    cost = receipt["cost_breakdown"]
    print(f"\n💰 Cost Breakdown:")
    print(f"   Total Credits: {cost['total_credits']}")
    print(f"   Avg Credits/Op: {cost['average_credits_per_operation']:.1f}")
    
    if cost["most_expensive_operation"]:
        expensive = cost["most_expensive_operation"]
        print(f"   Most Expensive: {expensive['reason']} ({expensive['credits']} credits)")
    
    # Show operations
    print(f"\n🔧 Operations:")
    for op in receipt["operations"]:
        print(f"   - {op['reason']} ({op['credits']} credits)")
        if op['metadata']:
            key_metadata = {k: v for k, v in op['metadata'].items() if k in ['task', 'priority', 'data_type', 'query']}
            if key_metadata:
                print(f"     Metadata: {key_metadata}")
    
    if last_processing:
        print(f"\n📊 Last Processing: {last_processing['task']} ({last_processing['priority']})")

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting ServerBase with clean context access...")
    print("📋 Available endpoints:")
    print("   POST /search_assistant/chat/completions - Agent with search tools")
    print("   POST /data_assistant/chat/completions - Data specialist")
    print("   POST /processor/chat/completions - Complex processing")
    print("   POST /researcher/chat/completions - Research specialist")
    print("   POST /analyst/chat/completions - Data analyst")
    print("   GET /{agent_name} - Agent info")
    print()
    print("💡 Test with tools that access context:")
    print('   curl -X POST "http://localhost:8000/search_assistant/chat/completions" \\')
    print('        -H "Content-Type: application/json" \\')
    print('        -H "X-User-ID: test-user-123" \\')
    print('        -H "X-Session-ID: session-456" \\')
    print('        -d \'{"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Search for Python tutorials"}]}\'')
    print()
    print("🔧 Test complex processing:")
    print('   curl -X POST "http://localhost:8000/processor/chat/completions" \\')
    print('        -H "Content-Type: application/json" \\')
    print('        -H "X-User-ID: power-user" \\')
    print('        -d \'{"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Process this data with high priority"}]}\'')
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 