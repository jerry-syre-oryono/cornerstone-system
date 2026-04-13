from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.utils import timezone
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from .services import find_match
from alumni.models import Person, AlumniAccount
from .models import SignupRequest

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .serializers import (
    RegisterAlumniSerializer, LoginSerializer, PasswordResetSerializer, 
    PasswordResetConfirmSerializer, SignupRequestSerializer, 
    AdminSignupRequestSerializer, AdminCreateUserSerializer
)

User = get_user_model()

@extend_schema(
    tags=['Auth & Onboarding'],
    request=RegisterAlumniSerializer, 
    responses={
        200: dict,
        202: dict,
        400: dict
    },
    description="Registers an alumni. If the record is found, an account is created. If not found, a SignupRequest is created for admin review."
)
@api_view(['POST'])
def register_alumni(request):
    """
    Form-based registration workflow:
    - full_name, graduation_year, email, password, password_again
    - Verify password match
    - Find alumni match
    - IF MATCH FOUND:
        - Create User and AlumniAccount link
        - Set email on Person if missing
        - Login
    - IF NO MATCH FOUND:
        - Create SignupRequest for Admin approval
    """
    full_name = request.data.get("full_name")
    graduation_year = request.data.get("graduation_year")
    email = request.data.get("email")
    password = request.data.get("password")
    password_again = request.data.get("password_again")
    
    # Optional fields for SignupRequest
    phone = request.data.get("phone")
    gender = request.data.get("gender")
    course = request.data.get("course")

    if not all([full_name, graduation_year, email, password, password_again]):
        return Response({"error": "All fields are required."}, status=400)

    if password != password_again:
        return Response({"error": "Passwords do not match."}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({"error": "A user with this email already exists."}, status=400)

    person = find_match(full_name, graduation_year)
    
    if not person:
        # Create a SignupRequest instead of failing
        if SignupRequest.objects.filter(email=email).exists():
            return Response({"error": "A signup request with this email already exists and is pending review."}, status=400)
        
        SignupRequest.objects.create(
            full_name=full_name,
            email=email,
            graduation_year=graduation_year,
            phone=phone,
            gender=gender,
            course=course,
            status='PENDING'
        )
        return Response({
            "status": "request_submitted",
            "message": "Alumni record not found. Your details have been submitted for admin review."
        }, status=202) # 202 Accepted

    # Normal onboarding if person is found
    if hasattr(person, 'alumni_account'):
        return Response({"error": "Account already exists for this alumni record."}, status=400)

    if not person.email:
        person.email = email
        person.save()

    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=person.first_name or "",
        last_name=person.sir_name or "",
        is_alumni=True,
        gender=person.gender or gender  # Use provided gender if record lacks it
    )

    AlumniAccount.objects.create(user=user, person=person)

    login(request, user)

    return Response({
        "status": "account_created", 
        "user_id": user.id,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser
    })

