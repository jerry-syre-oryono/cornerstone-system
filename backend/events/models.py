from django.db import models
from django.conf import settings

class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('Fellowship', 'Fellowship'),
        ('Social', 'Social'),
        ('Career', 'Career'),
        ('Reunion', 'Reunion'),
        ('Workshop', 'Workshop'),
        ('Other', 'Other'),
    ]

    title = models.CharField(max_length=255)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    capacity = models.PositiveIntegerField()
    location = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    
    # RSVP system
    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='rsvp_events', 
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    @property
    def rsvp_count(self):
        return self.attendees.count()

    @property
    def is_full(self):
        return self.attendees.count() >= self.capacity
