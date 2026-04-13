from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import User
from .serializers import UserSerializer, UserUpdateSerializer

@extend_schema(responses={200: UserSerializer(many=True)})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_male_users(request):
    """
    List all MALE users who have registered/onboarded.
    """
    users = User.objects.filter(gender='M')
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@extend_schema(responses={200: UserSerializer(many=True)})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_female_users(request):
    """
    List all FEMALE users who have registered/onboarded.
    """
    users = User.objects.filter(gender='F')
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

from rest_framework.parsers import MultiPartParser, FormParser
from .models import User
from .serializers import UserSerializer, UserUpdateSerializer

@extend_schema(
    request=UserUpdateSerializer,
    responses={200: UserSerializer},
    description="Updates the current user's profile details across all 4 interfaces."
)
@api_view(['PATCH', 'PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Update details for the currently authenticated user.
    Supports image uploads for profile_photo.
    """
    user = request.user
    # Add parser_classes for image upload support if needed, 
    # but for function based views we use the request.data which handles it
    serializer = UserUpdateSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(UserSerializer(user).data)
    return Response(serializer.errors, status=400)
