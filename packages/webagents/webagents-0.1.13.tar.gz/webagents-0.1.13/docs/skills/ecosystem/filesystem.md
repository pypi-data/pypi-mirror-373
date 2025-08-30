# Filesystem Skill

File and directory operations for agents.

## Features
- Read/write files
- List directories
- File metadata access

## Example: Add Filesystem Skill to an Agent
```python
from robutler.agents import BaseAgent
from robutler.agents.skills.ecosystem.filesystem import FilesystemSkill

agent = BaseAgent(
    name="fs-agent",
    model="openai/gpt-4o",
    skills={
        "filesystem": FilesystemSkill({})
    }
)
```

## Example: Use Filesystem Tool in a Skill
```python
from robutler.agents.skills import Skill, tool

class FileOpsSkill(Skill):
    def __init__(self):
        super().__init__()
        self.fs = self.agent.skills["filesystem"]

    @tool
    async def read_file(self, path: str) -> str:
        """Read a file from the filesystem"""
        return await self.fs.read_file(path)
```

**Implementation:** See `robutler/agents/skills/ecosystem/filesystem/skill.py`. 