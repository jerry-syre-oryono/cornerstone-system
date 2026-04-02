from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Person

class AlumniListSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = ['id', 'full_name', 'graduation_year', 'email', 'phone_primary', 'status']

    @extend_schema_field(serializers.CharField())
    def get_status(self, obj):
        return "Signed Up" if hasattr(obj, 'alumni_account') else "Pending"
