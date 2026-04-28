from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from .models import Resource

class ResourceSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = [
            'id', 'title', 'category', 'file_type', 'file_url', 
            'description', 'uploaded_by', 'uploaded_by_name', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['uploaded_by', 'created_at', 'updated_at']

    @extend_schema_field(OpenApiTypes.STR)
    def get_uploaded_by_name(self, obj) -> str:
        return obj.uploaded_by.get_full_name() if obj.uploaded_by else "System"
