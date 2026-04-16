from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import User
from .serializers import UserSerializer, UserUpdateSerializer
from alumni.models import Person
from onboarding.models import SignupRequest

@extend_schema(responses={200: dict})
@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_stats(request):
    """
    Overview stats for admin dashboard.
    """
    stats = {
        "total_alumni": Person.objects.count(),
        "total_users_signed_up": User.objects.count(),
        "total_male_users": User.objects.filter(gender='M').count(),
        "total_female_users": User.objects.filter(gender='F').count(),
        "total_at_university": User.objects.filter(academic_status='Still at University').count(),
        "total_who_have_graduated": User.objects.filter(academic_status='University Graduate').count(),
        "total_employed": User.objects.filter(employment_status__in=['Employed', 'Self-Employed']).count(),
        "total_pending_approvals": SignupRequest.objects.filter(status='PENDING').count(),
    }
    return Response(stats)

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

@extend_schema(responses={200: UserSerializer})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_profile(request):
    """
    Get the profile of the currently authenticated user.
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

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
