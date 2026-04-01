import pandas as pd
from alumni.models import Person
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

def clean(val):
    """Clean string values"""
    if pd.isna(val):
        return None
    return str(val).strip()

def clean_int(val, default=None):
    """Clean integer values"""
    if pd.isna(val):
        return default
    try:
        return int(float(str(val).strip()))
    except (ValueError, TypeError):
        return default

def run():
    # Find Excel file
    excel_files = [f for f in os.listdir(script_dir) if f.endswith('.xlsx')]
    if not excel_files:
        print("No Excel files found in scripts directory")
        return
    
    file_path = os.path.join(script_dir, excel_files[0])
    print(f"Found Excel file: {file_path}")
    
    # Try to find the COSA Combined sheet
    xl = pd.ExcelFile(file_path)
    target_sheet = None
    
    # Look for the main COSA Combined sheet
    for sheet in xl.sheet_names:
        if 'COSA Combined' in sheet or 'COSA' in sheet:
            target_sheet = sheet
            break
    
    if not target_sheet:
        print("Could not find COSA Combined sheet, using first sheet")
        target_sheet = xl.sheet_names[0]
    
    print(f"Using sheet: {target_sheet}")
    
    # Read the sheet
    df = pd.read_excel(xl, sheet_name=target_sheet)
    total_rows = len(df)
    print(f"Total rows in sheet: {total_rows}")
    
    count = 0
    skipped = 0
    errors = 0
    
    # Track emails to avoid duplicates
    existing_emails = set(Person.objects.filter(email__isnull=False).values_list('email', flat=True))
    
    for idx, row in df.iterrows():
        try:
            # Extract data with correct column names
            index_val = clean(row.get("Index"))
            names = clean(row.get("Names"))
            sir_name = clean(row.get("Sir Name"))
            first_name = clean(row.get("First Name"))
            graduation_year = clean_int(row.get("Year of Complition"))
            home_district = clean(row.get("Home District"))
            district_residence = clean(row.get("District of Residence"))
            village_residence = clean(row.get("Village/ ward of residence"))
            marital_status = clean(row.get("Marital Satus"))
            phone_primary = clean(row.get("Tell 1 ( MTN)"))
            phone_secondary = clean(row.get("Tell 2 (Airtel/ UTL)"))
            email = clean(row.get("Email"))
            course_offered = clean(row.get("Course offered at  University"))
            employment_status = clean(row.get("Employment Status"))
            area_of_work = clean(row.get("Area of work"))
            place_of_work = clean(row.get("Place of Work"))
            position = clean(row.get("POSITION AT WORKPLACE"))
            sector = clean(row.get("Sector of Work"))
            field_interest = clean(row.get("Field of interest"))
            best_channel = clean(row.get("Best communication channel"))
            title_roles = clean(row.get("Title/Roles"))
            
            # Construct full name
            full_name = names
            if not full_name and first_name:
                full_name = first_name
                if sir_name:
                    full_name += f" {sir_name}"
            
            # Skip if no name at all
            if not full_name and not names and not first_name:
                skipped += 1
                continue
            
            # Check for duplicate email
            if email and email in existing_emails:
                skipped += 1
                continue
            
            # Create the person record
            Person.objects.create(
                index_number=index_val,
                names=names,
                first_name=first_name,
                sir_name=sir_name,
                full_name=full_name or names,
                graduation_year=graduation_year,
                course_offered=course_offered,
                home_district=home_district,
                district_of_residence=district_residence,
                village_residence=village_residence,
                email=email,
                phone_primary=phone_primary,
                phone_secondary=phone_secondary,
                employment_status=employment_status,
                sector_of_work=sector,
                area_of_work=area_of_work,
                place_of_work=place_of_work,
                position_at_workplace=position,
                marital_status=marital_status,
                field_of_interest=field_interest,
                best_communication_channel=best_channel,
                title_roles=title_roles,
            )
            count += 1
            
            if email:
                existing_emails.add(email)
            
            # Progress indicator
            if (idx + 1) % 100 == 0:
                print(f"  Processed {idx + 1}/{total_rows} rows...")
                
        except Exception as e:
            print(f"Row {idx}: ERROR - {e}")
            errors += 1
    
    print(f"\n=== IMPORT SUMMARY ===")
    print(f"Total rows: {total_rows}")
    print(f"Imported: {count}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")
    print(f"Total processed: {count + skipped + errors}")