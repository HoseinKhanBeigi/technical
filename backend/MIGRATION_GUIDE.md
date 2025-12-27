# Migration Guide

## Quick Migration Commands

### Standard Workflow

```bash
# 1. Create migrations (after model changes)
docker-compose exec backend python manage.py makemigrations

# 2. Review the generated migration file
# Check: backend/users/migrations/XXXX_*.py

# 3. Apply migrations
docker-compose exec backend python manage.py migrate

# 4. Verify
docker-compose exec backend python manage.py showmigrations
```

### Safe Migration Creation

Use the custom command for safer migrations:

```bash
# Check for issues before creating migrations
docker-compose exec backend python manage.py validate_migrations

# Create migrations with validation
docker-compose exec backend python manage.py makemigrations_safe users

# Dry run (see what would be created)
docker-compose exec backend python manage.py makemigrations_safe users --dry-run
```

## Model Improvements Added

### 1. Field Validators
- `total_amount_paid`: Now has `MinValueValidator(0)` to prevent negative values

### 2. Database Constraints
- Check constraint: `total_amount_paid >= 0` (enforced at database level)

### 3. Model Validation
- `clean()` method validates:
  - Stripe customer ID format (must start with `cus_`)
  - Stripe subscription ID format (must start with `sub_`)
  - Subscription status consistency (active subscriptions must have a plan)

### 4. New Indexes
- Email index for faster email lookups

### 5. New Methods
- `lifetime_value_dollars` property (easier access)
- `increment_lifetime_value()` method (safer way to update lifetime value)
- Enhanced `has_plan()` method (can check for specific plan)

### 6. Default Ordering
- Users ordered by `-date_joined` (newest first)

## Creating Migrations for New Changes

After modifying `models.py`:

```bash
# Option 1: Standard way
docker-compose exec backend python manage.py makemigrations users

# Option 2: Safe way (recommended)
docker-compose exec backend python manage.py makemigrations_safe users

# Option 3: With validation
docker-compose exec backend python manage.py validate_migrations
docker-compose exec backend python manage.py makemigrations users
```

## Migration Best Practices

1. **Always review migration files** before applying
2. **Test migrations** on a copy of production data if possible
3. **Backup database** before running migrations in production
4. **Use transactions** - Django migrations run in transactions by default
5. **Check for data conflicts** - Some migrations may require data migrations

## Common Issues

### Issue: "Your models have changes that are not yet reflected in a migration"

**Solution:**
```bash
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```

### Issue: "Migration conflicts"

**Solution:**
```bash
# Check migration status
docker-compose exec backend python manage.py showmigrations

# If needed, merge migrations
docker-compose exec backend python manage.py makemigrations --merge
```

### Issue: "Validation errors when saving"

The model now validates:
- Stripe IDs must start with correct prefix
- Active subscriptions must have a plan
- Total amount paid cannot be negative

**Fix:** Ensure data meets these requirements before saving.

## Migration Files Location

```
backend/users/migrations/
├── __init__.py
├── 0001_initial.py          # Initial model
├── 0002_alter_user_*.py     # Index additions
└── 0003_*.py                # New constraints/validators
```

## Rollback Migrations

```bash
# Rollback last migration
docker-compose exec backend python manage.py migrate users 0002

# Rollback all migrations for an app
docker-compose exec backend python manage.py migrate users zero
```

## Data Migrations

For complex data transformations, create data migrations:

```bash
docker-compose exec backend python manage.py makemigrations --empty users
```

Then edit the generated file to add data transformation logic.

