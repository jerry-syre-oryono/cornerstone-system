from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    is_alumni = models.BooleanField(default=False)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)

    # Interface 1: Alumni Details
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    marital_status = models.CharField(max_length=20, choices=[('Single', 'Single'), ('Married', 'Married')], default='Single')
    
    # Spouse Details (visible if married)
    spouse_full_name = models.CharField(max_length=255, null=True, blank=True)
    spouse_phone = models.CharField(max_length=20, null=True, blank=True)
    spouse_email = models.EmailField(null=True, blank=True)
    spouse_occupation = models.CharField(max_length=255, null=True, blank=True)

    # Interface 2: Qualifications
    cla_campus = models.CharField(max_length=20, choices=[('CLA Boys', 'CLA Boys'), ('CLA Girls', 'CLA Girls')], null=True, blank=True)
    high_school_graduation_year = models.IntegerField(null=True, blank=True)
    
    ACADEMIC_STATUS_CHOICES = [
        ('University Graduate', 'University Graduate'),
        ('Still at University', 'Still at University'),
        ('Not Enrolled', 'Not Enrolled'),
    ]
    academic_status = models.CharField(max_length=50, choices=ACADEMIC_STATUS_CHOICES, null=True, blank=True)
    
    university_institution = models.CharField(max_length=255, null=True, blank=True)
    university_course = models.CharField(max_length=255, null=True, blank=True)
    university_graduation_year = models.IntegerField(null=True, blank=True)
    expected_graduation_year = models.IntegerField(null=True, blank=True)

    # Interface 3: Address Details
    address_country = models.CharField(max_length=100, null=True, blank=True)
    address_district_region = models.CharField(max_length=100, null=True, blank=True)
    address_city_town = models.CharField(max_length=100, null=True, blank=True)
    address_po_box = models.CharField(max_length=100, null=True, blank=True)
    address_physical_street = models.TextField(null=True, blank=True)

    # Interface 4: Work & Employment
    EMPLOYMENT_STATUS_CHOICES = [
        ('Employed', 'Employed'),
        ('Self-Employed', 'Self-Employed'),
        ('Unemployed', 'Unemployed'),
        ('Still a Student', 'Still a Student'),
    ]
    employment_status = models.CharField(max_length=50, choices=EMPLOYMENT_STATUS_CHOICES, null=True, blank=True)
    
    # Common Work Details (for Employed and Self-Employed)
    employer_company_name = models.CharField(max_length=255, null=True, blank=True)
    job_title_role = models.CharField(max_length=255, null=True, blank=True)
    industry_sector = models.CharField(max_length=100, null=True, blank=True)
    work_location = models.CharField(max_length=255, null=True, blank=True)
    work_year_started = models.IntegerField(null=True, blank=True)
    work_email = models.EmailField(null=True, blank=True)
    work_phone = models.CharField(max_length=20, null=True, blank=True)
    linkedin_profile = models.URLField(max_length=500, null=True, blank=True)