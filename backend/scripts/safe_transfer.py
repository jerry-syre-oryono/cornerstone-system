import json
import os
import sys
import django
import time

# Setup django environment if running as a standalone script
if __name__ == "__main__":
    # Add the backend directory to sys.path
    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if backend_path not in sys.path:
        sys.path.append(backend_path)
        
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from alumni.models import Person
from careers.models import Opportunity
from django.db import IntegrityError, DataError, connection, InterfaceError, OperationalError

def truncate(val, length):
    if val and len(str(val)) > length:
        return str(val)[:length]
    return val

def ensure_connection():
    """Checks and restores database connection if dropped."""
    try:
        connection.cursor()
    except (InterfaceError, OperationalError):
        print("🔄 Connection lost. Reconnecting...")
        connection.close()
        connection.connect()

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
    total = len(data)
    
    print(f"🚀 Starting import of {total} entries...")
    
    for i, entry in enumerate(data):
        # Prevent connection timeouts by refreshing every 50 records
        if i % 50 == 0:
            ensure_connection()
            if i > 0:
                print(f"Progress: {i}/{total} processed...")

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
            try:
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
                    person.save()
                    person_updated += 1
                else:
                    # Create new
                    Person.objects.create(**fields)
                    person_created += 1
            except (IntegrityError, DataError, OperationalError, InterfaceError) as e:
                # If it's a connection error, try to reconnect and continue
                if isinstance(e, (OperationalError, InterfaceError)):
                    ensure_connection()
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

    print(f"\n✅ Finished!")
    print(f"Created: {person_created} | Updated: {person_updated} | Opportunities: {opp_created}")

if __name__ == "__main__":
    run()
