"""
User model with subscription tracking capabilities.

This module defines the custom User model with subscription management features.
All monetary values are stored in cents (integers) to avoid floating-point precision issues.

The model is split into multiple modules for better organization:
- models.py: Core model definition with fields
- user_validators.py: Validation logic
- user_helpers.py: Helper methods and properties
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from typing import Optional
from .constants import (
    SUBSCRIPTION_STATUS_ACTIVE,
    SUBSCRIPTION_STATUS_INACTIVE,
    PLAN_BASIC,
    PLAN_PRO,
    PLAN_NONE,
    CENTS_PER_DOLLAR,
)
from .user_validators import validate_user_model
from .user_helpers import (
    get_lifetime_value_dollars,
    is_subscription_active,
    has_plan,
    increment_lifetime_value,
)


class User(AbstractUser):
    """
    Custom User model with subscription tracking.
    
    Tracks subscription status, current plan, and lifetime value.
    All monetary amounts are stored in cents (integers) to avoid floating-point precision issues.
    """
    
    SUBSCRIPTION_STATUS_CHOICES = [
        (SUBSCRIPTION_STATUS_ACTIVE, 'Active'),
        (SUBSCRIPTION_STATUS_INACTIVE, 'Inactive'),
    ]
    
    PLAN_CHOICES = [
        (PLAN_BASIC, 'Basic Plan'),
        (PLAN_PRO, 'Pro Plan'),
        (PLAN_NONE, 'None'),
    ]
    
    subscription_status = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_STATUS_CHOICES,
        default=SUBSCRIPTION_STATUS_INACTIVE,
        help_text="Current subscription status",
        db_index=True,  # Index for faster queries
    )
    
    current_plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default=PLAN_NONE,
        help_text="Current subscription plan",
        db_index=True,
    )
    
    total_amount_paid = models.IntegerField(
        default=0,
        help_text="Total amount paid in cents (integer, not floating point)",
        db_index=True,
        validators=[MinValueValidator(0)],  # Prevent negative values
    )
    
    stripe_customer_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,  # Each Stripe customer should map to one user
        help_text="Stripe customer ID (starts with 'cus_')",
        db_index=True,
    )
    
    stripe_subscription_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Stripe subscription ID (starts with 'sub_')",
        db_index=True,
    )
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['stripe_customer_id']),
            models.Index(fields=['subscription_status', 'current_plan']),
            models.Index(fields=['email']),  # For email lookups
        ]
        constraints = [
            # Ensure total_amount_paid is never negative
            models.CheckConstraint(
                check=models.Q(total_amount_paid__gte=0),
                name='users_user_total_amount_paid_non_negative'
            ),
        ]
        ordering = ['-date_joined']  # Newest users first by default
    
    def __str__(self) -> str:
        """String representation of the user."""
        return f"{self.username} - {self.current_plan} ({self.subscription_status})"
    
    def clean(self) -> None:
        """
        Validate model fields before saving.
        
        Delegates to user_validators module for validation logic.
        
        Raises:
            ValidationError: If validation fails
        """
        super().clean()
        validate_user_model(self)
    
    def save(self, *args, **kwargs) -> None:
        """
        Override save to run validation.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments (can include 'skip_validation=True' to skip)
        """
        # Allow skipping validation for bulk operations or migrations
        if not kwargs.pop('skip_validation', False):
            self.full_clean()  # Run model validation
        super().save(*args, **kwargs)
    
    @property
    def lifetime_value_dollars(self) -> float:
        """
        Get lifetime value in dollars (property for easy access).
        
        Returns:
            float: Lifetime value in dollars (e.g., 2000 cents = 20.00 dollars)
        """
        return get_lifetime_value_dollars(self)
    
    def get_lifetime_value_dollars(self) -> float:
        """
        Convert total_amount_paid from cents to dollars.
        
        Returns:
            float: Lifetime value in dollars (e.g., 2000 cents = 20.00 dollars)
        """
        return get_lifetime_value_dollars(self)
    
    def is_subscription_active(self) -> bool:
        """
        Check if user has an active subscription.
        
        Returns:
            bool: True if subscription is active, False otherwise
        """
        return is_subscription_active(self)
    
    def has_plan(self, plan_name: Optional[str] = None) -> bool:
        """
        Check if user has a plan.
        
        Args:
            plan_name: Optional specific plan to check ('basic', 'pro', or None for any plan)
            
        Returns:
            bool: True if user has the specified plan (or any plan if plan_name is None)
        """
        return has_plan(self, plan_name)
    
    def increment_lifetime_value(self, amount_cents: int) -> None:
        """
        Increment the total amount paid (in cents).
        
        This method should be used instead of direct assignment to ensure
        proper validation and logging.
        
        Args:
            amount_cents: Amount to add in cents (must be >= 0)
            
        Raises:
            ValueError: If amount_cents is negative
        """
        increment_lifetime_value(self, amount_cents)

