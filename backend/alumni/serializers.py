from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Person

class RegisteredAlumniSerializer(serializers.ModelSerializer):
    """
    Serializer for alumni who have registered (have an AlumniAccount).
    Includes more profile information for a directory view.
    """
    class Meta:
        model = Person
        fields = [
            'id', 'full_name', 'first_name', 'sir_name', 'graduation_year', 
            'email', 'phone_primary', 'employment_status', 'sector_of_work', 
            'area_of_work', 'place_of_work', 'position_at_workplace'
        ]

class AlumniListSerializer(serializers.ModelSerializer):

    status = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = ['id', 'full_name', 'graduation_year', 'email', 'phone_primary', 'status']

    @extend_schema_field(serializers.CharField())
    def get_status(self, obj):
        return "Signed Up" if hasattr(obj, 'alumni_account') else "Pending"
