"""
Constants used across the users app.
"""
from typing import Final

# Subscription statuses
SUBSCRIPTION_STATUS_ACTIVE: Final[str] = 'active'
SUBSCRIPTION_STATUS_INACTIVE: Final[str] = 'inactive'

# Plan types
PLAN_BASIC: Final[str] = 'basic'
PLAN_PRO: Final[str] = 'pro'
PLAN_NONE: Final[str] = 'none'

# Stripe subscription statuses that are considered active
ACTIVE_STRIPE_STATUSES: Final[tuple] = ('active', 'trialing')

# Amount conversion
CENTS_PER_DOLLAR: Final[int] = 100

