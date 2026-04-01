from django.db import models

class Person(models.Model):
    # Basic Information
    index_number = models.CharField(max_length=50, blank=True, null=True)
    names = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    sir_name = models.CharField(max_length=100, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    
    # Academic Information
    graduation_year = models.IntegerField(blank=True, null=True)
    course_offered = models.TextField(blank=True, null=True, verbose_name="Course offered at University")
    
    # Location Information
    home_district = models.CharField(max_length=100, blank=True, null=True)
    district_of_residence = models.CharField(max_length=100, blank=True, null=True)
    village_residence = models.CharField(max_length=255, blank=True, null=True, verbose_name="Village/ward of residence")
    
    # Contact Information
    email = models.EmailField(blank=True, null=True)
    phone_primary = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tell 1 (MTN)")
    phone_secondary = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tell 2 (Airtel/UTL)")
    
    # Employment Information
    employment_status = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('EMPLOYED', 'Employed'),
        ('UNEMPLOYED', 'Unemployed'),
        ('NOT SURE', 'Not Sure'),
        ('DECEASED', 'Deceased'),
    ])
    sector_of_work = models.CharField(max_length=100, blank=True, null=True)
    area_of_work = models.CharField(max_length=255, blank=True, null=True)
    place_of_work = models.CharField(max_length=255, blank=True, null=True)
    position_at_workplace = models.CharField(max_length=255, blank=True, null=True)
    
    # Personal Information
    marital_status = models.CharField(max_length=50, blank=True, null=True)
    field_of_interest = models.TextField(blank=True, null=True)
    best_communication_channel = models.CharField(max_length=255, blank=True, null=True)
    title_roles = models.TextField(blank=True, null=True, verbose_name="Title/Roles")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "People"
        ordering = ['graduation_year', 'first_name']
    
    def __str__(self):
        return self.full_name or f"{self.first_name} {self.sir_name}" or self.names or "Unnamed"