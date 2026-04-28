from rest_framework import serializers
from .models import Opportunity

class OpportunitySerializer(serializers.ModelSerializer):
    posted_by_name = serializers.ReadOnlyField(source='posted_by.get_full_name')

    class Meta:
        model = Opportunity
        fields = [
            'id', 'title', 'organisation', 'type', 'deadline', 
            'location', 'description', 'requirements', 'application_link', 
            'posted_by', 'posted_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['posted_by', 'created_at', 'updated_at']
