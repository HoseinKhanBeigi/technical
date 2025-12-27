"""
Subscription management views for upgrading/downgrading plans.

This module handles HTTP requests/responses for subscription operations.
Business logic is delegated to SubscriptionService and UserService.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from django.views.decorators.csrf import csrf_exempt
import logging
from .models import User
from .serializers import SubscriptionUpdateSerializer
from .stripe_utils import validate_stripe_config
from .subscription_service import SubscriptionService
from .user_service import UserService

logger = logging.getLogger(__name__)


def _user_status_view(request: Request) -> Response:
    """
    Get current user's subscription status and stats.
    
    Args:
        request: HTTP request object
        
    Returns:
        Response: User data including subscription status and lifetime value
    """
    # Use UserService for user status retrieval
    user_data = UserService.get_user_status(request.user)
    return Response(user_data)


user_status = csrf_exempt(api_view(['GET'])(permission_classes([IsAuthenticated])(_user_status_view)))


def _update_subscription_view(request: Request) -> Response:
    """
    Handle upgrade/downgrade subscription logic.
    
    Args:
        request: HTTP request with 'plan' in body
        
    Returns:
        Response: Updated user data or error message
    """
    user: User = request.user
    serializer = SubscriptionUpdateSerializer(data=request.data)
    
    if not serializer.is_valid():
        logger.warning(f"Invalid subscription update request from user {user.username}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    target_plan = serializer.validated_data['plan']
    
    # Validate Stripe configuration
    config_errors = validate_stripe_config()
    if config_errors:
        logger.error(f"Stripe configuration errors: {config_errors}")
        return Response(
            {'error': f'Stripe configuration error: {", ".join(config_errors)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    try:
        logger.info(f"User {user.username} updating subscription to {target_plan}")
        # Use service layer to handle subscription update
        SubscriptionService.handle_subscription_update(user, target_plan)
        
        # Refresh user from database using UserService
        UserService.refresh_user_from_db(user)
        user_data = UserService.get_user_status(user)
        logger.info(f"Subscription updated successfully for user {user.username}")
        return Response(user_data)
        
    except ValueError as e:
        logger.warning(f"Validation error for user {user.username}: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        # Handle Stripe errors
        logger.error(f"Error updating subscription for user {user.username}: {str(e)}", exc_info=True)
        error_msg = f'Error: {str(e)}'
        return Response(
            {'error': error_msg},
            status=status.HTTP_400_BAD_REQUEST
        )


update_subscription = csrf_exempt(api_view(['POST'])(permission_classes([IsAuthenticated])(_update_subscription_view)))
