from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.contrib.auth import login, authenticate
from django_ratelimit.decorators import ratelimit
from .services import find_match
from users.models import User
from alumni.models import Person

@api_view(['POST'])
@ratelimit(key='ip', rate='10/m')
def register_alumni(request):
    """
    Form-based registration workflow:
    - full_name, graduation_year, email, password, password_again
    - Verify password match
    - Find alumni match
    - Set email if none exists
    - Create user account and login
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
        
    if person.user:
        return Response({"error": "Account already exists for this alumni."}, status=400)
        
    if User.objects.filter(email=email).exists():
        return Response({"error": "A user with this email already exists."}, status=400)
        
    if not person.email:
        person.email = email
        person.save()
        
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=person.first_name,
        last_name=person.last_name,
        is_alumni=True
    )
    
    person.user = user
    person.account_created = True
    person.save()
    
    login(request, user)
    
    return Response({"status": "account_created", "user_id": user.id})

@api_view(['POST'])
@ratelimit(key='ip', rate='10/m')
def login_user(request):
    """
    Standard Login workflow:
    - user provides email and password
    - Authenticates the user
    - Starts the session
    """
    email = request.data.get("email")
    password = request.data.get("password")
    
    if not email or not password:
        return Response({"error": "Email and password are required."}, status=400)
    
    # We must use the username explicitly since our auth backend expects it, 
    # but the username is saved as the email when we create the user.
    user = authenticate(request, username=email, password=password)
    
    if user is not None:
        login(request, user)
        # Check if they are an alumni to return their person_id if helpful
        person_id = None
        if hasattr(user, 'person'):
            person_id = user.person.id
            
        return Response({
            "status": "logged_in", 
            "user_id": user.id,
            "person_id": person_id,
            "is_alumni": user.is_alumni
        })
    else:
        return Response({"error": "Invalid email or password."}, status=401)