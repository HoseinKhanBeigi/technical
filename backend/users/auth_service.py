"""
Authentication service for handling JWT token operations.

This service encapsulates all authentication-related business logic,
separating it from view layer concerns.
"""
import logging
from typing import Dict, Optional, Tuple
from django.contrib.auth import authenticate
from django.http import HttpRequest
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from .models import User
from .serializers import UserSerializer

logger = logging.getLogger(__name__)


class AuthService:
    """
    Service for handling authentication operations.
    
    Provides methods for user authentication, JWT token generation,
    token refresh, and token blacklisting.
    """
    
    @staticmethod
    def authenticate_user(
        request: HttpRequest,
        username: str,
        password: str
    ) -> Optional[User]:
        """
        Authenticate a user with username and password.
        
        Args:
            request: HTTP request object
            username: Username to authenticate
            password: Password to authenticate
            
        Returns:
            User instance if authentication succeeds, None otherwise
        """
        if not username or not password:
            logger.warning("Authentication attempt with missing credentials")
            return None
        
        user = authenticate(request, username=username, password=password)
        
        if user is None:
            logger.warning(f"Failed authentication attempt for username: {username}")
        else:
            logger.info(f"User {user.username} authenticated successfully")
        
        return user
    
    @staticmethod
    def generate_jwt_tokens(user: User) -> Dict[str, str]:
        """
        Generate JWT access and refresh tokens for a user.
        
        Args:
            user: User instance to generate tokens for
            
        Returns:
            Dictionary containing 'access' and 'refresh' token strings
            
        Raises:
            ValueError: If user is None or invalid
        """
        if user is None:
            raise ValueError("Cannot generate tokens for None user")
        
        try:
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            logger.debug(f"Generated JWT tokens for user {user.username}")
            
            return {
                'access': str(access_token),
                'refresh': str(refresh),
            }
        except Exception as e:
            logger.error(f"Error generating JWT tokens for user {user.username}: {e}")
            raise
    
    @staticmethod
    def refresh_access_token(refresh_token_string: str) -> str:
        """
        Generate a new access token from a refresh token.
        
        Args:
            refresh_token_string: Refresh token string
            
        Returns:
            New access token string
            
        Raises:
            TokenError: If refresh token is invalid or expired
        """
        if not refresh_token_string:
            raise ValueError("Refresh token is required")
        
        try:
            refresh_token = RefreshToken(refresh_token_string)
            access_token = refresh_token.access_token
            
            logger.debug("Successfully refreshed access token")
            return str(access_token)
        except TokenError as e:
            logger.warning(f"Token refresh failed: {e}")
            raise InvalidToken("Invalid or expired refresh token")
        except Exception as e:
            logger.error(f"Unexpected error refreshing token: {e}")
            raise InvalidToken("Error refreshing token")
    
    @staticmethod
    def blacklist_refresh_token(refresh_token_string: str) -> None:
        """
        Blacklist a refresh token to invalidate it.
        
        Args:
            refresh_token_string: Refresh token string to blacklist
            
        Raises:
            TokenError: If token is invalid
        """
        if not refresh_token_string:
            logger.warning("Attempted to blacklist empty token")
            return
        
        try:
            refresh_token = RefreshToken(refresh_token_string)
            refresh_token.blacklist()
            logger.info("Refresh token blacklisted successfully")
        except TokenError as e:
            logger.warning(f"Error blacklisting token: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error blacklisting token: {e}")
            raise TokenError("Error blacklisting token")
    
    @staticmethod
    def login_user(
        request: HttpRequest,
        username: str,
        password: str
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Complete login flow: authenticate user and generate tokens.
        
        Args:
            request: HTTP request object
            username: Username to authenticate
            password: Password to authenticate
            
        Returns:
            Tuple of (response_data, error_message)
            - response_data: Dict with 'access', 'refresh', and 'user' keys if successful
            - error_message: Error message string if authentication fails, None otherwise
        """
        user = AuthService.authenticate_user(request, username, password)
        
        if user is None:
            return None, 'Invalid credentials'
        
        try:
            tokens = AuthService.generate_jwt_tokens(user)
            user_data = UserSerializer(user).data
            
            logger.info(f"User {user.username} logged in successfully with JWT")
            
            return {
                'access': tokens['access'],
                'refresh': tokens['refresh'],
                'user': user_data,
            }, None
        except Exception as e:
            logger.error(f"Error during login for user {username}: {e}")
            return None, 'Error generating authentication tokens'
    
    @staticmethod
    def logout_user(refresh_token_string: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        Logout a user by blacklisting their refresh token.
        
        Args:
            refresh_token_string: Optional refresh token to blacklist
            
        Returns:
            Tuple of (success, error_message)
            - success: True if logout successful, False otherwise
            - error_message: Error message if logout fails, None otherwise
        """
        if not refresh_token_string:
            # Allow logout even without token (user might already be logged out)
            logger.debug("Logout called without refresh token")
            return True, None
        
        try:
            AuthService.blacklist_refresh_token(refresh_token_string)
            return True, None
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            return False, 'Error logging out'

