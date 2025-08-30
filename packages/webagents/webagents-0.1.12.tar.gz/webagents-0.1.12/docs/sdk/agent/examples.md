# Agent Examples

Practical examples of building different types of agents with Robutler SDK.

## Basic Examples

### Simple Chatbot

```python
from robutler.agents import BaseAgent

# Minimal chatbot
chatbot = BaseAgent(
    name="simple-chat",
    instructions="You are a friendly chatbot. Be helpful and concise.",
    model="openai/gpt-4o"
)

# Use it
response = await chatbot.run([
    {"role": "user", "content": "Hello! How are you?"}
])
print(response.choices[0].message.content)
```

### Math Tutor

```python
from robutler.agents import BaseAgent
from robutler.agents.skills import Skill
from robutler.agents.tools.decorators import tool

class MathSkill(Skill):
    @tool
    def calculate(self, expression: str) -> str:
        """Safely evaluate mathematical expressions"""
        try:
            # Safe eval with limited scope
            result = eval(expression, {"__builtins__": {}}, {
                "abs": abs, "round": round, "min": min, "max": max
            })
            return str(result)
        except:
            return "Invalid expression"
    
    @tool
    def solve_equation(self, equation: str) -> str:
        """Solve simple equations"""
        # Simplified example
        if "x" in equation:
            # Parse and solve for x
            parts = equation.split("=")
            if len(parts) == 2:
                return "x = 5"  # Placeholder
        return "Cannot solve this equation"

# Create math tutor
tutor = BaseAgent(
    name="math-tutor",
    instructions="""You are a patient math tutor. 
    - Explain concepts step by step
    - Use the calculate tool for computations
    - Encourage students when they struggle""",
    model="openai/gpt-4o",
    skills={"math": MathSkill()}
)
```

## Advanced Examples

### Customer Support Agent

```python
from robutler.agents import BaseAgent
from robutler.agents.skills import (
    Skill, ShortTermMemorySkill, 
    NLISkill, DiscoverySkill
)
from robutler.agents.tools.decorators import tool, handoff, hook

class SupportSkill(Skill):
    def __init__(self, config=None):
        super().__init__(config)
        self.knowledge_base = self.load_knowledge_base()
    
    @tool
    async def search_help(self, query: str) -> str:
        """Search help documentation"""
        results = []
        for article in self.knowledge_base:
            if query.lower() in article["content"].lower():
                results.append(f"- {article['title']}: {article['summary']}")
        
        return "\n".join(results) if results else "No relevant articles found"
    
    @tool
    async def check_order(self, order_id: str) -> Dict:
        """Check order status"""
        # Mock order lookup
        return {
            "order_id": order_id,
            "status": "In Transit",
            "estimated_delivery": "2024-01-15",
            "tracking": "TRK123456789"
        }
    
    @tool
    async def create_ticket(self, issue: str, priority: str = "normal") -> Dict:
        """Create support ticket"""
        ticket = {
            "id": f"TKT{random.randint(1000, 9999)}",
            "issue": issue,
            "priority": priority,
            "created": datetime.now().isoformat(),
            "status": "open"
        }
        
        # Save ticket (mock)
        await self.save_ticket(ticket)
        
        return ticket
    
    @handoff("technical-support")
    def needs_technical_support(self, query: str) -> bool:
        """Route technical issues to specialists"""
        tech_keywords = ["error", "crash", "bug", "not working", "broken"]
        return any(keyword in query.lower() for keyword in tech_keywords)
    
    @hook("on_connection")
    async def greet_customer(self, context):
        """Personalized greeting based on history"""
        user_id = context.peer_user_id
        
        # Check if returning customer
        history = await self.get_customer_history(user_id)
        if history:
            context["greeting"] = f"Welcome back! I see you previously contacted us about {history[-1]['topic']}."
        else:
            context["greeting"] = "Hello! How can I help you today?"
        
        return context

# Create support agent
support_agent = BaseAgent(
    name="customer-support",
    instructions="""You are a helpful customer support agent.
    - Be empathetic and professional
    - Search help docs first
    - Create tickets for unresolved issues
    - Escalate technical problems to specialists""",
    model="openai/gpt-4o",
    skills={
        "support": SupportSkill(),
        "memory": ShortTermMemorySkill({"max_messages": 100}),
        "nli": NLISkill(),
        "discovery": DiscoverySkill()
    }
)
```

