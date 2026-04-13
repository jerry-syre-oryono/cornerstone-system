from django.db import models
from alumni.models import Person
import uuid

class LoginToken(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Token for {self.person.full_name}"

class SignupRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    graduation_year = models.IntegerField()
    phone = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], blank=True, null=True)
    course = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.full_name} ({self.status})"
