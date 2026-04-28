from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Resource
from .serializers import ResourceSerializer

@extend_schema(responses={200: ResourceSerializer(many=True)})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_resources(request):
    """
    List all shared resources.
    """
    resources = Resource.objects.all()
    serializer = ResourceSerializer(resources, many=True)
    return Response(serializer.data)

@extend_schema(request=ResourceSerializer, responses={201: ResourceSerializer})
@api_view(['POST'])
@permission_classes([IsAdminUser])
def upload_resource(request):
    """
    Upload a new resource. Admin only.
    """
    serializer = ResourceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(uploaded_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(responses={200: ResourceSerializer})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_resource(request, pk):
    """
    Get details of a single resource.
    """
    try:
        resource = Resource.objects.get(pk=pk)
    except Resource.DoesNotExist:
        return Response({"error": "Resource not found."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ResourceSerializer(resource)
    return Response(serializer.data)
