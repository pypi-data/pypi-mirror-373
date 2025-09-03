"""
Authentication utilities for JWT tokens, two-factor authentication, and user management.
Provides consistent authentication patterns matching frontend expectations.
"""

import pyotp
from typing import Dict, Any, Optional, Union
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import create_api_response, create_error_response
from .validation import validate_login_data
from .models import get_user_data_dict


class AuthTokenManager:
    """
    Manages JWT token creation and validation for consistent authentication.
    """
    
    @staticmethod
    def create_tokens_for_user(user) -> Dict[str, str]:
        """
        Create access and refresh tokens for a user.
        
        Args:
            user: Django user instance
            
        Returns:
            Dictionary with access and refresh tokens
        """
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
    
    @staticmethod
    def create_login_response(user, include_tokens: bool = True) -> Dict[str, Any]:
        """
        Create login response matching TypeScript LoginResponse interface.
        
        Args:
            user: Django user instance
            include_tokens: Whether to include JWT tokens
            
        Returns:
            Login response dictionary
        """
        user_data = get_user_data_dict(user)
        
        if include_tokens:
            tokens = AuthTokenManager.create_tokens_for_user(user)
            user_data.update(tokens)
        
        return user_data


class TwoFactorAuthMixin:
    """
    Mixin for models that provides two-factor authentication functionality.
    """
    
    def generate_otp_secret(self) -> str:
        """Generate a new OTP secret for two-factor authentication."""
        return pyotp.random_base32()
    
    def get_totp_uri(self, issuer_name: str = "CodeFinal") -> str:
        """
        Get TOTP URI for QR code generation.
        
        Args:
            issuer_name: Name of the service issuing the token
            
        Returns:
            TOTP URI string
        """
        if not hasattr(self, 'otp_secret') or not self.otp_secret:
            return ""
        
        totp = pyotp.TOTP(self.otp_secret)
        return totp.provisioning_uri(
            name=self.email,
            issuer_name=issuer_name
        )
    
    def verify_totp_token(self, token: str) -> bool:
        """
        Verify a TOTP token.
        
        Args:
            token: 6-digit TOTP token
            
        Returns:
            True if token is valid, False otherwise
        """
        if not hasattr(self, 'otp_secret') or not self.otp_secret:
            return False
        
        totp = pyotp.TOTP(self.otp_secret)
        return totp.verify(token)
    
    def enable_two_factor(self) -> str:
        """
        Enable two-factor authentication for the user.
        
        Returns:
            New OTP secret
        """
        if not hasattr(self, 'otp_secret') or not self.otp_secret:
            self.otp_secret = self.generate_otp_secret()
        
        self.two_factor_enabled = True
        self.save()
        return self.otp_secret
    
    def disable_two_factor(self) -> None:
        """Disable two-factor authentication for the user."""
        self.two_factor_enabled = False
        self.otp_secret = None
        self.save()


def authenticate_user(email: str, password: str) -> Dict[str, Any]:
    """
    Authenticate user with email and password.
    Returns consistent response format matching TypeScript expectations.
    
    Args:
        email: User email
        password: User password
        
    Returns:
        Authentication response dictionary
    """
    # Validate input data
    validation = validate_login_data(email, password)
    if not validation['valid']:
        return create_error_response(
            message="Invalid login data",
            errors=validation['errors'],
            code="VALIDATION_ERROR"
        )
    
    # Attempt authentication
    user = authenticate(username=email, password=password)
    
    if user is None:
        return create_error_response(
            message="Invalid email or password",
            code="INVALID_CREDENTIALS"
        )
    
    if not user.is_active:
        return create_error_response(
            message="Account is disabled",
            code="ACCOUNT_DISABLED"
        )
    
    # Check if account is verified (if required)
    if hasattr(user, 'isVerified') and not user.isVerified:
        return create_error_response(
            message="Please verify your email address",
            code="EMAIL_NOT_VERIFIED"
        )
    
    # Create successful response
    login_data = AuthTokenManager.create_login_response(user)
    
    return create_api_response(
        data=login_data,
        message="Login successful"
    )


def verify_two_factor_token(user, token: str) -> Dict[str, Any]:
    """
    Verify two-factor authentication token.
    
    Args:
        user: Django user instance
        token: 6-digit TOTP token
        
    Returns:
        Verification response dictionary
    """
    if not hasattr(user, 'two_factor_enabled') or not user.two_factor_enabled:
        return create_error_response(
            message="Two-factor authentication is not enabled",
            code="2FA_NOT_ENABLED"
        )
    
    if not token or len(token) != 6:
        return create_error_response(
            message="Invalid token format",
            code="INVALID_TOKEN_FORMAT"
        )
    
    if not hasattr(user, 'verify_totp_token') or not user.verify_totp_token(token):
        return create_error_response(
            message="Invalid or expired token",
            code="INVALID_TOKEN"
        )
    
    return create_api_response(
        message="Token verified successfully"
    )


