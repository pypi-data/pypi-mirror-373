# n8n Skill

Integrate with n8n automation workflows.

## Features
- Trigger n8n workflows
- Exchange data with n8n

## Example: Add n8n Skill to an Agent
```python
from robutler.agents import BaseAgent
from robutler.agents.skills.ecosystem.n8n import N8nSkill

agent = BaseAgent(
    name="n8n-agent",
    model="openai/gpt-4o",
    skills={
        "n8n": N8nSkill({})
    }
)
```

## Example: Use n8n Tool in a Skill
```python
from robutler.agents.skills import Skill, tool

class N8nOpsSkill(Skill):
    def __init__(self):
        super().__init__()
        self.n8n = self.agent.skills["n8n"]

    @tool
    async def trigger_workflow(self, workflow_id: str, data: dict) -> str:
        """Trigger an n8n workflow"""
        return await self.n8n.trigger(workflow_id, data)
```

**Implementation:** See `robutler/agents/skills/ecosystem/n8n/skill.py`. 