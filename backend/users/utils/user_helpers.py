"""
User model helper methods and properties.

Contains business logic methods for the User model.
"""
from typing import Optional
from .constants import (
    PLAN_NONE,
    SUBSCRIPTION_STATUS_ACTIVE,
    CENTS_PER_DOLLAR,
)


def get_lifetime_value_dollars(user) -> float:
    """
    Convert total_amount_paid from cents to dollars.
    
    Args:
        user: User model instance
        
    Returns:
        float: Lifetime value in dollars (e.g., 2000 cents = 20.00 dollars)
    """
    return user.total_amount_paid / CENTS_PER_DOLLAR


def is_subscription_active(user) -> bool:
    """
    Check if user has an active subscription.
    
    Args:
        user: User model instance
        
    Returns:
        bool: True if subscription is active, False otherwise
    """
    return user.subscription_status == SUBSCRIPTION_STATUS_ACTIVE


def has_plan(user, plan_name: Optional[str] = None) -> bool:
    """
    Check if user has a plan.
    
    Args:
        user: User model instance
        plan_name: Optional specific plan to check ('basic', 'pro', or None for any plan)
        
    Returns:
        bool: True if user has the specified plan (or any plan if plan_name is None)
    """
    if plan_name is None:
        return user.current_plan != PLAN_NONE
    return user.current_plan == plan_name


def increment_lifetime_value(user, amount_cents: int) -> None:
    """
    Increment the total amount paid (in cents).
    
    This method should be used instead of direct assignment to ensure
    proper validation and logging.
    
    Args:
        user: User model instance
        amount_cents: Amount to add in cents (must be >= 0)
        
    Raises:
        ValueError: If amount_cents is negative
    """
    if amount_cents < 0:
        raise ValueError("Amount must be non-negative")
    user.total_amount_paid += amount_cents
    user.save(update_fields=['total_amount_paid'])

