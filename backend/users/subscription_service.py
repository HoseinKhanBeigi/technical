"""
Subscription service layer - main orchestrator for subscription operations.

This module follows the Service Layer pattern, orchestrating subscription
operations by delegating to specialized modules:
- subscription_creator.py: Creating new subscriptions
- subscription_updater.py: Updating existing subscriptions
- subscription_canceller.py: Canceling subscriptions
- subscription_validator.py: Validating and retrieving subscriptions
"""
from typing import Literal
import logging
from django.db import transaction

from .models import User
from .stripe_utils import get_stripe
from .constants import (
    PLAN_NONE,
    SUBSCRIPTION_STATUS_INACTIVE,
)
from .subscription_creator import create_subscription
from .subscription_updater import update_subscription_plan
from .subscription_canceller import cancel_subscription
from .subscription_validator import get_or_validate_subscription

logger = logging.getLogger(__name__)


class SubscriptionService:
    """
    Service class for managing subscriptions.
    
    Acts as the main orchestrator, delegating to specialized modules:
    - Creating subscriptions
    - Updating subscription plans
    - Canceling subscriptions
    - Validating subscription state
    """
    
    @staticmethod
    @transaction.atomic
    def handle_subscription_update(
        user: User,
        target_plan: Literal['basic', 'pro', 'none']
    ) -> None:
        """
        Main method to handle subscription updates (upgrade/downgrade/cancel).
        
        Wraps the entire operation in a database transaction to ensure atomicity.
        If any step fails, all changes are rolled back.
        
        Args:
            user: User instance to update
            target_plan: Target plan ('basic', 'pro', or 'none' for cancel)
            
        Raises:
            ValueError: If Stripe is not configured or plan is invalid
            Exception: If subscription operation fails (transaction will rollback)
        """
        stripe = get_stripe()
        
        if not stripe.api_key:
            raise ValueError('Failed to initialize Stripe API key.')
        
        # Handle cancellation (within transaction)
        if target_plan == PLAN_NONE:
            if user.stripe_subscription_id:
                subscription = get_or_validate_subscription(user, stripe)
                if subscription:
                    # Cancel in Stripe and update DB (both in transaction)
                    cancel_subscription(user, stripe, user.stripe_subscription_id)
                else:
                    # Invalid subscription ID, just update locally (in transaction)
                    user.subscription_status = SUBSCRIPTION_STATUS_INACTIVE
                    user.current_plan = PLAN_NONE
                    user.save()
            else:
                # No subscription to cancel (in transaction)
                user.subscription_status = SUBSCRIPTION_STATUS_INACTIVE
                user.current_plan = PLAN_NONE
                user.save()
            return
        
        # Handle upgrade/downgrade or new subscription (within transaction)
        subscription = get_or_validate_subscription(user, stripe)
        
        if subscription:
            # Update existing subscription (transaction handled in method)
            update_subscription_plan(user, stripe, subscription, target_plan)
        else:
            # Create new subscription (transaction handled in method)
            create_subscription(user, stripe, target_plan)

