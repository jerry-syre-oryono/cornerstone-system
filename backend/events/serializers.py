from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    rsvp_count = serializers.IntegerField(source='attendees.count', read_only=True)
    is_rsvped = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'event_type', 'start_date', 'end_date', 
            'capacity', 'location', 'description', 'rsvp_count', 'is_rsvped'
        ]

    def get_is_rsvped(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.attendees.filter(id=request.user.id).exists()
        return False
