#!/usr/bin/env python3
"""
Demo showcasing the new @http decorator and capabilities system

This demonstrates:
- @http decorator for custom API endpoints
- Capabilities auto-registration system
- Direct registration methods (@agent.http, @agent.tool, etc.)
- Conflict detection and scope-based access
- Integration with existing @tool, @hook, @handoff decorators
"""

from webagents.agents.core.base_agent import BaseAgent
from webagents.agents.skills.base import Handoff, HandoffResult
from webagents.agents.tools.decorators import tool, hook, handoff, http


# ===== DECORATED FUNCTIONS FOR CAPABILITIES DEMO =====

@tool(scope="owner")
def calculate_fibonacci(n: int) -> int:
    """Calculate fibonacci number"""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)


@http("/weather", method="get", scope="owner")
def get_weather_endpoint(location: str, units: str = "celsius") -> dict:
    """Weather API endpoint"""
    return {
        "location": location,
        "temperature": 25,
        "units": units,
        "condition": "sunny",
        "forecast": ["sunny", "cloudy", "rainy"]
    }


@http("/data", method="post")
async def post_data_endpoint(data: dict) -> dict:
    """Data submission endpoint"""
    return {
        "received": data,
        "status": "processed",
        "id": "12345",
        "timestamp": "2024-01-01T12:00:00Z"
    }


@http("/admin/users", method="get", scope="admin")
def get_users_endpoint() -> dict:
    """Admin-only users endpoint"""
    return {
        "users": [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob", "role": "user"},
            {"id": 3, "name": "Charlie", "role": "user"}
        ],
        "total": 3
    }


@hook("on_request", priority=10, scope="all")
async def request_logger_hook(context):
    """Log incoming requests"""
    print(f"🔍 Request received: {getattr(context, 'request_id', 'unknown')}")
    if hasattr(context, 'set'):
        context.set("logged", True)
    return context


@handoff(handoff_type="agent", scope="admin")
async def escalate_to_specialist(issue: str, priority: str = "normal") -> HandoffResult:
    """Escalate complex issues to specialist agent"""
    return HandoffResult(
        result=f"Issue '{issue}' escalated to specialist (priority: {priority})",
        handoff_type="agent",
        success=True,
        metadata={"escalated_at": "2024-01-01T12:00:00Z", "priority": priority}
    )


