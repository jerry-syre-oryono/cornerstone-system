import os
import pandas as pd
from django.core.management.base import BaseCommand
from alumni.models import Person
from django.db import IntegrityError, models

class Command(BaseCommand):
    help = 'Import/Update alumni from COSA Mailing List Excel with smarter matching'

    def handle(self, *args, **options):
        file_path = os.path.join('scripts', 'COSA UG Mailing list (1) (1).xlsx')
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading Excel: {e}"))
            return
        
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for idx, row in df.iterrows():
            first_name = str(row.get('First Name', '')).strip() if pd.notna(row.get('First Name')) else ''
            sir_name = str(row.get('Sirname', '')).strip() if pd.notna(row.get('Sirname')) else ''
            full_name = f"{first_name} {sir_name}".strip()
            
            if not full_name:
                continue

            # Email cleaning
            email = str(row.get('Email Address', '')).strip().replace(',', '.') if pd.notna(row.get('Email Address')) else None
            if email and ('@' not in email or '.' not in email):
                email = None

            # Phone cleaning - take the first number if multiple exist
            phone_raw = str(row.get('Phone number', '')).strip() if pd.notna(row.get('Phone number')) else None
            phone = None
            if phone_raw:
                # Split by common separators and take first part
                phone = phone_raw.replace('/', ',').split(',')[0].strip()
                if len(phone) > 50:
                    phone = phone[:50]

            grad_year = None
            try:
                if pd.notna(row.get('Year of Graduation')):
                    grad_year = int(float(row.get('Year of Graduation')))
            except (ValueError, TypeError):
                pass

            city = str(row.get('Current city', '')).strip() if pd.notna(row.get('Current city')) else None
            school = str(row.get('School', '')).strip() if pd.notna(row.get('School')) else ''

            # Smarter Matching Logic:
            # 1. Try by email (most unique)
            # 2. Try by phone
            # 3. Try by full name
            
            person = None
            if email:
                person = Person.objects.filter(email=email).first()
            
            if not person and phone:
                person = Person.objects.filter(phone_primary=phone).first()
                
            if not person:
                person = Person.objects.filter(full_name__iexact=full_name).first()

            if person:
                # Update existing
                if email: person.email = email
                if grad_year: person.graduation_year = grad_year
                if phone: person.phone_primary = phone
                if city: person.district_of_residence = city
                
                # Update name if the existing one is shorter or likely less complete
                if len(full_name) > len(person.full_name or ''):
                    person.full_name = full_name
                
                person.data_source = f"COSA Mailing List ({school})" if school else "COSA Mailing List"
                
                try:
                    person.save()
                    updated_count += 1
                except IntegrityError as e:
                    self.stdout.write(self.style.WARNING(f"Row {idx+2}: Conflict updating {full_name}: {e}"))
                    skipped_count += 1
            else:
                # Create new
                try:
                    Person.objects.create(
                        full_name=full_name,
                        first_name=first_name,
                        sir_name=sir_name,
                        email=email,
                        graduation_year=grad_year,
                        phone_primary=phone,
                        district_of_residence=city,
                        data_source=f"COSA Mailing List ({school})" if school else "COSA Mailing List"
                    )
                    created_count += 1
                except IntegrityError as e:
                    self.stdout.write(self.style.WARNING(f"Row {idx+2}: Conflict creating {full_name}: {e}"))
                    skipped_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Import Finished: {created_count} created, {updated_count} updated, {skipped_count} skipped."
        ))