@extend_schema(
    tags=['Auth & Onboarding'],
    request=SignupRequestSerializer, 
    responses={201: SignupRequestSerializer},
    description="Explicitly submit a signup request for admin review."
)
@api_view(['POST'])
def submit_signup_request(request):
    """
    Explicitly submit a signup request (optional, can be used by a separate 'Contact Admin' form).
    """
    serializer = SignupRequestSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@extend_schema(
    tags=['Admin - Signup Requests'],
    responses={200: AdminSignupRequestSerializer(many=True)},
    description="List all pending signup requests. Admin only."
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_pending_signup_requests(request):
    """
    List all pending signup requests (Admin only).
    """
    requests = SignupRequest.objects.filter(status='PENDING')
    serializer = AdminSignupRequestSerializer(requests, many=True)
    return Response(serializer.data)

@extend_schema(
    tags=['Admin - Signup Requests'],
    responses={200: dict},
    description="Approve a signup request. Creates User and Person records. Admin only."
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def approve_signup_request(request, pk):
    """
    Approve a signup request and create a User and Person record.
    """
    try:
        signup_request = SignupRequest.objects.get(pk=pk)
    except SignupRequest.DoesNotExist:
        return Response({"error": "Signup request not found."}, status=404)
    
    if signup_request.status != 'PENDING':
        return Response({"error": f"Request is already {signup_request.status}."}, status=400)

    # Create Person record
    person = Person.objects.create(
        full_name=signup_request.full_name,
        email=signup_request.email,
        graduation_year=signup_request.graduation_year,
        phone_primary=signup_request.phone,
        gender=signup_request.gender,
        course_offered=signup_request.course,
        data_source="Signup Request"
    )

    # Create User record (using email as username)
    password = User.objects.make_random_password()
    user = User.objects.create_user(
        username=signup_request.email,
        email=signup_request.email,
        password=password,
        first_name=signup_request.full_name.split(' ')[0] if ' ' in signup_request.full_name else signup_request.full_name,
        is_alumni=True,
        gender=signup_request.gender
    )

    # Link them
    AlumniAccount.objects.create(user=user, person=person)

    signup_request.status = 'APPROVED'
    signup_request.save()

    return Response({
        "status": "approved",
        "user_id": user.id,
        "person_id": person.id,
        "temporary_password": password 
    })

@extend_schema(
    tags=['Admin - Signup Requests'],
    responses={200: dict},
    description="Reject a signup request. Admin only."
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def reject_signup_request(request, pk):
    """
    Reject a signup request.
    """
    try:
        signup_request = SignupRequest.objects.get(pk=pk)
    except SignupRequest.DoesNotExist:
        return Response({"error": "Signup request not found."}, status=404)

    if signup_request.status != 'PENDING':
        return Response({"error": f"Request is already {signup_request.status}."}, status=400)

    signup_request.status = 'REJECTED'
    signup_request.save()

    return Response({"status": "rejected"})

@extend_schema(
    tags=['Admin - User Management'],
    responses={200: dict},
    description="Get total count of registered users and alumni. Admin only."
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def total_signed_up_users(request):
    """
    Get total count of signed up users/alumni.
    """
    total_users = User.objects.count()
    total_alumni_users = User.objects.filter(is_alumni=True).count()
    return Response({
        "total_users": total_users,
        "total_alumni_users": total_alumni_users
    })

@extend_schema(
    tags=['Admin - User Management'],
    request=AdminCreateUserSerializer, 
    responses={201: AdminCreateUserSerializer},
    description="Directly create a new user. Admin only."
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_create_user(request):
    """
    Admin-only API to add new users to the DB.
    """
    serializer = AdminCreateUserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@extend_schema(
    tags=['Auth & Onboarding'],
    request=LoginSerializer, 
    responses={200: dict},
    description="Login a user and return session details."
)
@api_view(['POST'])
def login_user(request):
    """
    Standard Login workflow:
    - returns person_id via AlumniAccount relationship
    """
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({"error": "Email and password are required."}, status=400)

    user = authenticate(request, username=email, password=password)

    if user is not None:
        login(request, user)
        
        # Safely try to get person_id via alumni_profile (AlumniAccount)
        person_id = None
        alumni_profile = getattr(user, 'alumni_profile', None)
        if alumni_profile:
            person_id = alumni_profile.person_id

        return Response({
            "status": "logged_in", 
            "user_id": user.id,
            "person_id": person_id,
            "is_alumni": getattr(user, 'is_alumni', False),
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser
        })
    else:
        return Response({"error": "Invalid email or password."}, status=401)

@extend_schema(
    tags=['Auth & Onboarding'],
    request=PasswordResetSerializer, 
    responses={200: dict},
    description="Initiate password reset process."
)
@api_view(['POST'])
def password_reset(request):
    """
    Step 1: Send password reset email
    """
    email = request.data.get("email")
    if not email:
        return Response({"error": "Email is required."}, status=400)
    
    user = User.objects.filter(email=email).first()
    if user:
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Simple reset link (you can change this to your frontend URL)
        reset_link = f"UID: {uid}, TOKEN: {token}"
        
        subject = "Password Reset Requested"
        message = f"Use the following to reset your password:\n{reset_link}"
        
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)
        except Exception as e:
            # For local dev if email fails, we return it in response for convenience
            return Response({"status": "sent_locally", "uid": uid, "token": token, "info": str(e)})

    return Response({"status": "reset_email_sent_if_exists"})

@extend_schema(
    tags=['Auth & Onboarding'],
    request=PasswordResetConfirmSerializer, 
    responses={200: dict},
    description="Confirm password reset with token."
)
@api_view(['POST'])
def password_reset_confirm(request):
    """
    Step 2: Confirm password reset with token
    """
    uidb64 = request.data.get("uidb64")
    token = request.data.get("token")
    new_password = request.data.get("new_password")
    new_password_again = request.data.get("new_password_again")
    
    if not all([uidb64, token, new_password, new_password_again]):
        return Response({"error": "All fields are required."}, status=400)
    
    if new_password != new_password_again:
        return Response({"error": "Passwords do not match."}, status=400)
        
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.set_password(new_password)
        user.save()
        return Response({"status": "password_reset_success"})
    else:
        return Response({"error": "Invalid reset link or token."}, status=400)
