import os
import sys
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Import alumni data from Excel file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Excel file name (default: UG DATA BASE 2021.xlsx)',
            default='UG DATA BASE 2021.xlsx'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before import'
        )

    def handle(self, *args, **options):
        # Add scripts directory to path
        scripts_dir = os.path.join(settings.BASE_DIR, 'scripts')
        sys.path.append(scripts_dir)
        
        # Clear data if requested
        if options['clear']:
            from alumni.models import Person
            count = Person.objects.count()
            Person.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Cleared {count} existing records'))
        
        # Import and run the script
        from import_alumni import run
        run()