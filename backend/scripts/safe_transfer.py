import json
import os
import django

# Setup django environment if running as a standalone script
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from alumni.models import Person
from careers.models import Opportunity
from django.db import IntegrityError, DataError

def truncate(val, length):
    if val and len(str(val)) > length:
        return str(val)[:length]
    return val

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
            
            # Truncate fields that have max_length in the model
            fields['phone_primary'] = truncate(fields.get('phone_primary'), 50)
            fields['phone_secondary'] = truncate(fields.get('phone_secondary'), 50)
            fields['index_number'] = truncate(fields.get('index_number'), 50)
            fields['employment_status'] = truncate(fields.get('employment_status'), 50)
            fields['marital_status'] = truncate(fields.get('marital_status'), 50)
            fields['data_source'] = truncate(fields.get('data_source'), 50)
            fields['full_name'] = truncate(fields.get('full_name'), 255)
            fields['first_name'] = truncate(fields.get('first_name'), 100)
            fields['sir_name'] = truncate(fields.get('sir_name'), 100)

            # Smart Matching
            person = None
            if email:
                person = Person.objects.filter(email=email).first()
            if not person and fields['phone_primary']:
                person = Person.objects.filter(phone_primary=fields['phone_primary']).first()
            if not person and full_name:
                person = Person.objects.filter(full_name__iexact=full_name).first()
                
            if person:
                # Update existing fields
                for key, value in fields.items():
                    if value is not None:
                        setattr(person, key, value)
                try:
                    person.save()
                    person_updated += 1
                except (IntegrityError, DataError) as e:
                    print(f"Skipping update for {full_name}: {e}")
                    continue
            else:
                # Create new
                try:
                    Person.objects.create(**fields)
                    person_created += 1
                except (IntegrityError, DataError) as e:
                    print(f"Skipping creation for {full_name}: {e}")
                    continue
                    
        elif model == 'careers.opportunity':
            title = fields.get('title')
            org = fields.get('organisation')
            if not Opportunity.objects.filter(title=title, organisation=org).exists():
                try:
                    fields.pop('posted_by', None) 
                    Opportunity.objects.create(**fields)
                    opp_created += 1
                except Exception:
                    continue

    print(f"✅ Finished: Persons ({person_created} created, {person_updated} updated), Opportunities ({opp_created} created)")

if __name__ == "__main__":
    run()
