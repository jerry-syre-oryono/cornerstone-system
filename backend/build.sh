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
    echo "Creating superuser..."
    python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', '$DJANGO_SUPERUSER_PASSWORD')" 2>/dev/null || echo "Superuser already exists or creation failed"
fi

# Load alumni data from fixture
if [ -f "alumni_data.json" ]; then
    echo "Loading alumni data from fixture..."
    python manage.py loaddata alumni_data.json
    echo "Alumni data loaded successfully"
else
    echo "⚠️  Warning: alumni_data.json not found. Skipping data import."
fi

echo "✅ Build completed successfully!"