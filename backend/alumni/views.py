from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Person
from .serializers import AlumniListSerializer

@extend_schema(responses={200: AlumniListSerializer(many=True)})
@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_alumni(request):
    """
    List all alumni with their signup status.
    Accessible only by Admin users.
    """
    alumni = Person.objects.all().prefetch_related('alumni_account')
    serializer = AlumniListSerializer(alumni, many=True)
    return Response(serializer.data)
