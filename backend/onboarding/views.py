from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from .services import find_match
from users.models import User
from alumni.models import Person, AlumniAccount

from drf_spectacular.utils import extend_schema
from .serializers import RegisterAlumniSerializer, LoginSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer

@extend_schema(request=RegisterAlumniSerializer, responses={200: dict})
@api_view(['POST'])
def register_alumni(request):
    """
    Form-based registration workflow:
    - full_name, graduation_year, email, password, password_again
    - Verify password match
    - Find alumni match
    - Create User and AlumniAccount link
    - Set email on Person if missing
    - Login
    """
    full_name = request.data.get("full_name")
    graduation_year = request.data.get("graduation_year")
    email = request.data.get("email")
    password = request.data.get("password")
    password_again = request.data.get("password_again")

    if not all([full_name, graduation_year, email, password, password_again]):
        return Response({"error": "All fields are required."}, status=400)

    if password != password_again:
        return Response({"error": "Passwords do not match."}, status=400)

    person = find_match(full_name, graduation_year)
    if not person:
        return Response({"error": "Alumni record not found. Please verify your name and graduation year."}, status=404)

    if hasattr(person, 'alumni_account'):
        return Response({"error": "Account already exists for this alumni record."}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({"error": "A user with this email already exists."}, status=400)

    if not person.email:
        person.email = email
        person.save()

    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=person.first_name or "",
        last_name=person.sir_name or "",
        is_alumni=True
    )

    AlumniAccount.objects.create(user=user, person=person)

    login(request, user)

    return Response({
        "status": "account_created", 
        "user_id": user.id,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser
    })

@extend_schema(request=LoginSerializer, responses={200: dict})
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
        person_id = None
        if hasattr(user, 'alumni_profile'):
            person_id = user.alumni_profile.person.id

        return Response({
            "status": "logged_in", 
            "user_id": user.id,
            "person_id": person_id,
            "is_alumni": user.is_alumni,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser
        })
    else:
        return Response({"error": "Invalid email or password."}, status=401)

@extend_schema(request=PasswordResetSerializer, responses={200: dict})
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

@extend_schema(request=PasswordResetConfirmSerializer, responses={200: dict})
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