"""
DiscoverySkill Package - Simplified Robutler Platform Integration

Agent discovery skill for Robutler platform.
Provides intent-based agent discovery and intent publishing capabilities.
"""

from .skill import (
    DiscoverySkill,
    DiscoveryResult
)

__all__ = [
    "DiscoverySkill",
    "DiscoveryResult"
]
