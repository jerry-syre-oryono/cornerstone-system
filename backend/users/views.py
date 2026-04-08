from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import User
from .serializers import UserSerializer

@extend_schema(responses={200: UserSerializer(many=True)})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_male_users(request):
    """
    List all MALE registered users.
    """
    users = User.objects.filter(gender='M')
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@extend_schema(responses={200: UserSerializer(many=True)})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_female_users(request):
    """
    List all FEMALE registered users.
    """
    users = User.objects.filter(gender='F')
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)
