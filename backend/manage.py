#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'billing_portal.settings')
    
    # Validate environment before running any commands (except validation command itself)
    if len(sys.argv) > 1 and sys.argv[1] != 'validate_env':
        try:
            from billing_portal.startup_validation import validate_startup
            # For management commands, don't fail fast - just warn
            # This allows commands like 'collectstatic' to run even if Stripe isn't configured
            validate_startup(fail_fast=False)
        except ImportError:
            # If validation module doesn't exist, continue without validation
            pass
        except Exception:
            # Don't block management commands if validation fails
            pass
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

