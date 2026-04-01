import pandas as pd
from alumni.models import Person
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

def clean(val):
    if pd.isna(val):
        return None
    return str(val).strip().title()

def clean_int(val, default=0):
    if pd.isna(val):
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default

def run():
    # Update filename to match your Excel file
    file_path = os.path.join(script_dir, "UG DATA BASE 2021.xlsx")
    
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return
    
    df = pd.read_excel(file_path)
    count = 0
    skipped = 0
    
    for _, row in df.iterrows():
        full_name = clean(row.get("Names"))
        first_name = clean(row.get("First Name"))
        last_name = clean(row.get("Sir Name"))
        
        if not first_name or not last_name:
            if full_name:
                parts = full_name.split()
                first_name = parts[0]
                last_name = parts[-1] if len(parts) > 1 else ""
        
        if not first_name:
            print(f"Skipping row due to missing name: {row.to_dict()}")
            skipped += 1
            continue
        
        Person.objects.create(
            full_name=full_name or f"{first_name} {last_name}",
            first_name=first_name,
            last_name=last_name,
            graduation_year=clean_int(row.get("Year of Complition")),
            email=clean(row.get("Email")),
            phone_primary=clean(row.get("Tell 1 ( MTN)")),
        )
        count += 1
    
    print(f"Imported {count} records (skipped {skipped})")