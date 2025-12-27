"""
Subscription creation operations.

Handles creating new Stripe subscriptions and ensuring users have customer IDs.
"""
from typing import Any, Literal
import logging
from django.db import transaction

from .models import User
from .stripe_utils import get_plan_price_ids
from .constants import (
    SUBSCRIPTION_STATUS_ACTIVE,
    SUBSCRIPTION_STATUS_INACTIVE,
    ACTIVE_STRIPE_STATUSES,
)

logger = logging.getLogger(__name__)


@transaction.atomic
def create_subscription(
    user: User,
    stripe: Any,
    target_plan: Literal['basic', 'pro']
) -> Any:
    """
    Create a new subscription for a user.
    
    Uses database transaction to ensure atomicity. If Stripe call succeeds
    but database save fails, the transaction will rollback.
    
    Args:
        user: User instance to create subscription for
        stripe: Stripe API module
        target_plan: Plan to subscribe to ('basic' or 'pro')
        
    Returns:
        stripe.Subscription: Created Stripe subscription object
        
    Raises:
        ValueError: If price ID is not configured
        Exception: If Stripe API call fails (transaction will rollback)
    """
    # Ensure user has a Stripe customer ID (within transaction)
    if not user.stripe_customer_id:
        try:
            customer = stripe.Customer.create(
                email=user.email,
                metadata={'user_id': user.id}
            )
            user.stripe_customer_id = customer.id
            user.save()
            logger.info(f"Created Stripe customer {customer.id} for user {user.username}")
        except Exception as e:
            logger.error(f"Failed to create Stripe customer: {str(e)}")
            raise  # Transaction will rollback
    
    plan_price_ids = get_plan_price_ids()
    price_id = plan_price_ids.get(target_plan)
    
    if not price_id:
        raise ValueError(f'Price ID not configured for plan: {target_plan}')
    
    # Create subscription in Stripe
    try:
        subscription = stripe.Subscription.create(
            customer=user.stripe_customer_id,
            items=[{'price': price_id}],
            payment_behavior='default_incomplete',
            payment_settings={'save_default_payment_method': 'on_subscription'},
            expand=['latest_invoice.payment_intent'],
        )
        logger.info(f"Created subscription {subscription.id} for user {user.username}")
    except Exception as e:
        logger.error(f"Failed to create subscription: {str(e)}")
        raise  # Transaction will rollback
    
    # Update user within same transaction
    user.stripe_subscription_id = subscription.id
    user.current_plan = target_plan
    
    # Check if subscription is immediately active
    if subscription.status in ACTIVE_STRIPE_STATUSES:
        user.subscription_status = SUBSCRIPTION_STATUS_ACTIVE
    else:
        # Will be activated by webhook when payment is confirmed
        user.subscription_status = SUBSCRIPTION_STATUS_INACTIVE
    
    user.save()
    return subscription

