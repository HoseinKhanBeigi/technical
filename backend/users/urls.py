from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .health_views import health_check, health_check_detailed
from .jwt_views import jwt_login, jwt_logout, jwt_refresh, jwt_verify

urlpatterns = [
    # Session-based auth (legacy, can be removed if using JWT only)
    path('csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # JWT authentication endpoints
    path('auth/jwt/login/', jwt_login, name='jwt_login'),
    path('auth/jwt/logout/', jwt_logout, name='jwt_logout'),
    path('auth/jwt/refresh/', jwt_refresh, name='jwt_refresh'),
    path('auth/jwt/verify/', jwt_verify, name='jwt_verify'),
    
    # User endpoints
    path('user/status/', views.user_status, name='user_status'),
    path('user/subscription/', views.update_subscription, name='update_subscription'),
    
    # Webhooks
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
    
    # Health check endpoints
    path('health/', health_check, name='health_check'),
    path('health/detailed/', health_check_detailed, name='health_check_detailed'),
]

