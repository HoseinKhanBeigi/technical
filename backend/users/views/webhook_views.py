"""
Stripe webhook endpoint view.
"""
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.conf import settings
from ..utils.stripe_utils import get_stripe
from ..webhooks.webhook_handlers import (
    handle_subscription_created,
    handle_subscription_updated,
    handle_subscription_deleted,
    handle_invoice_paid,
    handle_invoice_payment_failed,
)


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """Handle Stripe webhook events."""
    # Get Stripe with API key configured
    stripe = get_stripe()
    if not stripe.api_key:
        return JsonResponse({'error': 'Stripe not configured'}, status=500)
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    
    if not webhook_secret:
        return JsonResponse({'error': 'Webhook secret not configured'}, status=500)
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Handle the event
    event_type = event['type']
    data = event['data']['object']
    
    if event_type == 'customer.subscription.created':
        handle_subscription_created(data)
    elif event_type == 'customer.subscription.updated':
        handle_subscription_updated(data)
    elif event_type == 'customer.subscription.deleted':
        handle_subscription_deleted(data)
    elif event_type == 'invoice.paid':
        handle_invoice_paid(data)
    elif event_type == 'invoice.payment_failed':
        handle_invoice_payment_failed(data)
    
    return JsonResponse({'status': 'success'})

