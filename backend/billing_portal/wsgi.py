"""
WSGI config for billing_portal project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'billing_portal.settings')

# Validate environment before starting application (fail fast on critical errors)
try:
    from .startup_validation import validate_startup
    validate_startup(fail_fast=True)  # Fail fast - don't start if critical config is missing
except ImportError:
    # If validation module doesn't exist, continue without validation
    import logging
    logging.getLogger(__name__).warning("Startup validation module not found, skipping validation")
except SystemExit:
    # Re-raise SystemExit to actually stop the application
    raise
except Exception as e:
    # Log unexpected errors but don't crash (allows graceful degradation)
    import logging
    logging.getLogger(__name__).error(f"Startup validation failed: {e}")

application = get_wsgi_application()

