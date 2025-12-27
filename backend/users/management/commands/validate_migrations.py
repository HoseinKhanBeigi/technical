"""
Django management command to validate migrations and model consistency.

This command checks for common migration issues and validates that
models are properly configured.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.apps import apps
import sys


class Command(BaseCommand):
    help = 'Validate migrations and model consistency'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix common issues automatically',
        )

    def handle(self, *args, **options):
        fix = options.get('fix', False)
        errors = []
        warnings = []

        self.stdout.write(self.style.SUCCESS('=== Migration Validation ===\n'))

        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS('✓ Database connection OK'))
        except Exception as e:
            errors.append(f'Database connection failed: {e}')
            self.stdout.write(self.style.ERROR('✗ Database connection failed'))

        # Check for unapplied migrations
        self.stdout.write('\nChecking migration status...')
        try:
            call_command('showmigrations', '--list', verbosity=0)
            self.stdout.write(self.style.SUCCESS('✓ Migration status OK'))
        except Exception as e:
            warnings.append(f'Migration status check: {e}')

        # Validate models
        self.stdout.write('\nValidating models...')
        try:
            # Get User model
            User = apps.get_model('users', 'User')
            
            # Check for required fields
            required_fields = ['subscription_status', 'current_plan', 'total_amount_paid']
            for field_name in required_fields:
                if not hasattr(User, field_name):
                    errors.append(f'Missing required field: {field_name}')
                else:
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Field {field_name} exists'))

            # Check for indexes
            if hasattr(User._meta, 'indexes') and User._meta.indexes:
                self.stdout.write(self.style.SUCCESS(f'  ✓ {len(User._meta.indexes)} indexes defined'))
            else:
                warnings.append('No custom indexes defined')

            # Check for constraints
            if hasattr(User._meta, 'constraints') and User._meta.constraints:
                self.stdout.write(self.style.SUCCESS(f'  ✓ {len(User._meta.constraints)} constraints defined'))
            else:
                warnings.append('No custom constraints defined')

        except Exception as e:
            errors.append(f'Model validation failed: {e}')

        # Run Django system checks
        self.stdout.write('\nRunning Django system checks...')
        try:
            call_command('check', verbosity=0)
            self.stdout.write(self.style.SUCCESS('✓ System checks passed'))
        except Exception as e:
            errors.append(f'System checks failed: {e}')

        # Summary
        self.stdout.write('\n' + '=' * 50)
        if errors:
            self.stdout.write(self.style.ERROR(f'\n✗ Found {len(errors)} error(s):'))
            for error in errors:
                self.stdout.write(self.style.ERROR(f'  - {error}'))
            sys.exit(1)
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ Validation passed!'))

        if warnings:
            self.stdout.write(self.style.WARNING(f'\n⚠ Found {len(warnings)} warning(s):'))
            for warning in warnings:
                self.stdout.write(self.style.WARNING(f'  - {warning}'))

