# CodeFinal Shared Backend Utilities

Shared Django utilities, models, serializers, and validation that mirror the TypeScript shared types. This package ensures consistency between your Django backend and React frontend for the CodeFinal fire inspection system.

## Installation

```bash
# From your Django project directory
pip install -e /path/to/packages/backend-utils
```

Or add to your `requirements.txt`:
```txt
-e /path/to/packages/backend-utils
```

## Quick Start

### 1. Update Your Django User Model

Replace your existing Django user model imports with shared utilities:

```python
# accounts/models.py
from codefinal_shared import (
    UUIDMixin, TimestampMixin, AccountFieldsMixin, 
    SharedUserManager, ROLE_CHOICES, STATUS_CHOICES
)
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser, UUIDMixin, TimestampMixin, AccountFieldsMixin):
    objects = SharedUserManager()
    
    class Meta:
        ordering = ["-created_at"]
```

### 2. Update Your Serializers

Use shared serializers for consistent API responses:

```python
# accounts/serializers.py
from codefinal_shared import (
    AccountSerializer, LoginRequestSerializer, LoginResponseSerializer,
    create_api_response, create_error_response
)

class UserSerializer(AccountSerializer):
    class Meta(AccountSerializer.Meta):
        model = CustomUser
        # Add any additional fields specific to your implementation
```

### 3. Update Your Views

Use shared authentication and validation utilities:

```python
# accounts/views.py
from codefinal_shared import (
    authenticate_user, AuthTokenManager, 
    validate_login_data, create_api_response
)

@api_view(['POST'])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    # Use shared authentication
    result = authenticate_user(email, password)
    
    return Response(result, status=200 if result['success'] else 400)
```

## Core Components

### Constants
```python
from codefinal_shared import AccountRole, AccountStatus, SubscriptionLevel

# Use enum values that match TypeScript
user.role = AccountRole.ADMINISTRATOR.value
user.status = AccountStatus.ACTIVE.value
```

### Model Mixins
```python
from codefinal_shared import UUIDMixin, TimestampMixin, AccountFieldsMixin

class YourModel(UUIDMixin, TimestampMixin):
    # Automatically gets UUID primary key and created_at/updated_at fields
    pass
```

### Serializers
```python
from codefinal_shared import AccountSerializer, create_api_response

# Consistent API responses
return create_api_response(
    data=user_data,
    message="Operation successful"
)
```

### Validation
```python
from codefinal_shared import validate_login_data, validate_email_format

# Validation that matches frontend Zod schemas
validation_result = validate_login_data(email, password)
if not validation_result['valid']:
    return create_error_response("Validation failed", validation_result['errors'])
```

### Authentication
```python
from codefinal_shared import AuthTokenManager, TwoFactorAuthMixin

# JWT token management
tokens = AuthTokenManager.create_tokens_for_user(user)

# Two-factor authentication
class CustomUser(AbstractUser, TwoFactorAuthMixin):
    def setup_2fa(self):
        return self.enable_two_factor()
```

## Features

### ✅ Type Consistency
All utilities match the shared TypeScript types exactly, ensuring frontend and backend stay in sync.

### ✅ Validation Matching
Python validation functions mirror the Zod schemas from the frontend, providing identical validation logic.

### ✅ API Response Format
Consistent API response structure matching `TypeScript ApiResponse` and `ApiError` interfaces.

### ✅ Authentication Utilities
Complete JWT token management and two-factor authentication support.

### ✅ Django Integration
Drop-in replacements for common Django patterns with enhanced type safety.

## Available Utilities

### Models
- `UUIDMixin` - UUID primary key
- `TimestampMixin` - created_at/updated_at fields  
- `AccountFieldsMixin` - Complete user account fields
- `TenantAwareMixin` - Subscription level support
- `SharedUserManager` - Consistent user creation

### Serializers  
- `AccountSerializer` - User account serialization
- `LoginRequestSerializer` - Login request validation
- `LoginResponseSerializer` - Login response format
- `PaginatedResponseSerializer` - Paginated API responses

### Validation
- `validate_email_format()` - Email validation matching frontend
- `validate_password_strength()` - Password strength checking
- `validate_login_data()` - Complete login validation
- `DjangoFormValidator` - Django form integration

### Authentication
- `AuthTokenManager` - JWT token creation/management
- `TwoFactorAuthMixin` - TOTP two-factor authentication
- `authenticate_user()` - Complete authentication flow
- `create_user_permissions_list()` - Permission management

### Constants
- `AccountRole` - User roles enum
- `AccountStatus` - Account status enum  
- `SubscriptionLevel` - Subscription level enum
- `ROLE_CHOICES`, `STATUS_CHOICES` - Django choices

## Migration Guide

### From Existing Django Project

1. **Install the package**:
   ```bash
   pip install -e /path/to/packages/backend-utils
   ```

2. **Update your models** to use shared mixins:
   ```python
   # Before
   class CustomUser(AbstractUser):
       id = models.UUIDField(primary_key=True, default=uuid.uuid4)
       role = models.CharField(max_length=100, choices=ROLE_CHOICES)
   
   # After  
   from codefinal_shared import UUIDMixin, AccountFieldsMixin
   class CustomUser(AbstractUser, UUIDMixin, AccountFieldsMixin):
       pass  # Fields are provided by mixins
   ```

3. **Update serializers** to use shared formats:
   ```python
   # Before
   class UserSerializer(serializers.ModelSerializer):
       # Custom serialization logic
   
   # After
   from codefinal_shared import AccountSerializer
   class UserSerializer(AccountSerializer):
       # Inherits consistent serialization
   ```

4. **Update views** to use shared utilities:
   ```python
   # Before
   def login_view(request):
       # Custom authentication logic
   
   # After
   from codefinal_shared import authenticate_user
   def login_view(request):
       return authenticate_user(email, password)
   ```

## Benefits

### 🎯 **Type Safety**
Ensures your Django models exactly match the TypeScript interfaces used in the frontend.

### 🔄 **Consistency**  
Identical validation, serialization, and response formats between frontend and backend.

### 🚀 **Productivity**
Drop-in utilities eliminate boilerplate code and reduce development time.

### 🛡️ **Reliability**
Shared validation logic prevents frontend/backend mismatches that cause bugs.

### 📈 **Scalability**
Easily extend utilities as your application grows, with changes automatically reflected across projects.

## License

MIT License - matches the main CodeFinal project licensing. 