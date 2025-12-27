"""
User model validation logic.

Contains validation methods for the User model to ensure data integrity.
"""
from django.core.exceptions import ValidationError
from .constants import (
    SUBSCRIPTION_STATUS_ACTIVE,
    PLAN_NONE,
)


def validate_user_model(user) -> None:
    """
    Validate User model fields before saving.
    
    Args:
        user: User model instance to validate
        
    Raises:
        ValidationError: If validation fails
    """
    # Validate Stripe customer ID format (if provided)
    if user.stripe_customer_id and not user.stripe_customer_id.startswith('cus_'):
        raise ValidationError({
            'stripe_customer_id': 'Stripe customer ID must start with "cus_"'
        })
    
    # Validate Stripe subscription ID format (if provided)
    if user.stripe_subscription_id and not user.stripe_subscription_id.startswith('sub_'):
        raise ValidationError({
            'stripe_subscription_id': 'Stripe subscription ID must start with "sub_"'
        })
    
    # Validate subscription status consistency
    if user.subscription_status == SUBSCRIPTION_STATUS_ACTIVE and user.current_plan == PLAN_NONE:
        raise ValidationError({
            'subscription_status': 'Active subscription must have a plan (not "none")'
        })

