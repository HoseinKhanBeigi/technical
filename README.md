# Full Stack Subscription System

A robust SaaS billing portal built with Django + PostgreSQL backend and Next.js 14+ frontend, integrated with Stripe for subscription management.

## Features

- **User Subscription Management**: Track subscription status, current plan, and lifetime value
- **Stripe Integration**: Full integration with Stripe Test Mode for subscription handling
- **Real-time Updates**: Webhook-based synchronization of subscription status
- **Protected Routes**: Middleware-protected premium content route
- **Modern UI**: Beautiful, responsive dashboard with real-time subscription management

## Architecture

- **Backend**: Django 4.2 + Django REST Framework + PostgreSQL
- **Frontend**: Next.js 14+ (App Router) + TypeScript
- **Database**: PostgreSQL 15
- **Payment Processing**: Stripe Test Mode

## Prerequisites

- Docker and Docker Compose
- Stripe account (Test Mode)
- Stripe CLI (for local webhook testing, optional)

## Setup Instructions

### 1. Stripe Configuration

1. Log in to your [Stripe Dashboard](https://dashboard.stripe.com/test/products)
2. Create two products in Test Mode:
   - **Basic Plan**: $10/month (recurring)
   - **Pro Plan**: $20/month (recurring)
3. Copy the **Price IDs** for both plans (they start with `price_`)
4. Get your **Stripe Secret Key** (starts with `sk_test_`)
5. Get your **Stripe Publishable Key** (starts with `pk_test_`)

### 2. Stripe Webhook Setup

For local development, you can use Stripe CLI to forward webhooks:

```bash
stripe listen --forward-to localhost:8000/api/webhooks/stripe/
```

This will give you a webhook signing secret (starts with `whsec_`).

Alternatively, in production, configure the webhook endpoint in Stripe Dashboard:
- Endpoint URL: `https://yourdomain.com/api/webhooks/stripe/`
- Events to listen: `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.paid`, `invoice.payment_failed`

### 3. Environment Variables

Create a `.env` file in the project root:

```env
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True

# Stripe
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
STRIPE_BASIC_PLAN_PRICE_ID=price_your_basic_plan_price_id
STRIPE_PRO_PLAN_PRICE_ID=price_your_pro_plan_price_id
```

### 4. Build and Run

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

The services will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin

### 5. Create a Superuser

```bash
docker-compose exec backend python manage.py createsuperuser
```

This will allow you to:
- Access Django admin at http://localhost:8000/admin
- Create test users
- View subscription data

### 6. Create a Test User

You can create a user through Django admin or via the Django shell:

```bash
docker-compose exec backend python manage.py shell
```

```python
from users.models import User
user = User.objects.create_user('testuser', 'test@example.com', 'password123')
```

### 7. Access the Application

1. Navigate to http://localhost:3000
2. You'll be redirected to the login page
3. Login with the credentials you created
4. You'll be taken to the dashboard where you can:
   - View your current subscription status
   - See your lifetime spend
   - Upgrade/downgrade your subscription
   - Access premium content (if you have an active subscription)

## API Endpoints

### Login
```
POST /api/login/
Body: { "username": "string", "password": "string" }
```
Authenticates a user and creates a session.

### Logout
```
POST /api/logout/
```
Logs out the current user.

### Get User Status
```
GET /api/user/status/
```
Returns current user's subscription status, plan, and lifetime value.

**Response:**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "subscription_status": "active",
  "current_plan": "pro",
  "total_amount_paid": 2000,
  "lifetime_value": 20.0
}
```

### Update Subscription
```
POST /api/user/subscription/
Body: { "plan": "basic" | "pro" | "none" }
```
Upgrades, downgrades, or cancels the user's subscription.

### Stripe Webhook
```
POST /api/webhooks/stripe/
```
Handles Stripe webhook events for subscription lifecycle management.

## Frontend Routes

- **`/login`**: User login page (default route)
- **`/dashboard`**: Main dashboard showing current plan, lifetime spend, and subscription management
- **`/premium`**: Protected route only accessible with active subscription (enforced by middleware)

## Key Features Implementation

### Backend

1. **User Model**: Custom user model with:
   - `subscription_status`: 'active' or 'inactive'
   - `current_plan`: 'basic', 'pro', or 'none'
   - `total_amount_paid`: Integer in cents (not floating point)
   - Stripe customer and subscription IDs

2. **Webhook Handler**: Processes Stripe events:
   - `customer.subscription.created`: Sets subscription to active
   - `customer.subscription.updated`: Updates plan and status
   - `customer.subscription.deleted`: Marks subscription as inactive
   - `invoice.paid`: Increments `total_amount_paid` (in cents)

3. **Subscription Management**: Handles upgrade/downgrade logic with Stripe API

### Frontend

1. **Dashboard**: Real-time display of:
   - Current plan with visual badges
   - Subscription status
   - Lifetime spend formatted as currency
   - Upgrade/downgrade buttons

2. **Protected Route**: `/premium` route protected by Next.js middleware that:
   - Checks user authentication
   - Verifies active subscription status
   - Redirects to dashboard if not authorized

3. **Real-time Updates**: UI refreshes after subscription changes

## Testing the System

### Quick Test with Management Command

Test webhook handlers without actual Stripe events:

```bash
# Test invoice paid (increments lifetime value)
docker-compose exec backend python manage.py test_webhook invoice.paid

# Test subscription created
docker-compose exec backend python manage.py test_webhook subscription.created

# Test subscription updated
docker-compose exec backend python manage.py test_webhook subscription.updated

# Test subscription deleted
docker-compose exec backend python manage.py test_webhook subscription.deleted
```

### Full Testing Flow

1. **Create a User**: Use Django admin or shell
2. **Login**: Navigate to http://localhost:3000 and login with your credentials
3. **Upgrade to Basic**: Click "Upgrade to Basic" on dashboard
   - Subscription will be created in Stripe
   - Status will be 'inactive' until payment is confirmed
4. **Test Webhook**: Use the management command above to simulate `invoice.paid` event
   - This will activate the subscription and increment lifetime value
5. **Check Stripe**: Verify subscription created in Stripe Dashboard
6. **Access Premium**: With active subscription, navigate to `/premium` (should be accessible)
7. **Test Without Subscription**: Try accessing `/premium` without an active subscription (should redirect to dashboard)
8. **Cancel Subscription**: Test cancellation flow
9. **Verify Updates**: Check that subscription status and lifetime value update correctly

See `TESTING.md` for more detailed testing instructions.

## Development Notes

- The backend uses Django REST Framework with session authentication
- CORS is configured to allow requests from the frontend
- All amounts are stored in cents (integers) to avoid floating-point precision issues
- Webhook signature verification ensures security
- The frontend uses Next.js App Router with TypeScript

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL container is healthy: `docker-compose ps`
- Check database credentials in environment variables

### Stripe Webhook Not Working
- Verify webhook secret is correct
- Check webhook endpoint is accessible
- Use Stripe CLI for local testing: `stripe listen --forward-to localhost:8000/api/webhooks/stripe/`

### Frontend Can't Connect to Backend
- Check `NEXT_PUBLIC_API_URL` environment variable
- Verify backend is running: `docker-compose logs backend`
- Check CORS settings in Django settings.py

## Production Considerations

- Set `DEBUG=False` in production
- Use strong `DJANGO_SECRET_KEY`
- Configure proper `ALLOWED_HOSTS`
- Use environment variables for all secrets
- Set up proper SSL/TLS
- Configure production database
- Use Stripe production keys
- Set up proper webhook endpoint with HTTPS

## License

This project is for technical assessment purposes.

