from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from .models import LoginToken

def create_login_token(person):
    """Generate 15-minute login token"""
    return LoginToken.objects.create(
        person=person,
        expires_at=timezone.now() + timedelta(minutes=15)
    )

def send_magic_link(email, token):
    """Send magic link email"""
    link = f"http://localhost:5173/login?token={token}"
    
    send_mail(
        "Your Cornerstone Login Link",
        f"Click to login: {link}\n\nThis link expires in 15 minutes.",
        "no-reply@cornerstone.com",
        [email],
        fail_silently=False,
    )