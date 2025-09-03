"""
Constants and choices that mirror the shared TypeScript types.
These should be used in Django models to ensure consistency with frontend types.
"""

from enum import Enum
from typing import Tuple, List


class AccountRole(Enum):
    """Account roles matching TypeScript AccountRole enum"""
    ADMINISTRATOR = "Administrator"
    CONTRACTOR = "Contractor" 
    INSPECTOR = "Inspector"
    USER = "User"
    
    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        """Django model choices format"""
        return [(role.value, role.value) for role in cls]


class AccountStatus(Enum):
    """Account status matching TypeScript AccountStatus enum"""
    ACTIVE = "active"
    BANNED = "banned"
    
    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        """Django model choices format"""
        return [(status.value, status.value.upper()) for status in cls]


class SubscriptionLevel(Enum):
    """Subscription levels matching TypeScript SubscriptionLevel enum"""
    BASIC = "basic"
    PROFESSIONAL = "professional"
    
    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        """Django model choices format"""
        return [(level.value, level.value.upper()) for level in cls]


# Django choices - can be used directly in model fields
ROLE_CHOICES = AccountRole.choices()
STATUS_CHOICES = AccountStatus.choices()
SUBSCRIPTION_LEVEL_CHOICES = SubscriptionLevel.choices()

# Default values matching TypeScript defaults
DEFAULT_ROLE = AccountRole.USER.value
DEFAULT_STATUS = AccountStatus.ACTIVE.value
DEFAULT_SUBSCRIPTION = SubscriptionLevel.PROFESSIONAL.value

# Validation constants
MIN_PASSWORD_LENGTH = 5
EMAIL_MAX_LENGTH = 254
NAME_MAX_LENGTH = 50
PHONE_MAX_LENGTH = 20
ADDRESS_MAX_LENGTH = 100 