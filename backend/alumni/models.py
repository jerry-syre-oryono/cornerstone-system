from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=255)
    graduation_year = models.IntegerField()
    email = models.EmailField(null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    phone_primary = models.CharField(max_length=20, null=True, blank=True)
    account_created = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} ({self.graduation_year})"