from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .health_views import health_check, health_check_detailed

urlpatterns = [
    path('csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user/status/', views.user_status, name='user_status'),
    path('user/subscription/', views.update_subscription, name='update_subscription'),
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
    # Health check endpoints
    path('health/', health_check, name='health_check'),
    path('health/detailed/', health_check_detailed, name='health_check_detailed'),
]

