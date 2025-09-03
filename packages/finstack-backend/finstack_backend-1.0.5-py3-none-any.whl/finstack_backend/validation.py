"""
Validation utilities that mirror the Zod schemas from shared TypeScript types.
Provides consistent validation between frontend and backend.
"""

import re
from typing import Dict, List, Optional, Tuple
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from .constants import MIN_PASSWORD_LENGTH, EMAIL_MAX_LENGTH, NAME_MAX_LENGTH


def validate_email_format(email: str) -> bool:
    """
    Validate email format matching TypeScript email validation.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not email or len(email) > EMAIL_MAX_LENGTH:
        return False
    
    try:
        validator = EmailValidator()
        validator(email)
        return True
    except ValidationError:
        return False


def validate_password_strength(password: str) -> Dict[str, any]:
    """
    Validate password strength matching TypeScript password validation.
    
    Args:
        password: Password to validate
        
    Returns:
        Dictionary with validation results
    """
    result = {
        'valid': True,
        'errors': [],
        'strength': 'weak'
    }
    
    if not password:
        result['valid'] = False
        result['errors'].append('Password is required')
        return result
    
    if len(password) < MIN_PASSWORD_LENGTH:
        result['valid'] = False
        result['errors'].append(f'Password must be at least {MIN_PASSWORD_LENGTH} characters')
    
    # Check password strength
    strength_score = 0
    
    if len(password) >= 8:
        strength_score += 1
    
    if re.search(r'[A-Z]', password):
        strength_score += 1
        
    if re.search(r'[a-z]', password):
        strength_score += 1
        
    if re.search(r'\d', password):
        strength_score += 1
        
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        strength_score += 1
    
    if strength_score >= 4:
        result['strength'] = 'strong'
    elif strength_score >= 2:
        result['strength'] = 'medium'
    else:
        result['strength'] = 'weak'
    
    return result


def validate_name(name: str, field_name: str = "Name") -> List[str]:
    """
    Validate name fields matching TypeScript validation.
    
    Args:
        name: Name to validate
        field_name: Field name for error messages
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    if not name or not name.strip():
        errors.append(f'{field_name} is required')
        return errors
    
    if len(name.strip()) < 2:
        errors.append(f'{field_name} is too short')
    
    if len(name) > NAME_MAX_LENGTH:
        errors.append(f'{field_name} is too long')
    
    return errors


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not phone:
        return True  # Phone is optional
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Must be 10 or 11 digits (US format)
    return len(digits_only) in [10, 11]


def format_phone_number(phone: str) -> str:
    """
    Format phone number to consistent format matching TypeScript helper.
    
    Args:
        phone: Phone number to format
        
    Returns:
        Formatted phone number
    """
    if not phone:
        return ''
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    if len(digits_only) == 10:
        # Format as (XXX) XXX-XXXX
        return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
    elif len(digits_only) == 11 and digits_only.startswith('1'):
        # Format as +1 (XXX) XXX-XXXX
        return f"+1 ({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:]}"
    
    return phone  # Return original if can't format


def validate_login_data(email: str, password: str) -> Dict[str, any]:
    """
    Validate login data matching TypeScript loginSchema.
    
    Args:
        email: Email address
        password: Password
        
    Returns:
        Validation result dictionary
    """
    result = {
        'valid': True,
        'errors': {}
    }
    
    # Validate email
    if not email:
        result['errors']['email'] = 'Email is required'
        result['valid'] = False
    elif not validate_email_format(email):
        result['errors']['email'] = 'Email must be a valid email address'
        result['valid'] = False
    
    # Validate password
    if not password:
        result['errors']['password'] = 'Password is required'
        result['valid'] = False
    elif len(password) < MIN_PASSWORD_LENGTH:
        result['errors']['password'] = f'Password must be at least {MIN_PASSWORD_LENGTH} characters'
        result['valid'] = False
    
    return result


