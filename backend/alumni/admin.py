from django.contrib import admin
from .models import Person

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'first_name',
        'sir_name',
        'graduation_year',
        'email',
        'phone_primary',
        'employment_status',
        'sector_of_work',
        'home_district',
    ]
    
    list_filter = [
        'graduation_year',
        'employment_status',
        'marital_status',
        'sector_of_work',
        'home_district',
    ]
    
    search_fields = [
        'full_name',
        'first_name',
        'sir_name',
        'names',
        'email',
        'phone_primary',
        'home_district',
        'place_of_work',
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('index_number', 'names', 'first_name', 'sir_name', 'full_name', 'marital_status')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_primary', 'phone_secondary')
        }),
        ('Academic Information', {
            'fields': ('graduation_year', 'course_offered')
        }),
        ('Location Information', {
            'fields': ('home_district', 'district_of_residence', 'village_residence')
        }),
        ('Employment Information', {
            'fields': ('employment_status', 'sector_of_work', 'area_of_work', 'place_of_work', 'position_at_workplace')
        }),
        ('Other Information', {
            'fields': ('field_of_interest', 'best_communication_channel', 'title_roles')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )