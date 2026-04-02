#!/usr/bin/env bash
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run pre-migration cleanup to ensure unique constraints can be applied
echo "🧹 Cleaning up duplicates before migration..."
python cleanup_before_migrate.py

# Run migrations
python manage.py migrate

# Create superuser if environment variable is set
if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', '$DJANGO_SUPERUSER_PASSWORD')" 2>/dev/null || echo "Superuser already exists or creation failed"
fi

# Import alumni data from Excel
if [ -f "scripts/UG DATA BASE 2021.xlsx" ]; then
    echo "📊 Importing alumni data from Excel..."
    python manage.py shell -c "
import sys
sys.path.append('scripts')
from import_all_sheets import run
run()
"
    echo "✅ Excel import completed"
else
    echo "⚠️  No Excel file found, skipping data import"
fi

echo "✅ Build completed successfully!"