### Research Assistant

```python
class ResearchSkill(Skill):
    def __init__(self, config=None):
        super().__init__(config)
        self.sources = []
    
    @tool
    async def search_papers(self, topic: str, max_results: int = 5) -> List[Dict]:
        """Search academic papers"""
        # Mock paper search
        papers = [
            {
                "title": f"Advances in {topic}",
                "authors": ["Smith, J.", "Doe, A."],
                "year": 2024,
                "abstract": f"This paper explores recent developments in {topic}...",
                "url": f"https://arxiv.org/abs/2024.{random.randint(1000,9999)}"
            }
            for i in range(max_results)
        ]
        
        # Track sources
        self.sources.extend(papers)
        
        return papers
    
    @tool
    async def summarize_paper(self, url: str) -> str:
        """Summarize academic paper"""
        # Mock summarization
        return f"This paper discusses key findings in the field, including..."
    
    @tool
    def generate_bibliography(self) -> str:
        """Generate bibliography from sources"""
        if not self.sources:
            return "No sources cited yet."
        
        bibliography = []
        for i, source in enumerate(self.sources, 1):
            authors = ", ".join(source["authors"])
            entry = f"[{i}] {authors} ({source['year']}). {source['title']}. {source['url']}"
            bibliography.append(entry)
        
        return "\n".join(bibliography)
    
    @hook("finalize_connection")
    async def save_research_session(self, context):
        """Save research for future reference"""
        if self.sources:
            session = {
                "timestamp": datetime.now().isoformat(),
                "sources": self.sources,
                "messages": context.messages
            }
            await self.save_session(context.peer_user_id, session)
        
        return context

# Create research assistant
researcher = BaseAgent(
    name="research-assistant",
    instructions="""You are an academic research assistant.
    - Search for relevant papers
    - Summarize key findings
    - Track all sources
    - Generate proper citations""",
    model="openai/gpt-4o",
    skills={
        "research": ResearchSkill(),
        "memory": ShortTermMemorySkill()
    }
)
```

### Multi-Agent Coordinator

```python
class CoordinatorSkill(Skill):
    def __init__(self, config=None):
        super().__init__(config, dependencies=["nli", "discovery"])
    
    @tool
    async def plan_project(self, description: str) -> Dict:
        """Plan project with specialized agents"""
        
        # Analyze project requirements
        tasks = self.analyze_project(description)
        
        # Find suitable agents for each task
        plan = {"project": description, "tasks": []}
        
        for task in tasks:
            # Discover agents with required skills
            agents = await self.discovery.find_agents(
                intent=task["description"],
                skills=task["required_skills"]
            )
            
            if agents:
                best_agent = agents[0]  # Select best match
                plan["tasks"].append({
                    "task": task["name"],
                    "assigned_to": best_agent["name"],
                    "estimated_time": task["estimated_hours"],
                    "dependencies": task.get("dependencies", [])
                })
        
        return plan
    
    @tool
    async def execute_task(self, task_id: str, instructions: str) -> str:
        """Execute task through assigned agent"""
        
        # Get task details
        task = self.get_task(task_id)
        if not task:
            return "Task not found"
        
        # Execute via assigned agent
        result = await self.nli.query_agent(
            agent_name=task["assigned_to"],
            query=instructions,
            context={
                "task_id": task_id,
                "project_context": self.get_project_context()
            }
        )
        
        # Update task status
        self.update_task_status(task_id, "completed", result)
        
        return result.get("response", "No response from agent")
    
    @hook("on_message")
    async def track_progress(self, context):
        """Track project progress"""
        message = context.messages[-1]["content"]
        
        # Detect status queries
        if "status" in message.lower() or "progress" in message.lower():
            context["show_progress"] = True
        
        return context

# Create coordinator
coordinator = BaseAgent(
    name="project-coordinator",
    instructions="""You are a project coordinator that manages tasks across multiple specialized agents.
    - Break down projects into tasks
    - Assign tasks to appropriate agents
    - Track progress and dependencies
    - Coordinate results""",
    model="openai/gpt-4o",
    skills={
        "coordinator": CoordinatorSkill(),
        "nli": NLISkill(),
        "discovery": DiscoverySkill()
    }
)
```

## Specialized Examples

### Code Assistant

