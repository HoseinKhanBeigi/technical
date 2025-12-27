"""
Django management command to validate environment variables.

This command checks that all required environment variables are set
and validates their formats.
"""
from django.core.management.base import BaseCommand
from billing_portal.startup_validation import validate_environment, validate_startup
import sys


class Command(BaseCommand):
    help = 'Validate environment variables and configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fail-fast',
            action='store_true',
            help='Exit with error code if validation fails',
        )

    def handle(self, *args, **options):
        fail_fast = options.get('fail_fast', False)
        
        self.stdout.write(self.style.SUCCESS('=== Environment Validation ===\n'))
        
        # Get validation results
        errors = validate_environment()
        
        if errors:
            self.stdout.write(self.style.ERROR('\n✗ Validation FAILED\n'))
            self.stdout.write(self.style.ERROR('Critical configuration errors found:\n'))
            for error in errors:
                self.stdout.write(self.style.ERROR(f'  - {error}'))
            
            if fail_fast:
                self.stdout.write(self.style.ERROR('\nExiting with error code 1'))
                sys.exit(1)
            else:
                self.stdout.write(self.style.WARNING('\nValidation failed but continuing (use --fail-fast to exit on errors)'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ Validation PASSED\n'))
            self.stdout.write('All required environment variables are set correctly.')
            
            # Show warnings if any
            self.stdout.write('\nNote: Some optional variables may be missing (check logs for warnings)')

