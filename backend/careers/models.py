from django.db import models
from alumni.models import Person

class Employment(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    sector = models.CharField(max_length=100)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)