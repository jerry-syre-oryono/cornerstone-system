from rest_framework import serializers
from .models import Resource

class ResourceSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.ReadOnlyField(source='uploaded_by.get_full_name')

    class Meta:
        model = Resource
        fields = [
            'id', 'title', 'category', 'file_type', 'file_url', 
            'description', 'uploaded_by', 'uploaded_by_name', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['uploaded_by', 'created_at', 'updated_at']
