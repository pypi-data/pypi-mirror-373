"""
NLI Skill - Natural Language Interface for Agent-to-Agent Communication

Provides HTTP-based communication between Robutler agents with natural language messages.
"""

from .skill import NLISkill, NLICommunication, AgentEndpoint

__all__ = [
    'NLISkill',
    'NLICommunication', 
    'AgentEndpoint'
]
