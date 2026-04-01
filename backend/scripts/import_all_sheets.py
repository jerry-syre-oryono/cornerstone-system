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
        return int(float(str(val).strip()))
    except (ValueError, TypeError):
        return default

def import_cosa_sheet(df, sheet_name):
    """Import COSA Combined sheet"""
    count = 0
    for idx, row in df.iterrows():
        try:
            full_name = clean(row.get("Names"))
            first_name = clean(row.get("First Name"))
            sir_name = clean(row.get("Sir Name"))
            
            if not full_name and first_name:
                full_name = first_name
                if sir_name:
                    full_name += f" {sir_name}"
            
            if not full_name:
                continue
            
            Person.objects.create(
                full_name=full_name,
                names=full_name,
                first_name=first_name,
                sir_name=sir_name,
                graduation_year=clean_int(row.get("Year of Complition")),
                email=clean(row.get("Email")),
                phone_primary=clean(row.get("Tell 1 ( MTN)")),
                home_district=clean(row.get("Home District")),
                district_of_residence=clean(row.get("District of Residence")),
                village_residence=clean(row.get("Village/ ward of residence")),
                employment_status=clean(row.get("Employment Status")),
                place_of_work=clean(row.get("Place of Work")),
                position_at_workplace=clean(row.get("POSITION AT WORKPLACE")),
                sector_of_work=clean(row.get("Sector of Work")),
                marital_status=clean(row.get("Marital Satus")),
                phone_secondary=clean(row.get("Tell 2 (Airtel/ UTL)")),
                course_offered=clean(row.get("Course offered at  University")),
                area_of_work=clean(row.get("Area of work")),
                field_of_interest=clean(row.get("Field of interest")),
                best_communication_channel=clean(row.get("Best communication channel")),
                title_roles=clean(row.get("Title/Roles")),
                data_source="COSA",
            )
            count += 1
        except Exception as e:
            print(f"COSA Row {idx}: ERROR - {e}")
    return count

def import_aylf_sheet(df, sheet_name):
    """Import AYLF sheet"""
    count = 0
    for idx, row in df.iterrows():
        try:
            surname = clean(row.get("Surname ?"))
            other_names = clean(row.get("Other Names?"))
            full_name = f"{surname} {other_names}".strip() if surname and other_names else surname or other_names
            
            if not full_name:
                continue
            
            Person.objects.create(
                full_name=full_name,
                first_name=other_names,
                sir_name=surname,
                graduation_year=clean_int(row.get("Year")),
                email=clean(row.get("Email Address")),
                phone_primary=clean(row.get("Current Telephone Contact Tel 1")),
                home_district=clean(row.get("District f Origin ?")),
                district_of_residence=clean(row.get("Current district of work/Residence ?")),
                employment_status=clean(row.get("Employment status( work Done to earn a living)")),
                place_of_work=clean(row.get("Employment Org.")),
                position_at_workplace=clean(row.get("Designation or Job Title?")),
                sector_of_work=clean(row.get("If Yes, state the Sector of your Employment ?")),
                marital_status=clean(row.get("Marital Status?")),
                phone_secondary=clean(row.get("Telephone 2")),
                field_of_interest=clean(row.get("Other Areas of Influence or Interests")),
                best_communication_channel=clean(row.get("Communication")),
                data_source="AYLF",
            )
            count += 1
        except Exception as e:
            print(f"AYLF Row {idx}: ERROR - {e}")
    return count

def import_youth_corps_sheet(df, sheet_name):
    """Import Youth Corps sheet"""
    count = 0
    for idx, row in df.iterrows():
        try:
            names = clean(row.get("Names"))
            first_name = clean(row.get("First Name"))
            sir_name = clean(row.get("Sir Name"))
            full_name = names or f"{first_name} {sir_name}".strip()
            
            if not full_name:
                continue
            
            Person.objects.create(
                full_name=full_name,
                names=names,
                first_name=first_name,
                sir_name=sir_name,
                graduation_year=clean_int(row.get("Year")),
                email=clean(row.get("Email")),
                phone_primary=clean(row.get("Tell 1")),
                home_district=clean(row.get("Home District")),
                district_of_residence=clean(row.get("Residence")),
                employment_status=clean(row.get("Emplyment Status")),
                place_of_work=clean(row.get("Place of Work")),
                position_at_workplace=clean(row.get("Title/Roles")),
                sector_of_work=clean(row.get("Sector of Work/Profession/Field of Interest")),
                marital_status=clean(row.get("Marital Satus")),
                phone_secondary=clean(row.get("Tell 2")),
                field_of_interest=clean(row.get("Interest")),
                best_communication_channel=clean(row.get("Best Communication")),
                data_source="Youth Corps",
            )
            count += 1
        except Exception as e:
            print(f"Youth Corps Row {idx}: ERROR - {e}")
    return count

def run():
    """Main import function"""
    excel_files = [f for f in os.listdir(script_dir) if f.endswith('.xlsx')]
    if not excel_files:
        print("No Excel files found in scripts directory")
        return
    
    file_path = os.path.join(script_dir, excel_files[0])
    print(f"Found Excel file: {file_path}")
    
    xl = pd.ExcelFile(file_path)
    total_imported = 0
    stats = {}
    
    for sheet_name in xl.sheet_names:
        print(f"\n{'='*50}")
        print(f"Processing sheet: {sheet_name}")
        print(f"{'='*50}")
        
        df = pd.read_excel(xl, sheet_name=sheet_name)
        rows = len(df)
        print(f"Rows in sheet: {rows}")
        
        columns = list(df.columns)
        imported = 0
        
        if 'Course offered at  University' in columns or 'Tell 1 ( MTN)' in columns:
            imported = import_cosa_sheet(df, sheet_name)
            stats['COSA'] = stats.get('COSA', 0) + imported
        elif 'Surname ?' in columns:
            imported = import_aylf_sheet(df, sheet_name)
            stats['AYLF'] = stats.get('AYLF', 0) + imported
        elif 'Best Communication' in columns:
            imported = import_youth_corps_sheet(df, sheet_name)
            stats['Youth Corps'] = stats.get('Youth Corps', 0) + imported
        else:
            print(f"  Unknown sheet format, skipping...")
            continue
        
        total_imported += imported
        print(f"✅ Imported: {imported} records")
    
    print(f"\n{'='*50}")
    print(f"IMPORT SUMMARY")
    print(f"{'='*50}")
    for source, count in stats.items():
        print(f"{source}: {count} records")
    print(f"{'-'*50}")
    print(f"TOTAL: {total_imported} records")
    print(f"{'='*50}")