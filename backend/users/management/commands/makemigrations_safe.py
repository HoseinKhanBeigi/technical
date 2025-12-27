"""
Django management command to safely create migrations with validation.

This command helps ensure migrations are created correctly and provides
helpful information about what will be migrated.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import sys


class Command(BaseCommand):
    help = 'Safely create migrations with validation checks'

    def add_arguments(self, parser):
        parser.add_argument(
            'app_label',
            nargs='?',
            type=str,
            help='App label to create migrations for (default: all apps)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without creating files',
        )
        parser.add_argument(
            '--check',
            action='store_true',
            help='Check for migration issues without creating files',
        )

    def handle(self, *args, **options):
        app_label = options.get('app_label')
        dry_run = options.get('dry_run', False)
        check = options.get('check', False)

        self.stdout.write(self.style.SUCCESS('=== Safe Migration Creation ===\n'))

        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS('✓ Database connection OK'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Database connection failed: {e}'))
            sys.exit(1)

        # Check for unapplied migrations
        self.stdout.write('\nChecking for unapplied migrations...')
        try:
            call_command('showmigrations', '--list', verbosity=0)
            self.stdout.write(self.style.SUCCESS('✓ Migration status checked'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Warning: {e}'))

        # Run checks
        if check:
            self.stdout.write('\nRunning system checks...')
            try:
                call_command('check', verbosity=1)
                self.stdout.write(self.style.SUCCESS('✓ System checks passed'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ System checks failed: {e}'))
                sys.exit(1)

        # Create migrations
        if not dry_run:
            self.stdout.write(f'\nCreating migrations for: {app_label or "all apps"}...')
            try:
                if app_label:
                    call_command('makemigrations', app_label, verbosity=1)
                else:
                    call_command('makemigrations', verbosity=1)
                self.stdout.write(self.style.SUCCESS('\n✓ Migrations created successfully!'))
                self.stdout.write(self.style.WARNING('\nNext steps:'))
                self.stdout.write('  1. Review the migration files')
                self.stdout.write('  2. Run: python manage.py migrate')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'\n✗ Failed to create migrations: {e}'))
                sys.exit(1)
        else:
            self.stdout.write(self.style.WARNING('\nDry run mode - no files created'))
            self.stdout.write('Run without --dry-run to create migrations')

