from django.db import models
from django.conf import settings

class Resource(models.Model):
    CATEGORY_CHOICES = [
        ('Document', 'Document'),
        ('Guide', 'Guide'),
        ('Link', 'Link'),
        ('Handbook', 'Handbook'),
        ('Other', 'Other'),
    ]

    FILE_TYPE_CHOICES = [
        ('PDF', 'PDF'),
        ('Word', 'Word'),
        ('Excel', 'Excel'),
        ('Link', 'Link'),
        ('Image', 'Image'),
    ]

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    file_url = models.URLField(max_length=500)
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='uploaded_resources')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
