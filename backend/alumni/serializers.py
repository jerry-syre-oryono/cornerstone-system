from rest_framework import serializers
from .models import Person

class AlumniListSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = ['id', 'full_name', 'graduation_year', 'email', 'phone_primary', 'status']

    def get_status(self, obj):
        return "Signed Up" if hasattr(obj, 'alumni_account') else "Pending"
