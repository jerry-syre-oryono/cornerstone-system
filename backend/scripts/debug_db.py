import os
import sys
import django
from django.db import connection
from dotenv import load_dotenv
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

load_dotenv(BASE_DIR.parent / '.env')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def check():
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL')[:30]}...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            row = cursor.fetchone()
            print(f"Connected to: {row[0]}")
            
            cursor.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public';")
            tables = cursor.fetchall()
            print(f"Tables found: {len(tables)}")
            for t in tables:
                print(f" - {t[0]}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check()
