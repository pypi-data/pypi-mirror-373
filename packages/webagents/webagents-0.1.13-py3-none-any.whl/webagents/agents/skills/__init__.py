"""
Robutler Agents Skills

This module provides the skill system for Robutler agents, including core skills,
platform skills, and ecosystem skills. Skills are modular components that provide
specific functionality to agents.
"""

from .base import Skill, Handoff, HandoffResult

# Import all core skills that are always available
from .core.llm.litellm import LiteLLMSkill

# Core skills - these are fundamental and always available
CORE_SKILLS = {
    "litellm": LiteLLMSkill,
}

# Import Robutler platform skills
from .robutler.crm import CRMAnalyticsSkill

# Robutler platform skills - these integrate with Robutler services
ROBUTLER_SKILLS = {
    "crm": CRMAnalyticsSkill,
    "analytics": CRMAnalyticsSkill,  # Alias for convenience
}

# Ecosystem skills - these integrate with external services
ECOSYSTEM_SKILLS = {
    # Will be populated as ecosystem integrations are implemented
}

# Combined skills registry
ALL_SKILLS = {
    **CORE_SKILLS,
    **ROBUTLER_SKILLS, 
    **ECOSYSTEM_SKILLS
}

# Export main classes and registries
__all__ = [
    # Base classes
    'Skill',
    'Handoff', 
    'HandoffResult',
    
    # Skill registries
    'CORE_SKILLS',
    'ROBUTLER_SKILLS',
    'ECOSYSTEM_SKILLS', 
    'ALL_SKILLS',
    
    # Core skills
    'LiteLLMSkill',
]

# Lazy loading for ecosystem skills to avoid heavy imports
def get_skill(skill_name: str):
    """Get a skill class by name, with lazy loading for ecosystem skills
    
    Args:
        skill_name: Name of the skill to load
        
    Returns:
        Skill class if found, None otherwise
    """
    # Check core skills first
    if skill_name in CORE_SKILLS:
        return CORE_SKILLS[skill_name]
    
    # Check platform skills
    if skill_name in ROBUTLER_SKILLS:
        return ROBUTLER_SKILLS[skill_name]
    
    # Lazy load ecosystem skills
    ecosystem_imports = {
        "google": ("robutler.agents.skills.ecosystem.google", "GoogleSkill"),
        "database": ("robutler.agents.skills.ecosystem.database", "DatabaseSkill"),
        "filesystem": ("robutler.agents.skills.ecosystem.filesystem", "FilesystemSkill"),
        "web": ("robutler.agents.skills.ecosystem.web", "WebSkill"),
        "crewai": ("robutler.agents.skills.ecosystem.crewai", "CrewAISkill"),
        "n8n": ("robutler.agents.skills.ecosystem.n8n", "N8nSkill"),
        "zapier": ("robutler.agents.skills.ecosystem.zapier", "ZapierSkill"),
    }
    
    if skill_name in ecosystem_imports:
        try:
            module_path, class_name = ecosystem_imports[skill_name]
            module = __import__(module_path, fromlist=[class_name])
            skill_class = getattr(module, class_name)
            ECOSYSTEM_SKILLS[skill_name] = skill_class
            return skill_class
        except ImportError:
            # Ecosystem skill not available
            return None
    
    return None

def list_available_skills() -> dict:
    """List all available skills by category
    
    Returns:
        Dict with skill categories and their available skills
    """
    return {
        "core": list(CORE_SKILLS.keys()),
        "webagents": list(ROBUTLER_SKILLS.keys()),
        "ecosystem": list(ECOSYSTEM_SKILLS.keys())
    }
