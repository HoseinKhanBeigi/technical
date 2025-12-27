"""
JWT authentication views.

Provides JWT token-based authentication endpoints for API access.
Business logic is delegated to AuthService.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from .auth_service import AuthService
from .user_service import UserService
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def jwt_login(request):
    """
    JWT login endpoint.
    
    Authenticates user and returns JWT access and refresh tokens.
    
    Request Body:
        {
            "username": "string",
            "password": "string"
        }
    
    Response:
        {
            "access": "jwt_access_token",
            "refresh": "jwt_refresh_token",
            "user": { ... user data ... }
        }
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'detail': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Use AuthService for login logic
    response_data, error_message = AuthService.login_user(request, username, password)
    
    if error_message:
        return Response(
            {'detail': error_message},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    return Response(response_data)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def jwt_logout(request):
    """
    JWT logout endpoint.
    
    Blacklists the refresh token to invalidate the session.
    
    Request Body:
        {
            "refresh": "refresh_token_string"
        }
    """
    refresh_token = request.data.get('refresh')
    
    # Use AuthService for logout logic
    success, error_message = AuthService.logout_user(refresh_token)
    
    if success:
        logger.info(f"User {request.user.username} logged out (JWT token blacklisted)")
        return Response(
            {'detail': 'Successfully logged out'},
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {'detail': error_message or 'Error logging out'},
            status=status.HTTP_400_BAD_REQUEST
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def jwt_refresh(request):
    """
    JWT token refresh endpoint.
    
    Generates a new access token from a valid refresh token.
    
    Request Body:
        {
            "refresh": "refresh_token_string"
        }
    
    Response:
        {
            "access": "new_jwt_access_token"
        }
    """
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response(
            {'detail': 'Refresh token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Use AuthService for token refresh logic
        access_token = AuthService.refresh_access_token(refresh_token)
        return Response({
            'access': access_token,
        })
    except Exception as e:
        logger.error(f"Error refreshing JWT token: {e}")
        return Response(
            {'detail': 'Invalid or expired refresh token'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def jwt_verify(request):
    """
    JWT token verification endpoint.
    
    Verifies that the current access token is valid.
    
    Response:
        {
            "valid": true,
            "user": { ... user data ... }
        }
    """
    # Use UserService for user serialization
    user_data = UserService.get_user_status(request.user)
    
    return Response({
        'valid': True,
        'user': user_data,
    })

