"""
Django model mixins and utilities that match shared TypeScript types.
These can be used to ensure consistency between Django models and frontend types.
"""

import uuid
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.core.validators import MinLengthValidator, EmailValidator
from typing import Optional, Dict, Any
from .constants import (
    ROLE_CHOICES, STATUS_CHOICES, SUBSCRIPTION_LEVEL_CHOICES,
    DEFAULT_ROLE, DEFAULT_STATUS, EMAIL_MAX_LENGTH, NAME_MAX_LENGTH,
    PHONE_MAX_LENGTH, ADDRESS_MAX_LENGTH, MIN_PASSWORD_LENGTH
)


class TimestampMixin(models.Model):
    """
    Provides created_at and updated_at timestamps.
    Matches the timestamp fields in TypeScript Account interface.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    """
    Provides UUID primary key field.
    Matches the TypeScript Account.id field type.
    """
    id = models.UUIDField(
        primary_key=True, 
        unique=True,
        default=uuid.uuid4, 
        editable=False
    )
    
    class Meta:
        abstract = True


class AccountFieldsMixin(models.Model):
    """
    Provides account-related fields that match TypeScript Account interface.
    Can be used to extend Django's User model or other account-related models.
    """
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        validators=[EmailValidator()]
    )
    first_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        validators=[MinLengthValidator(2)]
    )
    last_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        validators=[MinLengthValidator(2)]
    )
    role = models.CharField(
        max_length=100,
        choices=ROLE_CHOICES,
        default=DEFAULT_ROLE,
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=100,
        choices=STATUS_CHOICES,
        default=DEFAULT_STATUS
    )
    isVerified = models.BooleanField(default=False)
    
    # Optional profile fields
    avatarUrl = models.ImageField(
        upload_to='users',
        null=True,
        blank=True,
        max_length=800
    )
    company = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    title = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    phone = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        null=True,
        blank=True
    )
    address = models.CharField(
        max_length=ADDRESS_MAX_LENGTH,
        null=True,
        blank=True
    )
    city = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    state = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    zip = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    
    # Two-factor authentication
    two_factor_enabled = models.BooleanField(default=False)
    otp_secret = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        editable=False
    )
    
    # Permissions
    is_admin_enabled = models.BooleanField(default=False)
    
    @property
    def name(self) -> str:
        """Full name property matching TypeScript Account.name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def permissions(self) -> list:
        """Permissions array matching TypeScript Account.permissions"""
        # Override in subclasses to return actual permissions
        return []
    
    class Meta:
        abstract = True


class TenantAwareMixin(models.Model):
    """
    Provides subscription_level field for tenant-aware models.
    Matches the TypeScript SubscriptionLevel enum.
    """
    subscription_level = models.CharField(
        max_length=100,
        choices=SUBSCRIPTION_LEVEL_CHOICES,
        default='professional'
    )
    
    class Meta:
        abstract = True


class SharedUserManager(BaseUserManager):
    """
    User manager that provides consistent user creation methods.
    Matches the patterns expected by TypeScript LoginRequest/RegisterRequest.
    """
    
    def _create_user(self, email: str, password: Optional[str] = None, **extra_fields) -> 'models.Model':
        """Create and save a user with the given email and password."""
        if not email:
            raise ValueError('The email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        
        if password:
            user.set_password(password)
        
        user.save(using=self._db)
        return user
    
    def create_user(self, email: str, password: Optional[str] = None, **extra_fields) -> 'models.Model':
        """Create a regular user."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email: str, password: str, **extra_fields) -> 'models.Model':
        """Create a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self._create_user(email, password, **extra_fields)


def get_user_data_dict(user) -> Dict[str, Any]:
    """
    Convert a Django user instance to a dictionary matching TypeScript Account interface.
    
    Args:
        user: Django user instance
        
    Returns:
        Dictionary matching TypeScript Account interface
    """
    return {
        'id': str(user.id) if hasattr(user, 'id') else None,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'name': user.name if hasattr(user, 'name') else f"{user.first_name} {user.last_name}".strip(),
        'role': user.role if hasattr(user, 'role') else None,
        'status': user.status if hasattr(user, 'status') else 'active',
        'isVerified': user.isVerified if hasattr(user, 'isVerified') else False,
        'avatarUrl': user.avatarUrl.url if hasattr(user, 'avatarUrl') and user.avatarUrl else None,
        'company': user.company if hasattr(user, 'company') else None,
        'title': user.title if hasattr(user, 'title') else None,
        'phone': user.phone if hasattr(user, 'phone') else None,
        'address': user.address if hasattr(user, 'address') else None,
        'city': user.city if hasattr(user, 'city') else None,
        'state': user.state if hasattr(user, 'state') else None,
        'zip': user.zip if hasattr(user, 'zip') else None,
        'two_factor_enabled': user.two_factor_enabled if hasattr(user, 'two_factor_enabled') else False,
        'is_admin_enabled': user.is_admin_enabled if hasattr(user, 'is_admin_enabled') else False,
        'permissions': user.permissions if hasattr(user, 'permissions') else [],
        'subscription_level': user.subscription_level if hasattr(user, 'subscription_level') else 'basic',
        'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') else None,
        'updated_at': user.updated_at.isoformat() if hasattr(user, 'updated_at') else None,
    } 