"""
JWT authentication views.

Provides JWT token-based authentication endpoints for API access.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from .serializers import UserSerializer
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
    
    user = authenticate(request, username=username, password=password)
    
    if user is None:
        logger.warning(f"Failed login attempt for username: {username}")
        return Response(
            {'detail': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token
    
    logger.info(f"User {user.username} logged in successfully with JWT")
    
    # Return tokens and user data
    return Response({
        'access': str(access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data,
    })


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
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the token
            logger.info(f"User {request.user.username} logged out (JWT token blacklisted)")
        return Response(
            {'detail': 'Successfully logged out'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Error during JWT logout: {e}")
        return Response(
            {'detail': 'Error logging out'},
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
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'detail': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token = RefreshToken(refresh_token)
        access_token = token.access_token
        
        return Response({
            'access': str(access_token),
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
    return Response({
        'valid': True,
        'user': UserSerializer(request.user).data,
    })

