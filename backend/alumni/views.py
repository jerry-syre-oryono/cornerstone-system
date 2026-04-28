from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiTypes
from .models import Person
from .serializers import AlumniListSerializer, RegisteredAlumniSerializer, PersonSerializer, AdminAddAlumniSerializer

class AlumniStatusResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField()

@extend_schema(responses={200: AlumniListSerializer(many=True)})
@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_alumni(request):
    """
    List ALL ACTIVE alumni (registered and pending).
    """
    alumni = Person.objects.filter(is_archived=False).prefetch_related('alumni_account')
    serializer = AlumniListSerializer(alumni, many=True)
    return Response(serializer.data)

@extend_schema(responses={200: AlumniListSerializer(many=True)})
@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_archived_alumni(request):
    """
    List ALL ARCHIVED alumni. Admin only.
    """
    alumni = Person.objects.filter(is_archived=True).prefetch_related('alumni_account')
    serializer = AlumniListSerializer(alumni, many=True)
    return Response(serializer.data)

@extend_schema(request=AdminAddAlumniSerializer, responses={201: PersonSerializer})
@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_alumni(request):
    """
    Add a new alumni record. Admin only.
    """
    serializer = AdminAddAlumniSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@extend_schema(request=PersonSerializer, responses={200: PersonSerializer})
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdminUser])
def edit_alumni(request, pk):
    """
    Edit an existing alumni record. Admin only.
    """
    try:
        person = Person.objects.get(pk=pk)
    except Person.DoesNotExist:
        return Response({"error": "Alumni record not found."}, status=404)
    
    partial = request.method == 'PATCH'
    serializer = PersonSerializer(person, data=request.data, partial=partial)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@extend_schema(request=None, responses={200: AlumniStatusResponseSerializer})
@api_view(['POST'])
@permission_classes([IsAdminUser])
def archive_alumni(request, pk):
    """
    Archive an alumni record. Admin only.
    """
    try:
        person = Person.objects.get(pk=pk)
        person.is_archived = True
        person.save()
        return Response({"status": "archived", "message": f"Alumni {person.full_name} has been archived."})
    except Person.DoesNotExist:
        return Response({"error": "Alumni record not found."}, status=404)

@extend_schema(request=None, responses={200: AlumniStatusResponseSerializer})
@api_view(['POST'])
@permission_classes([IsAdminUser])
def unarchive_alumni(request, pk):
    """
    Unarchive an alumni record. Admin only.
    """
    try:
        person = Person.objects.get(pk=pk)
        person.is_archived = False
        person.save()
        return Response({"status": "unarchived", "message": f"Alumni {person.full_name} has been restored."})
    except Person.DoesNotExist:
        return Response({"error": "Alumni record not found."}, status=404)

@extend_schema(responses={200: AlumniListSerializer(many=True)})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_male_alumni(request):
    """
    List all MALE alumni who have NOT registered yet.
    """
    alumni = Person.objects.filter(gender='M', alumni_account__isnull=True)
    serializer = AlumniListSerializer(alumni, many=True)
    return Response(serializer.data)

@extend_schema(responses={200: AlumniListSerializer(many=True)})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_female_alumni(request):
    """
    List all FEMALE alumni who have NOT registered yet.
    """
    alumni = Person.objects.filter(gender='F', alumni_account__isnull=True)
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
