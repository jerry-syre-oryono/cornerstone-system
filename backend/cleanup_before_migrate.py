import os
import sys
import django
from django.db import connection

# Add the current directory to sys.path so 'config' and apps can be found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from alumni.models import Person
from django.db.models import Count

def cleanup():
    print("--- Pre-migration Cleanup ---")
    
    # 1. Cleanup by email
    emails = Person.objects.values('email').annotate(count=Count('id')).filter(count__gt=1, email__isnull=False)
    for entry in emails:
        email = entry['email']
        records = Person.objects.filter(email=email).order_by('id')
        keep = records.first()
        to_delete = records.exclude(id=keep.id)
        count = to_delete.count()
        to_delete.delete()
        print(f"Deleted {count} duplicates for email: {email}")

    # 2. Cleanup by phone
    phones = Person.objects.values('phone_primary').annotate(count=Count('id')).filter(count__gt=1, phone_primary__isnull=False)
    for entry in phones:
        phone = entry['phone_primary']
        records = Person.objects.filter(phone_primary=phone).order_by('id')
        keep = records.first()
        to_delete = records.exclude(id=keep.id)
        count = to_delete.count()
        to_delete.delete()
        print(f"Deleted {count} duplicates for phone: {phone}")

    # 3. Cleanup by full_name (optional, but good for appearance)
    names = Person.objects.values('full_name').annotate(count=Count('id')).filter(count__gt=1, full_name__isnull=False)
    for entry in names:
        name = entry['full_name']
        records = Person.objects.filter(full_name=name).order_by('id')
        if records.count() > 1:
            keep = records.first()
            to_delete = records.exclude(id=keep.id)
            count = to_delete.count()
            to_delete.delete()
            print(f"Deleted {count} duplicates for name: {name}")

    print("--- Cleanup Finished ---")

if __name__ == "__main__":
    cleanup()
