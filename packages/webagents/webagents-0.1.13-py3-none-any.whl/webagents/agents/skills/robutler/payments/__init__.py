"""
PaymentSkill Package - Robutler V2.0

Payment processing and billing skill for Robutler platform.
Validates payment tokens, calculates costs using LiteLLM, and charges on connection finalization.
Based on robutler_v1 implementation patterns.
"""

from .skill import PaymentSkill, PaymentContext, PricingInfo, pricing
from .exceptions import (
    PaymentError,
    PaymentTokenRequiredError,
    PaymentTokenInvalidError,
    InsufficientBalanceError,
    PaymentChargingError,
    PaymentPlatformUnavailableError,
    PaymentConfigurationError,
    # Legacy compatibility
    PaymentValidationError,
    PaymentRequiredError
)

__all__ = [
    # Main classes
    "PaymentSkill", 
    "PaymentContext",
    # Pricing decorators
    "PricingInfo",
    "pricing",
    # New comprehensive error hierarchy
    "PaymentError",
    "PaymentTokenRequiredError",
    "PaymentTokenInvalidError",
    "InsufficientBalanceError",
    "PaymentChargingError",
    "PaymentPlatformUnavailableError",
    "PaymentConfigurationError",
    # Legacy compatibility
    "PaymentValidationError",
    "PaymentRequiredError"
]
