from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Person
from .serializers import AlumniListSerializer, RegisteredAlumniSerializer

@extend_schema(responses={200: AlumniListSerializer(many=True)})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_alumni(request):
    """
    List ALL alumni (registered and pending).
    """
    alumni = Person.objects.all().prefetch_related('alumni_account')
    serializer = AlumniListSerializer(alumni, many=True)
    return Response(serializer.data)

@extend_schema(responses={200: AlumniListSerializer(many=True)})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_male_alumni(request):
    """
    List all MALE alumni.
    """
    alumni = Person.objects.filter(gender='M').prefetch_related('alumni_account')
    serializer = AlumniListSerializer(alumni, many=True)
    return Response(serializer.data)

@extend_schema(responses={200: AlumniListSerializer(many=True)})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_female_alumni(request):
    """
    List all FEMALE alumni.
    """
    alumni = Person.objects.filter(gender='F').prefetch_related('alumni_account')
    serializer = AlumniListSerializer(alumni, many=True)
    return Response(serializer.data)

@extend_schema(responses={200: RegisteredAlumniSerializer(many=True)})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_registered_alumni(request):
    """
    Public-facing alumni directory. 
    Only shows alumni who have successfully registered an account.
    """
    registered_alumni = Person.objects.filter(alumni_account__isnull=False).order_by('full_name')
    serializer = RegisteredAlumniSerializer(registered_alumni, many=True)
    return Response(serializer.data)