def validate_register_data(first_name: str, last_name: str, email: str, password: str, confirm_password: str) -> Dict[str, any]:
    """
    Validate registration data matching TypeScript registerSchema.
    
    Args:
        first_name: First name
        last_name: Last name
        email: Email address
        password: Password
        confirm_password: Password confirmation
        
    Returns:
        Validation result dictionary
    """
    result = {
        'valid': True,
        'errors': {}
    }
    
    # Validate first name
    name_errors = validate_name(first_name, 'First name')
    if name_errors:
        result['errors']['first_name'] = name_errors[0]
        result['valid'] = False
    
    # Validate last name
    name_errors = validate_name(last_name, 'Last name')
    if name_errors:
        result['errors']['last_name'] = name_errors[0]
        result['valid'] = False
    
    # Validate email
    if not email:
        result['errors']['email'] = 'Email is required'
        result['valid'] = False
    elif not validate_email_format(email):
        result['errors']['email'] = 'Email must be a valid email address'
        result['valid'] = False
    
    # Validate password
    password_validation = validate_password_strength(password)
    if not password_validation['valid']:
        result['errors']['password'] = password_validation['errors'][0]
        result['valid'] = False
    
    # Validate password confirmation
    if password != confirm_password:
        result['errors']['confirm_password'] = "Passwords don't match"
        result['valid'] = False
    
    return result


def validate_password_reset_data(email: str) -> Dict[str, any]:
    """
    Validate password reset data matching TypeScript passwordResetSchema.
    
    Args:
        email: Email address
        
    Returns:
        Validation result dictionary
    """
    result = {
        'valid': True,
        'errors': {}
    }
    
    if not email:
        result['errors']['email'] = 'Email is required'
        result['valid'] = False
    elif not validate_email_format(email):
        result['errors']['email'] = 'Email must be a valid email address'
        result['valid'] = False
    
    return result


def validate_new_password_data(token: str, password: str, confirm_password: str) -> Dict[str, any]:
    """
    Validate new password data matching TypeScript newPasswordSchema.
    
    Args:
        token: Password reset token
        password: New password
        confirm_password: Password confirmation
        
    Returns:
        Validation result dictionary
    """
    result = {
        'valid': True,
        'errors': {}
    }
    
    if not token:
        result['errors']['token'] = 'Reset token is required'
        result['valid'] = False
    
    password_validation = validate_password_strength(password)
    if not password_validation['valid']:
        result['errors']['password'] = password_validation['message']
        result['valid'] = False
    
    if not confirm_password:
        result['errors']['confirm_password'] = 'Password confirmation is required'
        result['valid'] = False
    
    if password != confirm_password:
        result['errors']['confirm_password'] = "Passwords don't match"
        result['valid'] = False
    
    return result


def validate_change_password_data(old_password: str, new_password: str, confirm_password: str) -> Dict[str, any]:
    """
    Validate change password data matching TypeScript changePasswordSchema.
    
    Args:
        old_password: Current password
        new_password: New password
        confirm_password: New password confirmation
        
    Returns:
        Validation result dictionary
    """
    result = {
        'valid': True,
        'errors': {}
    }
    
    # Validate old password
    if not old_password:
        result['errors']['old_password'] = 'Current password is required'
        result['valid'] = False
    
    # Validate new password
    password_validation = validate_password_strength(new_password)
    if not password_validation['valid']:
        result['errors']['new_password'] = password_validation['errors'][0]
        result['valid'] = False
    
    # Validate password confirmation
    if new_password != confirm_password:
        result['errors']['confirm_password'] = "Passwords don't match"
        result['valid'] = False
    
    # Check if old and new passwords are different
    if old_password == new_password:
        result['errors']['new_password'] = 'New password must be different from current password'
        result['valid'] = False
    
    return result


class DjangoFormValidator:
    """
    Django form validator that uses shared validation functions.
    """
    
    @staticmethod
    def validate_email(value: str) -> str:
        """Django form validator for email"""
        if not validate_email_format(value):
            raise ValidationError('Email must be a valid email address')
        return value
    
    @staticmethod
    def validate_password(value: str) -> str:
        """Django form validator for password"""
        validation = validate_password_strength(value)
        if not validation['valid']:
            raise ValidationError(validation['errors'][0])
        return value
    
    @staticmethod
    def validate_name_field(value: str, field_name: str = "Name") -> str:
        """Django form validator for name fields"""
        errors = validate_name(value, field_name)
        if errors:
            raise ValidationError(errors[0])
        return value
    
    @staticmethod
    def validate_phone(value: str) -> str:
        """Django form validator for phone"""
        if value and not validate_phone_number(value):
            raise ValidationError('Phone number format is invalid')
        return value 