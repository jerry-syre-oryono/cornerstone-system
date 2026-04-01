import pandas as pd
from alumni.models import Person
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

def clean(val):
    if pd.isna(val):
        return None
    return str(val).strip()

def clean_int(val, default=None):
    if pd.isna(val):
        return default
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default

def clean_employment_status(val):
    if pd.isna(val):
        return None
    val = str(val).upper().strip()
    if 'EMPLOY' in val:
        return 'EMPLOYED'
    elif 'UNEMPLOY' in val or 'NOT EMPLOY' in val:
        return 'UNEMPLOYED'
    elif 'DECEASED' in val or 'PASSED' in val:
        return 'DECEASED'
    return val

def import_sheet(df, sheet_name):
    """Import data from a single sheet"""
    count = 0
    skipped = 0
    
    for idx, row in df.iterrows():
        try:
            # Extract data
            names = clean(row.get("Names"))
            sir_name = clean(row.get("Sir Name"))
            first_name = clean(row.get("First Name"))
            
            # Construct full name
            full_name = names
            if not full_name and first_name:
                full_name = first_name
                if sir_name:
                    full_name += f" {sir_name}"
            
            # Skip if no name at all
            if not names and not first_name and not sir_name:
                skipped += 1
                continue
            
            # Create the person record
            Person.objects.create(
                index_number=clean(row.get("Index")),
                names=names,
                first_name=first_name,
                sir_name=sir_name,
                full_name=full_name,
                graduation_year=clean_int(row.get("Year of Complition")),
                course_offered=clean(row.get("Course offered at  University")),
                home_district=clean(row.get("Home District")),
                district_of_residence=clean(row.get("District of Residence")),
                village_residence=clean(row.get("Village/ ward of residence")),
                email=clean(row.get("Email")),
                phone_primary=clean(row.get("Tell 1 ( MTN)")),
                phone_secondary=clean(row.get("Tell 2 (Airtel/ UTL)")),
                employment_status=clean_employment_status(row.get("Employment Status")),
                sector_of_work=clean(row.get("Sector of Work")),
                area_of_work=clean(row.get("Area of work")),
                place_of_work=clean(row.get("Place of Work")),
                position_at_workplace=clean(row.get("POSITION AT WORKPLACE")),
                marital_status=clean(row.get("Marital Satus")),
                field_of_interest=clean(row.get("Field of interest")),
                best_communication_channel=clean(row.get("Best communication channel")),
                title_roles=clean(row.get("Title/Roles")),
            )
            count += 1
            
        except Exception as e:
            print(f"Sheet '{sheet_name}', Row {idx}: ERROR - {e}")
            continue
    
    return count, skipped

def run():
    # Find Excel file
    excel_files = [f for f in os.listdir(script_dir) if f.endswith('.xlsx')]
    if not excel_files:
        print("No Excel files found in scripts directory")
        return
    
    file_path = os.path.join(script_dir, excel_files[0])
    print(f"Found Excel file: {file_path}")
    
    # Read all sheets
    xl = pd.ExcelFile(file_path)
    total_imported = 0
    total_skipped = 0
    
    for sheet_name in xl.sheet_names:
        print(f"\n--- Processing sheet: {sheet_name} ---")
        df = pd.read_excel(xl, sheet_name=sheet_name)
        rows = len(df)
        print(f"Rows in sheet: {rows}")
        
        imported, skipped = import_sheet(df, sheet_name)
        total_imported += imported
        total_skipped += skipped
        
        print(f"Imported from {sheet_name}: {imported} records (skipped {skipped})")
    
    print(f"\n=== TOTAL IMPORT SUMMARY ===")
    print(f"Total imported: {total_imported}")
    print(f"Total skipped: {total_skipped}")
    print(f"Overall total: {total_imported + total_skipped}")