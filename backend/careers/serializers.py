from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from .models import Opportunity

class OpportunitySerializer(serializers.ModelSerializer):
    posted_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = [
            'id', 'title', 'organisation', 'type', 'deadline', 
            'location', 'description', 'requirements', 'application_link', 
            'posted_by', 'posted_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['posted_by', 'created_at', 'updated_at']

    @extend_schema_field(OpenApiTypes.STR)
    def get_posted_by_name(self, obj):
        return obj.posted_by.get_full_name() if obj.posted_by else "System"
