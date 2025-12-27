"""
Webhook event handlers for Stripe events.

All handlers use database transactions to ensure data consistency.
Business logic for user retrieval is delegated to UserService.
"""
from django.conf import settings
from django.db import transaction
from ..models import User
from ..services.user_service import UserService
import logging

logger = logging.getLogger(__name__)


@transaction.atomic
def handle_subscription_created(subscription):
    """
    Handle subscription created event.
    
    Uses database transaction to ensure atomicity of user updates.
    """
    customer_id = subscription.get('customer')
    subscription_id = subscription.get('id')
    
    try:
        # Use UserService with select_for_update for transaction safety
        user = UserService.get_user_by_stripe_customer_id(customer_id, select_for_update=True)
        if not user:
            logger.warning(f"User not found for customer_id: {customer_id}")
            return
        
        user.stripe_subscription_id = subscription_id
        user.subscription_status = 'active'
        
        # Determine plan from price
        if subscription.get('items') and subscription['items'].get('data'):
            price_id = subscription['items']['data'][0]['price']['id']
            if price_id == settings.STRIPE_BASIC_PLAN_PRICE_ID:
                user.current_plan = 'basic'
            elif price_id == settings.STRIPE_PRO_PLAN_PRICE_ID:
                user.current_plan = 'pro'
        
        user.save()
        logger.info(f"Subscription {subscription_id} created for user {user.username}")
    except Exception as e:
        logger.warning(f"User not found for customer_id: {customer_id}")
    except Exception as e:
        logger.error(f"Error handling subscription.created: {str(e)}", exc_info=True)
        raise  # Re-raise to trigger transaction rollback


@transaction.atomic
def handle_subscription_updated(subscription):
    """
    Handle subscription updated event.
    
    Uses database transaction and row-level locking to prevent race conditions.
    """
    customer_id = subscription.get('customer')
    subscription_id = subscription.get('id')
    status = subscription.get('status')
    
    try:
        # Use UserService with select_for_update for transaction safety
        user = UserService.get_user_by_stripe_customer_id(customer_id, select_for_update=True)
        if not user:
            logger.warning(f"User not found for customer_id: {customer_id}")
            return
        
        user.stripe_subscription_id = subscription_id
        
        if status in ['active', 'trialing']:
            user.subscription_status = 'active'
        else:
            user.subscription_status = 'inactive'
        
        # Update plan from price
        if subscription.get('items') and subscription['items'].get('data'):
            price_id = subscription['items']['data'][0]['price']['id']
            if price_id == settings.STRIPE_BASIC_PLAN_PRICE_ID:
                user.current_plan = 'basic'
            elif price_id == settings.STRIPE_PRO_PLAN_PRICE_ID:
                user.current_plan = 'pro'
        
        user.save()
        logger.info(f"Subscription {subscription_id} updated for user {user.username}")
    except Exception as e:
        logger.warning(f"User not found for customer_id: {customer_id}")
    except Exception as e:
        logger.error(f"Error handling subscription.updated: {str(e)}", exc_info=True)
        raise  # Re-raise to trigger transaction rollback


@transaction.atomic
def handle_subscription_deleted(subscription):
    """
    Handle subscription deleted event.
    
    Uses database transaction to ensure atomicity of user updates.
    """
    customer_id = subscription.get('customer')
    
    try:
        # Use UserService with select_for_update for transaction safety
        user = UserService.get_user_by_stripe_customer_id(customer_id, select_for_update=True)
        if not user:
            logger.warning(f"User not found for customer_id: {customer_id}")
            return
        
        user.subscription_status = 'inactive'
        user.current_plan = 'none'
        user.stripe_subscription_id = None
        user.save()
        logger.info(f"Subscription deleted for user {user.username}")
    except Exception as e:
        logger.warning(f"User not found for customer_id: {customer_id}")
    except Exception as e:
        logger.error(f"Error handling subscription.deleted: {str(e)}", exc_info=True)
        raise  # Re-raise to trigger transaction rollback


@transaction.atomic
def handle_invoice_paid(invoice):
    """
    Handle invoice paid event - increment total_amount_paid.
    
    Critical: Uses transaction and row-level locking to prevent race conditions
    when incrementing total_amount_paid. This ensures accurate lifetime value tracking.
    """
    customer_id = invoice.get('customer')
    amount_paid = invoice.get('amount_paid', 0)  # Amount in cents
    
    try:
        # Use UserService with select_for_update for transaction safety
        user = UserService.get_user_by_stripe_customer_id(customer_id, select_for_update=True)
        if not user:
            logger.warning(f"User not found for customer_id: {customer_id}")
            return
        
        # Increment total_amount_paid (stored in cents as integer)
        # This is atomic within the transaction
        user.total_amount_paid += amount_paid
        
        # Ensure subscription is active when invoice is paid
        if user.subscription_status != 'active':
            user.subscription_status = 'active'
        
        user.save()
        logger.info(
            f"Invoice paid: ${amount_paid/100:.2f} for user {user.username}. "
            f"New lifetime value: ${user.get_lifetime_value_dollars():.2f}"
        )
    except Exception as e:
        logger.warning(f"User not found for customer_id: {customer_id}")
    except Exception as e:
        logger.error(f"Error handling invoice.paid: {str(e)}", exc_info=True)
        raise  # Re-raise to trigger transaction rollback


@transaction.atomic
def handle_invoice_payment_failed(invoice):
    """
    Handle invoice payment failed event.
    
    Uses database transaction for consistency, though currently only logs the event.
    """
    customer_id = invoice.get('customer')
    
    try:
        # Use UserService with select_for_update for transaction safety
        user = UserService.get_user_by_stripe_customer_id(customer_id, select_for_update=True)
        if not user:
            logger.warning(f"User not found for customer_id: {customer_id}")
            return
        
        # Optionally mark subscription as inactive on payment failure
        # For now, we'll let Stripe handle the subscription status
        logger.info(f"Payment failed for customer: {customer_id}, user: {user.username}")
    except Exception as e:
        logger.warning(f"User not found for customer_id: {customer_id}")
    except Exception as e:
        logger.error(f"Error handling invoice.payment_failed: {str(e)}", exc_info=True)
        raise  # Re-raise to trigger transaction rollback

