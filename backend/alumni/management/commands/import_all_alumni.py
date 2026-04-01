from django.core.management.base import BaseCommand
from django.conf import settings
import sys
import os

class Command(BaseCommand):
    help = 'Import all alumni data from Excel file'

    def add_arguments(self, parser):
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
            from alumni.models import COSAAlumni, AYLFAlumni, YouthCorpsAlumni
            
            count1 = COSAAlumni.objects.count()
            count2 = AYLFAlumni.objects.count()
            count3 = YouthCorpsAlumni.objects.count()
            
            COSAAlumni.objects.all().delete()
            AYLFAlumni.objects.all().delete()
            YouthCorpsAlumni.objects.all().delete()
            
            self.stdout.write(self.style.WARNING(f'Cleared: COSA ({count1}), AYLF ({count2}), Youth Corps ({count3})'))
        
        # Import all sheets
        from import_all_sheets import run
        run()