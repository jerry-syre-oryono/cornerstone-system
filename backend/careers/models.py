from django.db import models
from alumni.models import Person
from django.conf import settings

class Employment(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    sector = models.CharField(max_length=100)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

class Opportunity(models.Model):
    TYPE_CHOICES = [
        ('Job', 'Job'),
        ('Scholarship', 'Scholarship'),
        ('Internship', 'Internship'),
        ('Fellowship', 'Fellowship'),
    ]

    title = models.CharField(max_length=255)
    organisation = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    deadline = models.DateField()
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    requirements = models.TextField(blank=True, null=True)
    application_link = models.URLField(blank=True, null=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='posted_opportunities')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Opportunities"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} at {self.organisation}"