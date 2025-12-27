from django.urls import path
from .health_views import health_check, health_check_detailed
from .jwt_views import jwt_login, jwt_logout, jwt_refresh, jwt_verify
from .subscription_views import user_status, update_subscription
from .webhook_views import stripe_webhook

urlpatterns = [
    # JWT authentication endpoints
    path('auth/jwt/login/', jwt_login, name='jwt_login'),
    path('auth/jwt/logout/', jwt_logout, name='jwt_logout'),
    path('auth/jwt/refresh/', jwt_refresh, name='jwt_refresh'),
    path('auth/jwt/verify/', jwt_verify, name='jwt_verify'),
    
    # User endpoints
    path('user/status/', user_status, name='user_status'),
    path('user/subscription/', update_subscription, name='update_subscription'),
    
    # Webhooks
    path('webhooks/stripe/', stripe_webhook, name='stripe_webhook'),
    
    # Health check endpoints
    path('health/', health_check, name='health_check'),
    path('health/detailed/', health_check_detailed, name='health_check_detailed'),
]

