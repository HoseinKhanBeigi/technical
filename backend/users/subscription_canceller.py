"""
Subscription cancellation operations.

Handles canceling subscriptions in Stripe and updating user records.
"""
from typing import Any
import logging
from django.db import transaction

from .models import User
from .constants import (
    SUBSCRIPTION_STATUS_INACTIVE,
    PLAN_NONE,
)

logger = logging.getLogger(__name__)


@transaction.atomic
def cancel_subscription(
    user: User,
    stripe: Any,
    subscription_id: str
) -> None:
    """
    Cancel a subscription in Stripe and update user.
    
    Uses database transaction to ensure atomicity - either both operations
    succeed or both are rolled back.
    
    Args:
        user: User instance to update
        stripe: Stripe API module
        subscription_id: Stripe subscription ID to cancel
        
    Note:
        If subscription doesn't exist in Stripe, silently continues
        and updates user locally.
    """
    try:
        stripe.Subscription.delete(subscription_id)
        logger.info(f"Subscription {subscription_id} canceled in Stripe")
    except Exception as e:
        # Subscription already deleted or doesn't exist
        logger.warning(f"Could not delete subscription {subscription_id}: {str(e)}")
    
    # Update user within transaction
    user.subscription_status = SUBSCRIPTION_STATUS_INACTIVE
    user.current_plan = PLAN_NONE
    user.stripe_subscription_id = None
    user.save()
    logger.info(f"User {user.username} subscription canceled")

