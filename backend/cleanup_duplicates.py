import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from alumni.models import Person
from django.db.models import Count

def cleanup_duplicates():
    # 1. Remove records where name and email and phone are all null
    null_records = Person.objects.filter(full_name__isnull=True, email__isnull=True, phone_primary__isnull=True)
    null_count = null_records.count()
    null_records.delete()
    print(f"Deleted {null_count} records where name, email, and phone were all null.")

    # 2. Handle "None None" records if they exist as strings
    none_none_records = Person.objects.filter(full_name="None None")
    none_none_count = none_none_records.count()
    if none_none_count > 1:
        # Keep only one or delete all if they are useless
        # For now let's delete them as they seem to be junk data from import
        none_none_records.delete()
        print(f"Deleted {none_none_count} 'None None' records.")

    # 3. Cleanup by email
    emails = Person.objects.values('email').annotate(count=Count('id')).filter(count__gt=1, email__isnull=False)
    for entry in emails:
        email = entry['email']
        records = Person.objects.filter(email=email).order_by('id')
        keep = records.first()
        to_delete = records.exclude(id=keep.id)
        count = to_delete.count()
        to_delete.delete()
        print(f"Deleted {count} duplicates for email: {email}")

    # 4. Cleanup by phone
    phones = Person.objects.values('phone_primary').annotate(count=Count('id')).filter(count__gt=1, phone_primary__isnull=False)
    for entry in phones:
        phone = entry['phone_primary']
        records = Person.objects.filter(phone_primary=phone).order_by('id')
        keep = records.first()
        to_delete = records.exclude(id=keep.id)
        count = to_delete.count()
        to_delete.delete()
        print(f"Deleted {count} duplicates for phone: {phone}")

    # 5. Cleanup by full_name (careful here, but since it's alumni data, name + something else usually unique)
    # We already did email and phone, so now we check names that might still have duplicates
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

if __name__ == "__main__":
    cleanup_duplicates()