def create_user_permissions_list(user) -> list:
    """
    Create permissions list for user matching TypeScript Account.permissions format.
    
    Args:
        user: Django user instance
        
    Returns:
        List of permission strings
    """
    permissions = []
    
    if hasattr(user, 'is_superuser') and user.is_superuser:
        permissions.append('superuser')
    
    if hasattr(user, 'is_staff') and user.is_staff:
        permissions.append('staff')
    
    if hasattr(user, 'is_admin_enabled') and user.is_admin_enabled:
        permissions.append('admin')
    
    # Add role-based permissions
    if hasattr(user, 'role') and user.role:
        role_permissions = {
            'Administrator': ['admin', 'manage_users', 'manage_settings'],
            'Inspector': ['inspect', 'create_reports'],
            'Contractor': ['view_projects', 'submit_documents'],
            'User': ['view_basic']
        }
        
        if user.role in role_permissions:
            permissions.extend(role_permissions[user.role])
    
    # Add Django permissions if available
    if hasattr(user, 'user_permissions'):
        django_perms = user.user_permissions.values_list('codename', flat=True)
        permissions.extend(django_perms)
    
    return list(set(permissions))  # Remove duplicates


def get_user_role_display(user) -> str:
    """
    Get user role display name matching TypeScript AccountRole values.
    
    Args:
        user: Django user instance
        
    Returns:
        Role display string
    """
    if hasattr(user, 'role') and user.role:
        return user.role
    
    if hasattr(user, 'is_superuser') and user.is_superuser:
        return 'Administrator'
    
    return 'User'


def check_user_permission(user, permission: str) -> bool:
    """
    Check if user has a specific permission.
    
    Args:
        user: Django user instance
        permission: Permission string to check
        
    Returns:
        True if user has permission, False otherwise
    """
    if isinstance(user, AnonymousUser):
        return False
    
    permissions = create_user_permissions_list(user)
    return permission in permissions


def require_permission(permission: str):
    """
    Decorator to require specific permission for a view.
    
    Args:
        permission: Required permission string
        
    Returns:
        Decorator function
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not check_user_permission(request.user, permission):
                return create_error_response(
                    message="Insufficient permissions",
                    code="PERMISSION_DENIED"
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def get_user_subscription_level(user) -> str:
    """
    Get user subscription level matching TypeScript SubscriptionLevel values.
    
    Args:
        user: Django user instance
        
    Returns:
        Subscription level string
    """
    if hasattr(user, 'subscription_level'):
        return user.subscription_level
    
    # Check if user has tenant with subscription level
    if hasattr(user, 'tenant') and hasattr(user.tenant, 'subscription_level'):
        return user.tenant.subscription_level
    
    return 'basic'  # Default subscription level


# Password Reset Utilities
def generate_password_reset_token(user) -> str:
    """
    Generate a secure password reset token for a user.
    
    Args:
        user: Django user instance
        
    Returns:
        Password reset token string
    """
    from django.contrib.auth.tokens import default_token_generator
    return default_token_generator.make_token(user)


def verify_password_reset_token(user, token: str) -> bool:
    """
    Verify a password reset token for a user.
    
    Args:
        user: Django user instance
        token: Token to verify
        
    Returns:
        True if token is valid, False otherwise
    """
    from django.contrib.auth.tokens import default_token_generator
    return default_token_generator.check_token(user, token)


def send_password_reset_email(user, token: str, reset_url: str, from_email: str = None) -> bool:
    """
    Send password reset email to user.
    
    Args:
        user: Django user instance
        token: Password reset token
        reset_url: Base URL for password reset (token will be appended)
        from_email: Sender email address
        
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = 'Password Reset Request'
        reset_link = f"{reset_url}?token={token}"
        
        message = f"""
        Hi {user.first_name or user.email},
        
        You have requested a password reset for your account.
        
        Click the link below to reset your password:
        {reset_link}
        
        If you did not request this password reset, please ignore this email.
        
        This link will expire in 24 hours.
        
        Best regards,
        The Team
        """
        
        html_message = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hi {user.first_name or user.email},</p>
            <p>You have requested a password reset for your account.</p>
            <p><a href="{reset_link}" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Your Password</a></p>
            <p>If you did not request this password reset, please ignore this email.</p>
            <p>This link will expire in 24 hours.</p>
            <p>Best regards,<br>The Team</p>
        </body>
        </html>
        """
        
        send_mail(
            subject=subject,
            message=message,
            html_message=html_message,
            from_email=from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send password reset email: {e}")
        return False


def reset_user_password(user, new_password: str) -> bool:
    """
    Reset user password and save the user.
    
    Args:
        user: Django user instance
        new_password: New password to set
        
    Returns:
        True if password was reset successfully, False otherwise
    """
    try:
        user.set_password(new_password)
        user.save()
        return True
    except Exception as e:
        print(f"Failed to reset user password: {e}")
        return False 