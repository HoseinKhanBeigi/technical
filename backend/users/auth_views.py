"""
Authentication views for user login/logout.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from .serializers import UserSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def get_csrf_token(request):
    """Get CSRF token for frontend."""
    return Response({'csrfToken': get_token(request)})


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Handle user login."""
    # Get data from request - try both data and POST
    username = request.data.get('username') or request.POST.get('username')
    password = request.data.get('password') or request.POST.get('password')
    
    if not username or not password:
        return Response(
            {'detail': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    else:
        return Response(
            {'detail': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


def _logout_view(request):
    """Handle user logout."""
    logout(request)
    return Response({'detail': 'Successfully logged out'})


logout_view = csrf_exempt(api_view(['POST'])(permission_classes([IsAuthenticated])(_logout_view)))

