"""
Django REST Framework serializer utilities that match shared TypeScript API types.
Provides consistent API response formats for LoginResponse, ApiResponse, etc.
"""

from rest_framework import serializers
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
from django.conf import settings


class BaseAPISerializer(serializers.Serializer):
    """
    Base serializer that provides common API response structure.
    Matches TypeScript ApiResponse interface.
    """
    success = serializers.BooleanField(default=True)
    message = serializers.CharField(required=False, allow_blank=True)
    data = serializers.JSONField(required=False)
    
    class Meta:
        abstract = True


class ApiErrorSerializer(serializers.Serializer):
    """
    Error response serializer matching TypeScript ApiError interface.
    """
    success = serializers.BooleanField(default=False)
    message = serializers.CharField()
    errors = serializers.JSONField(required=False)
    code = serializers.CharField(required=False)


class PaginatedResponseSerializer(serializers.Serializer):
    """
    Paginated response serializer matching TypeScript PaginatedResponse interface.
    """
    data = serializers.ListField()
    pagination = serializers.DictField(child=serializers.IntegerField())
    
    def to_representation(self, instance):
        """Convert paginated queryset to expected format"""
        if hasattr(instance, 'results'):
            # Django REST pagination object
            return {
                'data': instance.results,
                'pagination': {
                    'page': getattr(instance, 'number', 1),
                    'limit': getattr(instance, 'paginator', {}).get('per_page', 10),
                    'total': getattr(instance, 'paginator', {}).get('count', 0),
                    'pages': getattr(instance, 'paginator', {}).get('num_pages', 1),
                }
            }
        return super().to_representation(instance)


class AccountSerializer(serializers.Serializer):
    """
    Account serializer matching TypeScript Account interface.
    Can be used as a base for user serialization.
    """
    id = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    name = serializers.CharField(read_only=True)
    role = serializers.CharField(required=False, allow_null=True)
    status = serializers.CharField(default='active')
    isVerified = serializers.BooleanField(default=False)
    avatarUrl = serializers.SerializerMethodField()
    company = serializers.CharField(required=False, allow_null=True)
    title = serializers.CharField(required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_null=True)
    address = serializers.CharField(required=False, allow_null=True)
    city = serializers.CharField(required=False, allow_null=True)
    state = serializers.CharField(required=False, allow_null=True)
    zip = serializers.CharField(required=False, allow_null=True)
    two_factor_enabled = serializers.BooleanField(default=False)
    is_admin_enabled = serializers.BooleanField(default=False)
    permissions = serializers.ListField(child=serializers.CharField(), default=list)
    subscription_level = serializers.CharField(default='basic')
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    def get_avatarUrl(self, obj) -> Optional[str]:
        """Get absolute URL for avatar image"""
        request = self.context.get('request')
        if hasattr(obj, 'avatarUrl') and obj.avatarUrl:
            if request:
                return request.build_absolute_uri(obj.avatarUrl.url)
            return obj.avatarUrl.url
        return None
    
    def validate_avatarUrl(self, value: str) -> str:
        """Validate and normalize avatar URL"""
        if not value:
            return value
            
        request = self.context.get('request')
        if request:
            url_parts = urlparse(value)
            if url_parts.netloc == request.get_host():
                # Convert absolute URL to relative path
                relative_path = url_parts.path
                if relative_path.startswith(settings.MEDIA_URL):
                    relative_path = relative_path[len(settings.MEDIA_URL):]
                return relative_path
        return value


class LoginRequestSerializer(serializers.Serializer):
    """
    Login request serializer matching TypeScript LoginRequest interface.
    """
    email = serializers.EmailField()
    password = serializers.CharField(min_length=5)


class LoginResponseSerializer(BaseAPISerializer):
    """
    Login response serializer matching TypeScript LoginResponse interface.
    """
    access = serializers.CharField()
    refresh = serializers.CharField()
    
    # Include all account fields
    id = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    name = serializers.CharField()
    role = serializers.CharField(allow_null=True)
    isVerified = serializers.BooleanField()
    two_factor_enabled = serializers.BooleanField()
    subscription_level = serializers.CharField()
    permissions = serializers.ListField(child=serializers.CharField())


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Password reset request matching TypeScript PasswordResetRequest interface.
    """
    email = serializers.EmailField()


class NewPasswordRequestSerializer(serializers.Serializer):
    """
    New password request matching TypeScript NewPasswordRequest interface.
    """
    token = serializers.CharField()
    password = serializers.CharField(min_length=8)


class ChangePasswordRequestSerializer(serializers.Serializer):
    """
    Change password request matching TypeScript ChangePasswordRequest interface.
    """
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=5)
    confirm_password = serializers.CharField()
    
    def validate(self, data):
        """Validate that passwords match"""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return data


def create_api_response(data: Any = None, message: str = "", success: bool = True) -> Dict[str, Any]:
    """
    Create a consistent API response matching TypeScript ApiResponse interface.
    
    Args:
        data: Response data
        message: Success/error message
        success: Whether the operation was successful
        
    Returns:
        Dictionary matching TypeScript ApiResponse interface
    """
    response = {'success': success}
    
    if message:
        response['message'] = message
    
    if data is not None:
        response['data'] = data
    
    return response


def create_error_response(message: str, errors: Optional[Dict[str, Any]] = None, code: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a consistent error response matching TypeScript ApiError interface.
    
    Args:
        message: Error message
        errors: Detailed error information
        code: Error code
        
    Returns:
        Dictionary matching TypeScript ApiError interface
    """
    response = {
        'success': False,
        'message': message
    }
    
    if errors:
        response['errors'] = errors
    
    if code:
        response['code'] = code
    
    return response


def create_validation_error_response(serializer_errors: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    Create error response from Django REST serializer validation errors.
    
    Args:
        serializer_errors: Django REST serializer errors
        
    Returns:
        Dictionary matching TypeScript ApiError interface
    """
    # Flatten field errors into a more readable format
    formatted_errors = {}
    for field, errors in serializer_errors.items():
        if isinstance(errors, list):
            formatted_errors[field] = errors[0] if errors else "Invalid value"
        else:
            formatted_errors[field] = str(errors)
    
    return create_error_response(
        message="Validation failed",
        errors=formatted_errors,
        code="VALIDATION_ERROR"
    ) 