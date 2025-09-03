"""
Enhanced Two-Factor Authentication utilities with verification step.
Prevents user lockouts by requiring confirmation before enabling 2FA.
"""
import base64
import io
import pyotp
import qrcode
from typing import Dict, Any, Optional
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings

User = get_user_model()


class TwoFactorSetupManager:
    """
    Manages enhanced 2FA setup process with verification step.
    
    Flow:
    1. init_setup() - Generate secret and QR code, store temporarily
    2. verify_setup() - Verify user scanned correctly, then enable 2FA
    3. disable() - Disable 2FA immediately
    """
    
    TEMP_SECRET_CACHE_PREFIX = 'temp_2fa_secret'
    TEMP_SECRET_TIMEOUT = 300  # 5 minutes
    
    @classmethod
    def init_setup(cls, user) -> Dict[str, Any]:
        """
        Initialize 2FA setup by generating secret and QR code.
        Does NOT enable 2FA yet - requires verification.
        
        Returns:
            dict: Contains 'secret', 'qr_code' (base64), 'backup_codes'
        """
        # Generate new secret
        secret = pyotp.random_base32()
        
        # Store secret temporarily (not in user model yet)
        cache_key = f'{cls.TEMP_SECRET_CACHE_PREFIX}:{user.id}'
        cache.set(cache_key, secret, cls.TEMP_SECRET_TIMEOUT)
        
        # Generate QR code
        issuer_name = getattr(settings, 'TWO_FACTOR_ISSUER_NAME', 'FinStack App')
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name=issuer_name
        )
        
        # Create QR code image
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        # Convert to base64 for frontend
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        qr_code_data_url = f"data:image/png;base64,{qr_code_base64}"
        
        return {
            'secret': secret,
            'qr_code': qr_code_data_url,
            'backup_codes': cls._generate_backup_codes()
        }
    
    @classmethod
    def verify_setup(cls, user, verification_code: str, secret: str) -> Dict[str, Any]:
        """
        Verify the 2FA setup by checking the code and enabling 2FA.
        
        Args:
            user: User instance
            verification_code: 6-digit code from authenticator app
            secret: The secret that was generated in init_setup
            
        Returns:
            dict: Success/error result
            
        Raises:
            ValueError: If verification fails or secret is invalid
        """
        # Get temporary secret from cache
        cache_key = f'{cls.TEMP_SECRET_CACHE_PREFIX}:{user.id}'
        cached_secret = cache.get(cache_key)
        
        if not cached_secret:
            raise ValueError("Setup session expired. Please start 2FA setup again.")
        
        if cached_secret != secret:
            raise ValueError("Invalid setup session. Please start 2FA setup again.")
        
        # Verify the code
        totp = pyotp.TOTP(secret)
        if not totp.verify(verification_code, valid_window=1):
            raise ValueError("Invalid verification code. Please check your authenticator app and try again.")
        
        # Code is valid - enable 2FA
        user.otp_secret = secret
        user.two_factor_enabled = True
        user.save(update_fields=['otp_secret', 'two_factor_enabled'])
        
        # Clear temporary secret
        cache.delete(cache_key)
        
        return {
            'success': True,
            'message': 'Two-factor authentication has been successfully enabled.',
            'backup_codes': cls._generate_backup_codes()
        }
    
    @classmethod
    def disable(cls, user) -> Dict[str, Any]:
        """
        Disable 2FA for the user.
        
        Args:
            user: User instance
            
        Returns:
            dict: Success result
        """
        user.two_factor_enabled = False
        user.otp_secret = None
        user.save(update_fields=['two_factor_enabled', 'otp_secret'])
        
        # Clear any temporary secrets
        cache_key = f'{cls.TEMP_SECRET_CACHE_PREFIX}:{user.id}'
        cache.delete(cache_key)
        
        return {
            'success': True,
            'message': 'Two-factor authentication has been disabled.'
        }
    
    @classmethod
    def get_setup_status(cls, user) -> Dict[str, Any]:
        """
        Get current 2FA setup status for the user.
        
        Returns:
            dict: Current status information
        """
        cache_key = f'{cls.TEMP_SECRET_CACHE_PREFIX}:{user.id}'
        has_pending_setup = cache.get(cache_key) is not None
        
        # Get TTL safely - not all cache backends support ttl()
        setup_expires_in = None
        if has_pending_setup:
            try:
                setup_expires_in = cache.ttl(cache_key)
            except (AttributeError, TypeError):
                # Fallback: assume default timeout if ttl() not supported
                setup_expires_in = cls.TEMP_SECRET_TIMEOUT
        
        return {
            'enabled': user.two_factor_enabled,
            'has_pending_setup': has_pending_setup,
            'setup_expires_in': setup_expires_in
        }
    
    @classmethod
    def _generate_backup_codes(cls) -> list:
        """
        Generate backup codes for 2FA recovery.
        
        Returns:
            list: List of backup codes
        """
        import secrets
        import string
        
        codes = []
        for _ in range(8):
            # Generate 8-character alphanumeric codes
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            codes.append(f"{code[:4]}-{code[4:]}")  # Format: ABCD-1234
        
        return codes


def verify_2fa_code(user, code: str) -> bool:
    """
    Verify a 2FA code for login.
    
    Args:
        user: User instance with 2FA enabled
        code: 6-digit code from authenticator app
        
    Returns:
        bool: True if code is valid
    """
    if not user.two_factor_enabled or not user.otp_secret:
        return False
    
    totp = pyotp.TOTP(user.otp_secret)
    return totp.verify(code, valid_window=1)


def is_2fa_required(user) -> bool:
    """
    Check if 2FA is required for this user.
    
    Args:
        user: User instance
        
    Returns:
        bool: True if 2FA is enabled and required
    """
    return user.two_factor_enabled and bool(user.otp_secret) 