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