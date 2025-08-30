# Crewai Skill

Integrate with the Crewai agent ecosystem.

## Features
- Register and discover Crewai agents
- Interoperate with Crewai workflows

## Example: Add Crewai Skill to an Agent
```python
from robutler.agents import BaseAgent
from robutler.agents.skills.ecosystem.crewai import CrewaiSkill

agent = BaseAgent(
    name="crewai-agent",
    model="openai/gpt-4o",
    skills={
        "crewai": CrewaiSkill({})
    }
)
```

## Example: Use Crewai Tool in a Skill
```python
from robutler.agents.skills import Skill, tool

class CrewaiOpsSkill(Skill):
    def __init__(self):
        super().__init__()
        self.crewai = self.agent.skills["crewai"]

    @tool
    async def list_agents(self) -> str:
        """List available Crewai agents"""
        return await self.crewai.list_agents()
```

**Implementation:** See `robutler/agents/skills/ecosystem/crewai/skill.py`. 