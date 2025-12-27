# Testing Guide

## Testing Webhooks Locally

### Option 1: Using Django Management Command

Test webhook handlers without actual Stripe events:

```bash
# Test subscription created
docker-compose exec backend python manage.py test_webhook subscription.created

# Test subscription updated
docker-compose exec backend python manage.py test_webhook subscription.updated

# Test invoice paid (increments lifetime value)
docker-compose exec backend python manage.py test_webhook invoice.paid

# Test subscription deleted
docker-compose exec backend python manage.py test_webhook subscription.deleted
```

### Option 2: Using Stripe CLI

1. Install Stripe CLI (if not already installed)
2. Forward webhooks to your local server:

```bash
stripe listen --forward-to localhost:8000/api/webhooks/stripe/
```

3. Trigger test events from Stripe Dashboard or CLI:

```bash
# Trigger a test subscription.created event
stripe trigger customer.subscription.created

# Trigger a test invoice.paid event
stripe trigger invoice.paid
```

## Testing Subscription Flow

1. **Create/Login User**
   - Login at http://localhost:3000/login
   - Or create via Django admin

2. **Upgrade Subscription**
   - Go to dashboard
   - Click "Upgrade to Basic" or "Upgrade to Pro"
   - Check that subscription is created in Stripe Dashboard

3. **Test Webhook Updates**
   - Use the management command or Stripe CLI to trigger webhook events
   - Verify that:
     - Subscription status updates to 'active'
     - Lifetime value increments when invoice.paid is triggered
     - Plan changes are reflected

4. **Test Protected Route**
   - With active subscription: Access http://localhost:3000/premium (should work)
   - Without active subscription: Should redirect to dashboard

5. **Test Downgrade/Cancel**
   - Click "Cancel Subscription" or change plan
   - Verify subscription is updated/cancelled in Stripe
   - Verify status updates in dashboard

## Expected Behavior

- **Subscription Created**: Status should be 'inactive' initially, becomes 'active' when payment confirmed
- **Invoice Paid**: `total_amount_paid` should increment (in cents)
- **Subscription Updated**: Plan and status should sync from Stripe
- **Subscription Deleted**: Status should be 'inactive', plan should be 'none'

## Troubleshooting

- **Webhook not working**: Check `STRIPE_WEBHOOK_SECRET` in `.env`
- **Subscription not activating**: Trigger `invoice.paid` webhook or use test command
- **Lifetime value not updating**: Ensure `invoice.paid` webhook is triggered

