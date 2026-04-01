from django.db import models

class Person(models.Model):
    """Main alumni model - keep existing functionality"""
    # Keep your existing fields
    index_number = models.CharField(max_length=50, blank=True, null=True)
    names = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    sir_name = models.CharField(max_length=100, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    graduation_year = models.IntegerField(blank=True, null=True)
    course_offered = models.TextField(blank=True, null=True)
    home_district = models.CharField(max_length=100, blank=True, null=True)
    district_of_residence = models.CharField(max_length=100, blank=True, null=True)
    village_residence = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_primary = models.CharField(max_length=50, blank=True, null=True)
    phone_secondary = models.CharField(max_length=50, blank=True, null=True)
    employment_status = models.CharField(max_length=50, blank=True, null=True)
    sector_of_work = models.CharField(max_length=100, blank=True, null=True)
    area_of_work = models.CharField(max_length=255, blank=True, null=True)
    place_of_work = models.CharField(max_length=255, blank=True, null=True)
    position_at_workplace = models.CharField(max_length=255, blank=True, null=True)
    marital_status = models.CharField(max_length=50, blank=True, null=True)
    field_of_interest = models.TextField(blank=True, null=True)
    best_communication_channel = models.CharField(max_length=255, blank=True, null=True)
    title_roles = models.TextField(blank=True, null=True)
    data_source = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "People"
        ordering = ['-graduation_year', 'full_name']
    
    def __str__(self):
        return self.full_name or f"{self.first_name} {self.sir_name}" or "Unnamed"

class COSAAlumni(Person):
    """COSA Combined sheet data - inherits from Person"""
    # Person already has all fields, so we just use this as a proxy
    class Meta:
        proxy = True
        verbose_name = "COSA Alumni"
        verbose_name_plural = "COSA Alumni"

class AYLFAlumni(Person):
    """AYLF sheet data - inherits from Person"""
    class Meta:
        proxy = True
        verbose_name = "AYLF Alumni"
        verbose_name_plural = "AYLF Alumni"

class YouthCorpsAlumni(Person):
    """Youth Corps sheet data - inherits from Person"""
    class Meta:
        proxy = True
        verbose_name = "Youth Corps Alumni"
        verbose_name_plural = "Youth Corps Alumni"

class AlumniAccount(models.Model):
    """Link table between User and Person record"""
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='alumni_profile')
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='alumni_account')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Account for {self.person.full_name or self.person.first_name}"