```python
class CodeSkill(Skill):
    @tool
    def analyze_code(self, code: str, language: str = "python") -> Dict:
        """Analyze code for issues and improvements"""
        analysis = {
            "language": language,
            "lines": len(code.split("\n")),
            "complexity": "medium",  # Simplified
            "issues": [],
            "suggestions": []
        }
        
        # Basic analysis
        if "eval(" in code:
            analysis["issues"].append("Use of eval() is dangerous")
        
        if language == "python" and "import *" in code:
            analysis["issues"].append("Avoid wildcard imports")
        
        return analysis
    
    @tool
    def generate_tests(self, code: str, framework: str = "pytest") -> str:
        """Generate unit tests for code"""
        # Parse function names (simplified)
        functions = [line.split("def ")[1].split("(")[0] 
                    for line in code.split("\n") 
                    if line.strip().startswith("def ")]
        
        tests = [f"""
def test_{func}():
    # TODO: Implement test for {func}
    assert True  # Placeholder
""" for func in functions]
        
        return f"import {framework}\n" + "\n".join(tests)

# Create code assistant
code_assistant = BaseAgent(
    name="code-assistant",
    instructions="""You are an expert programming assistant.
    - Analyze code for best practices
    - Generate tests and documentation
    - Explain complex concepts clearly
    - Suggest improvements""",
    model="openai/gpt-4o",
    skills={"code": CodeSkill()}
)
```

### Personal Finance Advisor

```python
class FinanceSkill(Skill):
    @tool
    def calculate_budget(self, income: float, expenses: Dict[str, float]) -> Dict:
        """Calculate monthly budget"""
        total_expenses = sum(expenses.values())
        savings = income - total_expenses
        
        return {
            "income": income,
            "expenses": expenses,
            "total_expenses": total_expenses,
            "savings": savings,
            "savings_rate": (savings / income) * 100 if income > 0 else 0,
            "recommendations": self.get_budget_recommendations(income, expenses, savings)
        }
    
    @tool
    def investment_analysis(self, amount: float, years: int, rate: float = 7.0) -> Dict:
        """Analyze investment growth"""
        # Compound interest calculation
        future_value = amount * (1 + rate/100) ** years
        total_return = future_value - amount
        
        return {
            "initial_amount": amount,
            "years": years,
            "annual_rate": rate,
            "future_value": round(future_value, 2),
            "total_return": round(total_return, 2),
            "roi_percentage": round((total_return / amount) * 100, 2)
        }
    
    @handoff("tax-advisor")
    def needs_tax_advice(self, query: str) -> bool:
        """Route tax questions to specialist"""
        tax_keywords = ["tax", "deduction", "filing", "IRS", "return"]
        return any(keyword in query.lower() for keyword in tax_keywords)

# Create finance advisor
finance_advisor = BaseAgent(
    name="finance-advisor",
    instructions="""You are a personal finance advisor.
    - Help with budgeting and savings
    - Provide investment guidance
    - Explain financial concepts simply
    - Always include disclaimers about professional advice""",
    model="openai/gpt-4o",
    skills={
        "finance": FinanceSkill(),
        "memory": ShortTermMemorySkill()
    }
)
```

## Running Examples

### Basic Usage

```python
# Run any agent
async def main():
    # Simple query
    response = await chatbot.run([
        {"role": "user", "content": "Tell me a joke"}
    ])
    print(response.choices[0].message.content)
    
    # With streaming
    async for chunk in researcher.run_streaming([
        {"role": "user", "content": "Find papers about quantum computing"}
    ]):
        print(chunk.choices[0].delta.content, end="")

# Run with asyncio
import asyncio
asyncio.run(main())
```

### Server Deployment

```python
from robutler.server import app

# Register all agents
app.register_agent(chatbot)
app.register_agent(support_agent)
app.register_agent(researcher)
app.register_agent(coordinator)

# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Testing Agents

```python
import pytest

@pytest.mark.asyncio
async def test_math_tutor():
    response = await tutor.run([
        {"role": "user", "content": "Calculate 25 * 4"}
    ])
    
    assert "100" in response.choices[0].message.content

@pytest.mark.asyncio
async def test_support_handoff():
    response = await support_agent.run([
        {"role": "user", "content": "My app keeps crashing!"}
    ])
    
    # Should trigger handoff to technical support
    assert response.metadata.get("handoff_triggered") == True
``` 