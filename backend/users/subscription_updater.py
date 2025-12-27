"""
Subscription update operations.

Handles updating existing subscriptions to new plans.
"""
from typing import Any, Literal
import logging
from django.db import transaction

from .models import User
from .stripe_utils import get_plan_price_ids

logger = logging.getLogger(__name__)


@transaction.atomic
def update_subscription_plan(
    user: User,
    stripe: Any,
    subscription: Any,
    target_plan: Literal['basic', 'pro']
) -> None:
    """
    Update an existing subscription to a new plan.
    
    Uses database transaction to ensure atomicity between Stripe update
    and database update.
    
    Args:
        user: User instance to update
        stripe: Stripe API module
        subscription: Stripe subscription object
        target_plan: Target plan ('basic' or 'pro')
        
    Raises:
        ValueError: If price ID is not configured for the target plan
        Exception: If Stripe API call fails (transaction will rollback)
    """
    plan_price_ids = get_plan_price_ids()
    price_id = plan_price_ids.get(target_plan)
    
    if not price_id:
        raise ValueError(f'Price ID not configured for plan: {target_plan}')
    
    try:
        # Update subscription in Stripe
        stripe.Subscription.modify(
            subscription.id,
            items=[{
                'id': subscription['items']['data'][0].id,
                'price': price_id,
            }],
            proration_behavior='always_invoice',
        )
        logger.info(f"Subscription {subscription.id} updated to {target_plan} plan")
    except Exception as e:
        logger.error(f"Failed to update subscription: {str(e)}")
        raise  # Transaction will rollback
    
    # Update user within same transaction
    user.current_plan = target_plan
    user.save()

