#!/usr/bin/env python3
"""
Demo script showcasing BaseAgent with tools, hooks, and handoffs

This script demonstrates the new BaseAgent initialization capabilities:
- Tools: Functions that the agent can call
- Hooks: Lifecycle event handlers
- Handoffs: Agent-to-agent communication patterns
"""

import asyncio
from webagents.agents.core.base_agent import BaseAgent
from webagents.agents.skills.base import Handoff, HandoffResult
from webagents.agents.tools.decorators import tool, hook, handoff


# Example tools for the demo
def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two numbers"""
    result = a + b
    print(f"🔧 Tool executed: {a} + {b} = {result}")
    return result


@tool(name="multiply", description="Multiply two numbers", scope="owner")
def calculate_product(x: int, y: int) -> int:
    """Calculate the product of two numbers"""
    result = x * y
    print(f"🔧 Decorated tool executed: {x} * {y} = {result}")
    return result


@tool(scope="admin")
def admin_function(action: str) -> str:
    """Admin-only function"""
    print(f"🔒 Admin function executed: {action}")
    return f"Admin action completed: {action}"


# Example hooks for the demo
def logging_hook(context):
    """Simple logging hook"""
    print(f"📝 Hook executed: Request processing started")
    if hasattr(context, 'set'):
        context.set("logged", True)
    return context


@hook("on_response", priority=10, scope="all")
def response_hook(context):
    """Response processing hook"""
    print(f"📤 Response hook: Processing response")
    if hasattr(context, 'set'):
        context.set("response_processed", True)
    return context


def audit_hook(context):
    """Audit hook for tracking"""
    print(f"🔍 Audit hook: Recording activity")
    return context


# Example handoffs for the demo
@handoff(handoff_type="agent", description="Escalate to supervisor")
def escalate_to_supervisor(issue: str, priority: str = "normal") -> HandoffResult:
    """Escalate issue to supervisor agent"""
    print(f"📞 Handoff executed: Escalating '{issue}' with priority '{priority}'")
    return HandoffResult(
        result=f"Issue '{issue}' escalated to supervisor",
        handoff_type="agent",
        success=True,
        metadata={"priority": priority, "escalated_at": "now"}
    )


@handoff(handoff_type="llm", scope="admin")
def switch_to_creative_mode(task: str) -> HandoffResult:
    """Switch to creative LLM for specific tasks"""
    print(f"🎨 LLM handoff: Switching to creative mode for '{task}'")
    return HandoffResult(
        result=f"Switched to creative mode for: {task}",
        handoff_type="llm",
        success=True
    )


def main():
    """Main demo function"""
    print("🚀 BaseAgent Capabilities Demo")
    print("=" * 50)
    
    # 1. Basic agent without extra capabilities
    print("\n1. Basic Agent:")
    basic_agent = BaseAgent(
        name="basic-agent",
        instructions="I am a basic agent"
    )
    print(f"   Agent: {basic_agent.name}")
    print(f"   Tools: {len(basic_agent._registered_tools)}")
    print(f"   Hooks: {len(basic_agent._registered_hooks)}")
    print(f"   Handoffs: {len(basic_agent._registered_handoffs)}")
    
    # 2. Agent with tools
    print("\n2. Agent with Tools:")
    tool_agent = BaseAgent(
        name="tool-agent",
        instructions="I can perform calculations",
        tools=[calculate_sum, calculate_product, admin_function]
    )
    print(f"   Agent: {tool_agent.name}")
    print(f"   Tools registered: {len(tool_agent._registered_tools)}")
    for tool in tool_agent._registered_tools:
        print(f"     - {tool['name']} (scope: {tool['scope']}, source: {tool['source']})")
    
    # Test tool lookup and execution
    print("\n   Testing tool execution:")
    sum_tool = tool_agent._get_tool_function_by_name("calculate_sum")
    if sum_tool:
        result = sum_tool(5, 3)
        print(f"     Result: {result}")
    
    multiply_tool = tool_agent._get_tool_function_by_name("multiply")
    if multiply_tool:
        result = multiply_tool(4, 7)
        print(f"     Result: {result}")
    
    # 3. Agent with hooks
    print("\n3. Agent with Hooks:")
    hook_agent = BaseAgent(
        name="hook-agent",
        instructions="I have lifecycle hooks",
        hooks={
            "on_request": [logging_hook, audit_hook],
            "on_response": [response_hook]
        }
    )
    print(f"   Agent: {hook_agent.name}")
    print(f"   Hooks registered: {sum(len(hooks) for hooks in hook_agent._registered_hooks.values())}")
    for event, hooks in hook_agent._registered_hooks.items():
        if hooks:
            print(f"     {event}: {len(hooks)} hooks")
            for hook in hooks:
                print(f"       - {hook['handler'].__name__} (priority: {hook['priority']})")
    
    # 4. Agent with handoffs
    print("\n4. Agent with Handoffs:")
    handoff_config = Handoff(
        target="expert-agent",
        handoff_type="agent",
        description="Transfer to domain expert",
        scope="owner"
    )
    
    handoff_agent = BaseAgent(
        name="handoff-agent",
        instructions="I can handoff to other agents",
        handoffs=[handoff_config, escalate_to_supervisor, switch_to_creative_mode]
    )
    print(f"   Agent: {handoff_agent.name}")
    print(f"   Handoffs registered: {len(handoff_agent._registered_handoffs)}")
    for handoff in handoff_agent._registered_handoffs:
        config = handoff['config']
        print(f"     - {config.target} ({config.handoff_type}) - {config.description}")
        print(f"       Scope: {config.scope}, Source: {handoff['source']}")
    
    # 5. Full-featured agent
    print("\n5. Full-Featured Agent:")
    full_agent = BaseAgent(
        name="full-agent",
        instructions="I have all capabilities",
        scopes=["owner", "admin"],  # Multiple scopes
        tools=[calculate_sum, calculate_product],
        hooks={
            "on_request": [logging_hook],
            "on_response": [response_hook, audit_hook]
        },
        handoffs=[escalate_to_supervisor]
    )
    print(f"   Agent: {full_agent.name}")
    print(f"   Scopes: {full_agent.scopes}")
    print(f"   Total capabilities:")
    print(f"     - Tools: {len(full_agent._registered_tools)}")
    print(f"     - Hooks: {sum(len(hooks) for hooks in full_agent._registered_hooks.values())}")
    print(f"     - Handoffs: {len(full_agent._registered_handoffs)}")
    
    # Test scope filtering
    print("\n   Scope filtering demonstration:")
    all_tools = full_agent.get_tools_for_scope("all")
    owner_tools = full_agent.get_tools_for_scope("owner")
    admin_tools = full_agent.get_tools_for_scope("admin")
    multi_scope_tools = full_agent.get_tools_for_scopes(["owner", "admin"])
    
    print(f"     - 'all' scope can access: {len(all_tools)} tools")
    print(f"     - 'owner' scope can access: {len(owner_tools)} tools")
    print(f"     - 'admin' scope can access: {len(admin_tools)} tools")
    print(f"     - ['owner', 'admin'] scopes can access: {len(multi_scope_tools)} tools")
    
    # 6. Scope management demonstration
    print("\n6. Scope Management:")
    scope_agent = BaseAgent(
        name="scope-agent",
        instructions="I demonstrate scope management",
        scopes=["all"]
    )
    print(f"   Initial scopes: {scope_agent.get_scopes()}")
    
    # Add scopes
    scope_agent.add_scope("owner")
    scope_agent.add_scope("admin")
    print(f"   After adding scopes: {scope_agent.get_scopes()}")
    
    # Check scopes
    print(f"   Has 'owner' scope: {scope_agent.has_scope('owner')}")
    print(f"   Has 'guest' scope: {scope_agent.has_scope('guest')}")
    
    # Remove scope
    scope_agent.remove_scope("all")
    print(f"   After removing 'all': {scope_agent.get_scopes()}")
    
    # Set new scopes
    scope_agent.set_scopes(["custom", "special"])
    print(f"   After setting new scopes: {scope_agent.get_scopes()}")
    
    # 7. Scope inheritance demonstration
    print("\n7. Scope Inheritance:")
    admin_agent = BaseAgent(
        name="admin-agent",
        instructions="I am an admin agent",
        scopes=["admin", "owner"],  # Multiple scopes
        tools=[calculate_sum, calculate_product]  # These should inherit admin scopes
    )
    print(f"   Agent scopes: {admin_agent.scopes}")
    for tool in admin_agent._registered_tools:
        print(f"     Tool '{tool['name']}' inherited scopes: {tool['scope']}")
    
    print("\n✅ Demo completed! All BaseAgent scopes capabilities working correctly.")


if __name__ == "__main__":
    main() 