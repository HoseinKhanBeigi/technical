"""
Health check endpoints for monitoring and deployment.

Provides endpoints to check system health, database connectivity,
and Stripe configuration status.
"""
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
def health_check(request):
    """
    Basic health check endpoint.
    
    Returns:
        JsonResponse: Status 200 if healthy, 503 if unhealthy
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'billing_portal',
    })


@csrf_exempt
def health_check_detailed(request):
    """
    Detailed health check with database and Stripe connectivity.
    
    Returns:
        JsonResponse: Detailed health status with component checks
    """
    health_status = {
        'status': 'healthy',
        'service': 'billing_portal',
        'components': {},
    }
    
    overall_healthy = True
    
    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['components']['database'] = {
            'status': 'healthy',
            'message': 'Database connection successful',
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status['components']['database'] = {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}',
        }
        overall_healthy = False
    
    # Check Stripe configuration
    stripe_configured = bool(settings.STRIPE_SECRET_KEY)
    health_status['components']['stripe'] = {
        'status': 'healthy' if stripe_configured else 'degraded',
        'message': 'Stripe configured' if stripe_configured else 'Stripe not configured',
        'configured': stripe_configured,
    }
    
    if not overall_healthy:
        health_status['status'] = 'unhealthy'
    
    status_code = 200 if overall_healthy else 503
    return JsonResponse(health_status, status=status_code)

