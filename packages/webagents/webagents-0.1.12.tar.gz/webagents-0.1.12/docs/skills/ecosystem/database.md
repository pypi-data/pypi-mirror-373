# Database Skill

Database access and query execution for agents.

## Features
- Connect to databases
- Run SQL queries
- Fetch and update records

## Example: Add Database Skill to an Agent
```python
from robutler.agents import BaseAgent
from robutler.agents.skills.ecosystem.database import DatabaseSkill

agent = BaseAgent(
    name="db-agent",
    model="openai/gpt-4o",
    skills={
        "database": DatabaseSkill({})
    }
)
```

## Example: Use Database Tool in a Skill
```python
from robutler.agents.skills import Skill, tool

class QuerySkill(Skill):
    def __init__(self):
        super().__init__()
        self.db = self.agent.skills["database"]

    @tool
    async def run_query(self, sql: str) -> str:
        """Run a SQL query"""
        return await self.db.query(sql)
```

**Implementation:** See `robutler/agents/skills/ecosystem/database/skill.py`. 