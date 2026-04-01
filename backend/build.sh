#!/usr/bin/env bash
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Create superuser if environment variable is set
if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', '$DJANGO_SUPERUSER_PASSWORD')" 2>/dev/null || echo "Superuser already exists or creation failed"
fi

# Load alumni data from fixture (preferred method)
if [ -f "alumni_data.json" ]; then
    echo "Loading alumni data from fixture..."
    python manage.py loaddata alumni_data.json
    echo "Loaded alumni data from fixture"
else
    # Fallback to Excel import
    echo "No fixture found, importing from Excel..."
    
    # Import alumni data if database is empty or reset flag is set
    if [ "$RESET_DB" = "true" ]; then
        echo "Reset flag detected, clearing existing data..."
        python manage.py shell -c "from alumni.models import Person; Person.objects.all().delete(); print('Cleared existing records')"
    fi
    
    echo "Checking if alumni data exists..."
    python manage.py shell -c "
from alumni.models import Person
import sys
sys.exit(0 if Person.objects.count() == 0 else 1)
" && python manage.py shell -c "
import sys
import os

# Add scripts directory to path
sys.path.append('scripts')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

# Run the import script
from import_alumni import run
run()
"
fi

echo "Build completed!"