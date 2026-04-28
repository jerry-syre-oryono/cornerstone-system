from rest_framework import viewsets, generics, status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Event
from .serializers import EventSerializer

class RSVPResponseSerializer(serializers.Serializer):
    status = serializers.CharField(required=False)
    rsvp_count = serializers.IntegerField()
    error = serializers.CharField(required=False)

# Admin APIs: Create, Update, Delete
class AdminEventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdminUser]

    @extend_schema(description="Admin: Create a new event.")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(description="Admin: Update an event.")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(description="Admin: Delete an event.")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

# User APIs: List, RSVP
class EventListView(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(description="User: List all upcoming events.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

@extend_schema(
    responses={200: RSVPResponseSerializer, 400: RSVPResponseSerializer},
    description="User: RSVP to an event. If already RSVPed, it will toggle/remove the RSVP."
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rsvp_to_event(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if event.attendees.filter(id=user.id).exists():
        # Toggle off if already RSVPed
        event.attendees.remove(user)
        return Response({"status": "rsvp_removed", "rsvp_count": event.attendees.count()})
    else:
        # Check capacity
        if event.attendees.count() >= event.capacity:
            return Response({"error": "Event is at full capacity"}, status=status.HTTP_400_BAD_REQUEST)
        
        event.attendees.add(user)
        return Response({"status": "rsvp_success", "rsvp_count": event.attendees.count()})
