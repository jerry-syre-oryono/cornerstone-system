import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from alumni.models import Person
from django.db.models import Count

def find_duplicates():
    # Find duplicates based on full_name and email
    duplicates = Person.objects.values('full_name', 'email').annotate(name_count=Count('id')).filter(name_count__gt=1)
    
    print(f"Found {duplicates.count()} sets of duplicates based on full_name and email.")
    
    total_dupes = 0
    for entry in duplicates:
        print(f"Name: {entry['full_name']}, Email: {entry['email']}, Count: {entry['name_count']}")
        total_dupes += (entry['name_count'] - 1)
    
    print(f"Total redundant records to remove: {total_dupes}")

    # Also check by phone_primary if email is None
    duplicates_phone = Person.objects.filter(email__isnull=True).values('full_name', 'phone_primary').annotate(name_count=Count('id')).filter(name_count__gt=1)
    print(f"Found {duplicates_phone.count()} sets of duplicates based on full_name and phone_primary (where email is null).")
    
    for entry in duplicates_phone:
        print(f"Name: {entry['full_name']}, Phone: {entry['phone_primary']}, Count: {entry['name_count']}")
        total_dupes += (entry['name_count'] - 1)

    print(f"Grand total redundant records: {total_dupes}")

if __name__ == "__main__":
    find_duplicates()