def main():
    print("🚀 HTTP Decorator & Capabilities System Demo")
    print("=" * 60)
    
    # 1. Capabilities Auto-Registration Demo
    print("\n1. 📦 Capabilities Auto-Registration:")
    print("   Using capabilities=[] to auto-register decorated functions")
    
    capabilities = [
        calculate_fibonacci,     # @tool
        get_weather_endpoint,    # @http
        post_data_endpoint,      # @http
        get_users_endpoint,      # @http
        request_logger_hook,     # @hook
        escalate_to_specialist   # @handoff
    ]
    
    agent = BaseAgent(
        name="capabilities-agent",
        instructions="Agent with auto-registered capabilities",
        scopes=["owner", "admin"],
        capabilities=capabilities
    )
    
    print(f"   ✅ Auto-registered from capabilities:")
    print(f"      - Tools: {len(agent._registered_tools)}")
    print(f"      - HTTP handlers: {len(agent._registered_http_handlers)}")
    print(f"      - Hooks: {sum(len(hooks) for hooks in agent._registered_hooks.values())}")
    print(f"      - Handoffs: {len(agent._registered_handoffs)}")
    
    # 2. HTTP Endpoints Overview
    print("\n2. 🌐 HTTP Endpoints:")
    print("   Custom API endpoints registered with the agent")
    
    all_handlers = agent.get_all_http_handlers()
    for handler in all_handlers:
        method = handler['method'].upper()
        path = f"/{agent.name}{handler['subpath']}"
        scope = handler['scope']
        print(f"   📡 {method} {path} (scope: {scope})")
        print(f"      └─ {handler['description']}")
    
    # 3. Scope-Based Access Control
    print("\n3. 🔒 Scope-Based Access Control:")
    print("   Different users see different endpoints based on their scope")
    
    scopes_to_test = ["all", "owner", "admin"]
    for scope in scopes_to_test:
        accessible_handlers = agent.get_http_handlers_for_scope(scope)
        paths = [h['subpath'] for h in accessible_handlers]
        print(f"   👤 '{scope}' scope can access: {len(accessible_handlers)} endpoints")
        for path in paths:
            print(f"      └─ {path}")
    
    # 4. Direct Registration Demo
    print("\n4. 🎯 Direct Registration (@agent.http, @agent.tool, etc.):")
    print("   FastAPI-style direct registration on agent instances")
    
    direct_agent = BaseAgent(
        name="direct-agent",
        instructions="Agent with direct registration",
        scopes=["owner"]
    )
    
    @direct_agent.http("/status")
    def get_status() -> dict:
        """Agent status endpoint"""
        return {
            "status": "healthy",
            "uptime": "24h",
            "version": "2.0.0",
            "capabilities": ["tools", "http", "handoffs"]
        }
    
    @direct_agent.http("/metrics", method="get", scope="admin")
    def get_metrics() -> dict:
        """Performance metrics endpoint"""
        return {
            "requests_per_second": 100,
            "response_time_ms": 50,
            "error_rate": 0.01,
            "memory_usage": "256MB"
        }
    
    @direct_agent.tool(name="quick_calc", scope="all")
    def quick_calculator(expression: str) -> str:
        """Quick calculation tool"""
        try:
            # Simple eval for demo (don't use in production!)
            result = eval(expression.replace("^", "**"))
            return f"{expression} = {result}"
        except:
            return f"Invalid expression: {expression}"
    
    print(f"   ✅ Direct registration results:")
    print(f"      - HTTP handlers: {len(direct_agent._registered_http_handlers)}")
    print(f"      - Tools: {len(direct_agent._registered_tools)}")
    
    # Test direct registrations
    print(f"   🧪 Testing direct registrations:")
    status_result = get_status()
    calc_result = quick_calculator("2 + 3 * 4")
    print(f"      Status endpoint: {status_result['status']}")
    print(f"      Calculator tool: {calc_result}")
    
    # 5. Conflict Detection Demo
    print("\n5. ⚠️  Conflict Detection:")
    print("   System prevents conflicting endpoint registrations")
    
    @http("/test-conflict")
    def first_handler():
        return {"handler": "first"}
    
    @http("/test-conflict")  # Same path
    def second_handler():
        return {"handler": "second"}
    
    conflict_agent = BaseAgent(name="conflict-agent", instructions="Conflict test")
    conflict_agent.register_http_handler(first_handler)
    
    try:
        conflict_agent.register_http_handler(second_handler)
        print("   ❌ Conflict detection failed")
    except ValueError as e:
        print(f"   ✅ Conflict detected: {str(e)[:60]}...")
    
    # Test core path conflicts
    try:
        @http("/chat/completions")
        def core_conflict():
            return {}
        conflict_agent.register_http_handler(core_conflict)
        print("   ❌ Core path conflict detection failed")
    except ValueError as e:
        print(f"   ✅ Core path conflict detected: {str(e)[:60]}...")
    
    # 6. Integration with Existing System
    print("\n6. 🔗 Integration with Existing System:")
    print("   HTTP handlers work alongside existing tools, hooks, and handoffs")
    
    # Create a comprehensive agent
    comprehensive_agent = BaseAgent(
        name="comprehensive-agent",
        instructions="Agent with all capability types",
        scopes=["all", "owner"],
        tools=[calculate_fibonacci],
        hooks={"on_request": [request_logger_hook]},
        handoffs=[escalate_to_specialist],
        http_handlers=[get_weather_endpoint, post_data_endpoint],
        capabilities=[]  # Could add more here
    )
    
    print(f"   ✅ Comprehensive agent capabilities:")
    print(f"      - Agent name: {comprehensive_agent.name}")
    print(f"      - Agent scopes: {comprehensive_agent.scopes}")
    print(f"      - Tools: {len(comprehensive_agent._registered_tools)} registered")
    print(f"      - HTTP handlers: {len(comprehensive_agent._registered_http_handlers)} registered")
    print(f"      - Hooks: {sum(len(h) for h in comprehensive_agent._registered_hooks.values())} registered")
    print(f"      - Handoffs: {len(comprehensive_agent._registered_handoffs)} registered")
    
    # 7. Example API Usage
    print("\n7. 📋 Example API Usage:")
    print("   How the HTTP endpoints would be called")
    
    example_calls = [
        f"GET  /{comprehensive_agent.name}/weather?location=NYC&units=fahrenheit",
        f"POST /{comprehensive_agent.name}/data",
        f"GET  /{direct_agent.name}/status",
        f"GET  /{direct_agent.name}/metrics (admin only)",
    ]
    
    for call in example_calls:
        print(f"   🌐 {call}")
    
    print(f"\n✅ HTTP Decorator & Capabilities System Demo Complete!")
    print(f"🎉 New Features Summary:")
    print(f"   - @http decorator for custom API endpoints")
    print(f"   - capabilities=[] for auto-registration")
    print(f"   - @agent.http(), @agent.tool() direct registration")
    print(f"   - Conflict detection and scope-based access")
    print(f"   - Full integration with existing decorator system")


if __name__ == "__main__":
    main() 