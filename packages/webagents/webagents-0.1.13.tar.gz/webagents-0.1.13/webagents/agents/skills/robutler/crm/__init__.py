"""
CRM & Analytics Skill Package - Robutler Platform Integration

CRM and analytics skill for Robutler platform.
Provides contact management and event tracking capabilities.
"""

from .skill import (
    CRMAnalyticsSkill,
    Contact,
    AnalyticsEvent
)

__all__ = [
    "CRMAnalyticsSkill",
    "Contact", 
    "AnalyticsEvent"
]
