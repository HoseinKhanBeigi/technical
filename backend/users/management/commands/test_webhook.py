"""
Management command to test Stripe webhook locally.
Usage: python manage.py test_webhook <event_type>
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from users.webhooks.webhook_handlers import (
    handle_subscription_created,
    handle_subscription_updated,
    handle_subscription_deleted,
    handle_invoice_paid,
    handle_invoice_payment_failed
)
import json


class Command(BaseCommand):
    help = 'Test Stripe webhook handlers with mock data'

    def add_arguments(self, parser):
        parser.add_argument(
            'event_type',
            type=str,
            choices=[
                'subscription.created',
                'subscription.updated',
                'subscription.deleted',
                'invoice.paid',
                'invoice.payment_failed'
            ],
            help='Type of webhook event to test'
        )
        parser.add_argument(
            '--customer-id',
            type=str,
            help='Stripe customer ID (optional, will use first user if not provided)'
        )

    def handle(self, *args, **options):
        from users.models import User
        
        event_type = options['event_type']
        customer_id = options.get('customer_id')
        
        # Get a user for testing
        if customer_id:
            try:
                user = User.objects.get(stripe_customer_id=customer_id)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User with customer_id {customer_id} not found'))
                return
        else:
            user = User.objects.filter(stripe_customer_id__isnull=False).first()
            if not user:
                self.stdout.write(self.style.ERROR('No user with Stripe customer ID found'))
                return
            customer_id = user.stripe_customer_id
        
        self.stdout.write(f'Testing webhook: {event_type} for customer: {customer_id}')
        
        # Create mock event data based on event type
        if event_type == 'subscription.created':
            mock_data = {
                'customer': customer_id,
                'id': 'sub_test_123',
                'status': 'active',
                'items': {
                    'data': [{
                        'price': {
                            'id': settings.STRIPE_BASIC_PLAN_PRICE_ID
                        }
                    }]
                }
            }
            handle_subscription_created(mock_data)
            self.stdout.write(self.style.SUCCESS('✓ Subscription created handler executed'))
            
        elif event_type == 'subscription.updated':
            mock_data = {
                'customer': customer_id,
                'id': user.stripe_subscription_id or 'sub_test_123',
                'status': 'active',
                'items': {
                    'data': [{
                        'price': {
                            'id': settings.STRIPE_PRO_PLAN_PRICE_ID
                        }
                    }]
                }
            }
            handle_subscription_updated(mock_data)
            self.stdout.write(self.style.SUCCESS('✓ Subscription updated handler executed'))
            
        elif event_type == 'subscription.deleted':
            mock_data = {
                'customer': customer_id,
                'id': user.stripe_subscription_id or 'sub_test_123'
            }
            handle_subscription_deleted(mock_data)
            self.stdout.write(self.style.SUCCESS('✓ Subscription deleted handler executed'))
            
        elif event_type == 'invoice.paid':
            mock_data = {
                'customer': customer_id,
                'amount_paid': 1000,  # $10.00 in cents
                'id': 'in_test_123'
            }
            handle_invoice_paid(mock_data)
            self.stdout.write(self.style.SUCCESS('✓ Invoice paid handler executed'))
            
        elif event_type == 'invoice.payment_failed':
            mock_data = {
                'customer': customer_id,
                'id': 'in_test_123'
            }
            handle_invoice_payment_failed(mock_data)
            self.stdout.write(self.style.SUCCESS('✓ Invoice payment failed handler executed'))
        
        # Refresh user to show updated data
        user.refresh_from_db()
        self.stdout.write(f'\nUpdated user data:')
        self.stdout.write(f'  Plan: {user.current_plan}')
        self.stdout.write(f'  Status: {user.subscription_status}')
        self.stdout.write(f'  Lifetime Value: ${user.get_lifetime_value_dollars():.2f}')

