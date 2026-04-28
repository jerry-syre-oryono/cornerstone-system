import random
from datetime import timedelta
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.utils import timezone
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .services import find_match
from alumni.models import Person, AlumniAccount
from .models import SignupRequest, PasswordResetOTP

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .serializers import (
    RegisterAlumniSerializer, LoginSerializer, PasswordResetSerializer, 
    PasswordResetConfirmSerializer, SignupRequestSerializer, 
    AdminSignupRequestSerializer, AdminCreateUserSerializer,
    PasswordResetRequestSerializer, PasswordResetVerifyOTPSerializer,
    PasswordResetSetPasswordSerializer
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
    request=None,
    responses={200: OpenApiTypes.OBJECT},
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
    request=None,
    responses={200: OpenApiTypes.OBJECT},
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
    tags=['Admin - Signup Requests'],
    responses={204: None},
    description="Delete a signup request permanently. Admin only."
)
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_signup_request(request, pk):
    """
    Permanently delete a signup request (Admin only).
    """
    try:
        signup_request = SignupRequest.objects.get(pk=pk)
    except SignupRequest.DoesNotExist:
        return Response({"error": "Signup request not found."}, status=404)

    signup_request.delete()
    return Response(status=204)

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
    male_users = User.objects.filter(gender='M').count()
    female_users = User.objects.filter(gender='F').count()
    unspecified_gender = User.objects.filter(gender__isnull=True).count()
    
    return Response({
        "total_users": total_users,
        "total_alumni_users": total_alumni_users,
        "male_users": male_users,
        "female_users": female_users,
        "unspecified_gender": unspecified_gender
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
    tags=['Admin - User Management'],
    request=UserRoleSerializer,
    responses={200: dict},
    description="Promote or demote a user. Admin only."
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def change_user_role(request, pk):
    """
    Change a user's role by setting is_staff and is_superuser.
    """
    try:
        user_to_change = User.objects.get(pk=pk)
        role = request.data.get("role") # 'admin' or 'alumni'

        if role == 'admin':
            user_to_change.is_staff = True
            user_to_change.is_superuser = True
        elif role == 'alumni':
            user_to_change.is_staff = False
            user_to_change.is_superuser = False
        else:
            return Response({"error": "Invalid role. Use 'admin' or 'alumni'."}, status=400)
        
        user_to_change.save()
        return Response({"status": f"User {user_to_change.email} role changed to {role}."})
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=404)

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
    - returns token for Token Authentication
    - returns person_id via AlumniAccount relationship
    """
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({"error": "Email and password are required."}, status=400)

    # Try authenticating with username=email (for alumni)
    user = authenticate(request, username=email, password=password)
    
    # If that fails, try finding a user by email and then authenticating with their username
    if user is None:
        user_obj = User.objects.filter(email=email).first()
        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)

    if user is not None:
        login(request, user)
        
        token, _ = Token.objects.get_or_create(user=user)
        
        # Safely try to get person_id via alumni_profile (AlumniAccount)
        person_id = None
        # Use related_name from AlumniAccount if it exists, otherwise check manually
        alumni_profile = getattr(user, 'alumni_profile', None)
        if alumni_profile:
            person_id = alumni_profile.person_id

        # Automatically determine role based on DB status
        if user.is_superuser or user.is_staff:
            role = "admin"
        else:
            role = "alumni"

        return Response({
            "status": "logged_in", 
            "token": token.key,
            "user_id": user.id,
            "person_id": person_id,
            "role": role,
            "is_alumni": user.is_alumni or bool(person_id),
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "profile_photo": user.profile_photo.url if user.profile_photo else None,
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
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
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

@extend_schema(
    tags=['Auth & Onboarding - OTP Password Reset'],
    request=PasswordResetRequestSerializer,
    responses={200: dict},
    description="Step 1: Request OTP for password reset. An OTP will be sent to the user's email."
)
@api_view(['POST'])
def request_password_reset_otp(request):
    """
    Step 1: Request OTP for password reset.
    Generates a 6-digit OTP and sends it to the user's email.
    """
    email = request.data.get("email")
    if not email:
        return Response({"error": "Email is required."}, status=400)

    user = User.objects.filter(email=email).first()
    if not user:
        return Response({"status": "otp_sent", "message": "If an account with that email exists, an OTP has been sent."})

    otp = str(random.randint(100000, 999999))
    expires_at = timezone.now() + timedelta(minutes=10)

    PasswordResetOTP.objects.filter(email=email).delete()
    PasswordResetOTP.objects.create(
        email=email,
        otp=otp,
        expires_at=expires_at,
        is_used=False,
        is_verified=False
    )

    subject = "Your Password Reset OTP"
    context = {"otp": otp}
    html_message = render_to_string("onboarding/emails/password_reset_otp.html", context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject, 
            plain_message, 
            settings.DEFAULT_FROM_EMAIL, 
            [email], 
            html_message=html_message,
            fail_silently=False
        )
    except Exception as e:
        return Response({
            "status": "otp_sent_dev",
            "otp": otp,
            "message": f"Email service failed. Your OTP is: {otp}",
            "debug_info": str(e)
        })

    return Response({"status": "otp_sent", "message": "If an account with that email exists, an OTP has been sent."})

@extend_schema(
    tags=['Auth & Onboarding - OTP Password Reset'],
    request=PasswordResetVerifyOTPSerializer,
    responses={200: dict},
    description="Step 2: Verify the OTP sent to the user's email."
)
@api_view(['POST'])
def verify_password_reset_otp(request):
    """
    Step 2: Verify the OTP.
    Marks the OTP as verified so it can be used to reset the password.
    """
    email = request.data.get("email")
    otp = request.data.get("otp") or request.data.get("otp_code") # Support both names

    if not email or not otp:
        return Response({"error": "Email and OTP are required."}, status=400)

    otp_record = PasswordResetOTP.objects.filter(
        email=email, 
        otp=otp, 
        is_used=False
    ).order_by('-created_at').first()

    if not otp_record:
        return Response({"error": "Invalid OTP."}, status=400)

    if otp_record.is_verified:
        return Response({"error": "OTP has already been used."}, status=400)

    if timezone.now() > otp_record.expires_at:
        return Response({"error": "OTP has expired. Please request a new one."}, status=400)

    otp_record.is_verified = True
    otp_record.save()

    return Response({
        "status": "otp_verified",
        "message": "OTP verified successfully. You can now set a new password."
    })

@extend_schema(
    tags=['Auth & Onboarding - OTP Password Reset'],
    request=PasswordResetSetPasswordSerializer,
    responses={200: dict},
    description="Step 3: Set a new password using the verified OTP."
)
@api_view(['POST'])
def set_password_with_otp(request):
    """
    Step 3: Set new password using verified OTP.
    Supports both direct reset (if OTP is valid) and standard multi-step flow.
    """
    email = request.data.get("email")
    otp = request.data.get("otp") or request.data.get("otp_code")
    new_password = request.data.get("new_password")
    confirm_password = request.data.get("confirm_password") or request.data.get("new_password_again")

    if not all([email, otp, new_password, confirm_password]):
        return Response({"error": "All fields are required (email, otp/otp_code, new_password, confirm_password)."}, status=400)

    if new_password != confirm_password:
        return Response({"error": "Passwords do not match."}, status=400)

    otp_record = PasswordResetOTP.objects.filter(
        email=email, 
        otp=otp, 
        is_used=False
    ).order_by('-created_at').first()

    if not otp_record:
        return Response({"error": "Invalid OTP."}, status=400)

    # Note: We now allow direct reset if the OTP is valid and not expired, 
    # even if it wasn't pre-verified via the verify endpoint.
    if timezone.now() > otp_record.expires_at:
        return Response({"error": "OTP has expired. Please request a new one."}, status=400)

    user = User.objects.filter(email=email).first()
    if not user:
        return Response({"error": "User not found."}, status=404)

    user.set_password(new_password)
    user.save()

    otp_record.is_used = True
    otp_record.is_verified = True # Mark as verified as well since it worked
    otp_record.save()

    return Response({
        "status": "password_reset_success",
        "message": "Your password has been reset successfully."
    })
