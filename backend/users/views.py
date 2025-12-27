"""
Main views module - imports all views from separate modules.
This keeps the codebase organized and maintainable.
"""
from .auth_views import login_view, logout_view, get_csrf_token
from .subscription_views import user_status, update_subscription
from .webhook_views import stripe_webhook

# Export all views for use in urls.py
__all__ = [
    'login_view',
    'logout_view',
    'get_csrf_token',
    'user_status',
    'update_subscription',
    'stripe_webhook',
]
