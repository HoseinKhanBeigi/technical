"""
Startup validation for critical environment variables and configuration.

This module validates that all required environment variables are set
and that critical services are properly configured before the application starts.

The validation runs at startup and will fail fast if critical configuration is missing,
preventing the application from starting in an invalid state.
"""
import os
import sys
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Track if validation has already run to avoid duplicate checks
_validation_run = False


def validate_environment() -> list[str]:
    """
    Validate that all required environment variables are set.
    
    Returns:
        list[str]: List of missing or invalid environment variables
        
    Example:
        >>> errors = validate_environment()
        >>> if errors:
        ...     raise ValueError(f"Configuration errors: {errors}")
    """
    errors: list[str] = []
    warnings: list[str] = []
    
    # Critical: Database configuration
    required_db_vars = {
        'DB_NAME': 'Database name',
        'DB_USER': 'Database user',
        'DB_PASSWORD': 'Database password',
        'DB_HOST': 'Database host',
    }
    for var, description in required_db_vars.items():
        if not validate_required_env_var(var, description):
            errors.append(f'Missing required database variable: {var} ({description})')
    
    # Critical: Django secret key (should not be default in production)
    secret_key = os.getenv('DJANGO_SECRET_KEY', '')
    is_debug = os.getenv('DEBUG', 'True') == 'True'
    
    if not secret_key or secret_key == 'django-insecure-change-in-production':
        if is_debug:
            warnings.append('Using default SECRET_KEY (OK for development, but change for production)')
        else:
            errors.append('SECRET_KEY must be set in production (cannot use default value)')
    
    # Validate Stripe configuration format if provided
    stripe_secret = os.getenv('STRIPE_SECRET_KEY', '')
    if stripe_secret:
        if not validate_env_var_format('STRIPE_SECRET_KEY', 'sk_test_', 'Stripe secret key'):
            warnings.append('STRIPE_SECRET_KEY format may be incorrect (should start with "sk_test_" or "sk_live_")')
    
    stripe_publishable = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
    if stripe_publishable:
        if not validate_env_var_format('STRIPE_PUBLISHABLE_KEY', 'pk_test_', 'Stripe publishable key'):
            warnings.append('STRIPE_PUBLISHABLE_KEY format may be incorrect (should start with "pk_test_" or "pk_live_")')
    
    stripe_webhook = os.getenv('STRIPE_WEBHOOK_SECRET', '')
    if stripe_webhook:
        if not validate_env_var_format('STRIPE_WEBHOOK_SECRET', 'whsec_', 'Stripe webhook secret'):
            warnings.append('STRIPE_WEBHOOK_SECRET format may be incorrect (should start with "whsec_")')
    
    # Important: Stripe configuration (warnings, not errors - app can run without Stripe)
    stripe_vars = {
        'STRIPE_SECRET_KEY': 'Stripe API secret key',
        'STRIPE_PUBLISHABLE_KEY': 'Stripe publishable key',
        'STRIPE_WEBHOOK_SECRET': 'Stripe webhook signing secret',
        'STRIPE_BASIC_PLAN_PRICE_ID': 'Basic plan price ID',
        'STRIPE_PRO_PLAN_PRICE_ID': 'Pro plan price ID',
    }
    
    for var, description in stripe_vars.items():
        if not os.getenv(var):
            warnings.append(f'Missing {var}: {description} (subscription features will not work)')
    
    # Log warnings
    if warnings:
        logger.warning('Configuration warnings:')
        for warning in warnings:
            logger.warning(f'  - {warning}')
    
    # Log errors
    if errors:
        logger.error('Configuration errors:')
        for error in errors:
            logger.error(f'  - {error}')
    
    return errors


def validate_startup(fail_fast: bool = True) -> bool:
    """
    Validate configuration at startup and optionally fail fast if critical issues found.
    
    Args:
        fail_fast: If True, raise exception on critical errors. If False, only log errors.
        
    Returns:
        bool: True if validation passed, False if there were critical errors
        
    Raises:
        SystemExit: If fail_fast=True and critical configuration is missing
    """
    global _validation_run
    
    # Only run validation once per process
    if _validation_run:
        return True
    
    _validation_run = True
    
    errors = validate_environment()
    
    if errors:
        error_msg = (
            '\n' + '=' * 70 + '\n'
            'CRITICAL CONFIGURATION ERRORS FOUND\n'
            '=' * 70 + '\n'
            'The application cannot start due to missing or invalid configuration.\n'
            'Please fix the following errors:\n\n'
            + '\n'.join(f'  ✗ {e}' for e in errors) + '\n\n'
            '=' * 70 + '\n'
        )
        
        logger.error(error_msg)
        
        if fail_fast:
            print(error_msg, file=sys.stderr)
            sys.exit(1)
        
        return False
    
    logger.info('✓ Environment validation passed')
    return True


def validate_required_env_var(var_name: str, description: Optional[str] = None) -> bool:
    """
    Validate that a required environment variable is set.
    
    Args:
        var_name: Name of the environment variable
        description: Optional description of what the variable is for
        
    Returns:
        bool: True if variable is set, False otherwise
    """
    value = os.getenv(var_name)
    if not value:
        desc = f' ({description})' if description else ''
        logger.error(f'Missing required environment variable: {var_name}{desc}')
        return False
    return True


def validate_env_var_format(var_name: str, expected_prefix: str, description: str) -> bool:
    """
    Validate that an environment variable has the expected format.
    
    Args:
        var_name: Name of the environment variable
        expected_prefix: Expected prefix (e.g., 'sk_test_', 'cus_')
        description: Description of what the variable should contain
        
    Returns:
        bool: True if variable is set and has correct format, False otherwise
    """
    value = os.getenv(var_name)
    if not value:
        return False
    
    if not value.startswith(expected_prefix):
        logger.warning(
            f'Environment variable {var_name} may have incorrect format. '
            f'Expected to start with "{expected_prefix}" but got "{value[:20]}..."'
        )
        return False
    
    return True

