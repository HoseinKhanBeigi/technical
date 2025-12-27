"""
Subscription validation and retrieval operations.

Handles retrieving subscriptions from Stripe and validating subscription IDs.
"""
from typing import Optional, Any
import logging
from django.db import transaction

from ..models import User

logger = logging.getLogger(__name__)


@transaction.atomic
def get_or_validate_subscription(
    user: User,
    stripe: Any
) -> Optional[Any]:
    """
    Get subscription from Stripe or handle invalid subscription ID.
    
    Uses transaction when clearing invalid subscription ID to ensure consistency.
    
    Args:
        user: User instance
        stripe: Stripe API module
        
    Returns:
        Optional[stripe.Subscription]: Subscription object if found, None otherwise
        
    Note:
        If subscription doesn't exist, clears the invalid ID from user within transaction.
    """
    if not user.stripe_subscription_id:
        return None
    
    try:
        subscription = stripe.Subscription.retrieve(user.stripe_subscription_id)
        return subscription
    except stripe.error.InvalidRequestError:
        # Subscription doesn't exist in Stripe (might be test data)
        # Clear within transaction
        logger.warning(
            f"Subscription {user.stripe_subscription_id} not found in Stripe, "
            f"clearing from user {user.username}"
        )
        user.stripe_subscription_id = None
        user.save()
        return None
    except Exception as e:
        logger.error(f"Failed to retrieve subscription: {str(e)}")
        raise Exception(f'Failed to retrieve subscription: {str(e)}')

