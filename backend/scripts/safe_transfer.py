import json
import os
import django

# Setup django environment if running as a standalone script
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from alumni.models import Person
from careers.models import Opportunity
from django.db import IntegrityError

def run():
    file_path = 'transfer_data.json'
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return
    
    person_created = 0
    person_updated = 0
    opp_created = 0
    
    print(f"Processing {len(data)} entries from {file_path}...")
    
    for entry in data:
        model = entry['model']
        fields = entry['fields']
        
        if model == 'alumni.person':
            email = fields.get('email')
            phone = fields.get('phone_primary')
            full_name = fields.get('full_name')
            
            # Smart Matching
            person = None
            if email:
                person = Person.objects.filter(email=email).first()
            if not person and phone:
                person = Person.objects.filter(phone_primary=phone).first()
            if not person and full_name:
                person = Person.objects.filter(full_name__iexact=full_name).first()
                
            if person:
                # Update existing fields if they are not None in the JSON
                for key, value in fields.items():
                    if value is not None:
                        setattr(person, key, value)
                try:
                    person.save()
                    person_updated += 1
                except IntegrityError:
                    continue
            else:
                # Create new
                try:
                    Person.objects.create(**fields)
                    person_created += 1
                except IntegrityError:
                    continue
                    
        elif model == 'careers.opportunity':
            title = fields.get('title')
            org = fields.get('organisation')
            # For simplicity, we skip existing opportunities by title/org
            if not Opportunity.objects.filter(title=title, organisation=org).exists():
                try:
                    # Remove posted_by for now to avoid User matching issues during transfer
                    # It will be null or can be set manually in admin
                    fields.pop('posted_by', None) 
                    Opportunity.objects.create(**fields)
                    opp_created += 1
                except Exception:
                    continue

    print(f"✅ Finished: Persons ({person_created} created, {person_updated} updated), Opportunities ({opp_created} created)")

if __name__ == "__main__":
    run()
