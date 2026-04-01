from django.contrib import admin
from .models import Person, AlumniAccount

@admin.register(AlumniAccount)
class AlumniAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'person', 'created_at']
    search_fields = ['user__email', 'person__full_name', 'person__first_name']

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'graduation_year', 'home_district', 'email', 'phone_primary', 'data_source']
    list_filter = ['graduation_year', 'home_district', 'employment_status', 'data_source']
    search_fields = ['full_name', 'first_name', 'sir_name', 'email', 'home_district', 'place_of_work']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('full_name', 'first_name', 'sir_name', 'marital_status', 'data_source')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_primary', 'phone_secondary')
        }),
        ('Academic Information', {
            'fields': ('graduation_year', 'course_offered')
        }),
        ('Location', {
            'fields': ('home_district', 'district_of_residence', 'village_residence')
        }),
        ('Employment', {
            'fields': ('employment_status', 'sector_of_work', 'area_of_work', 'place_of_work', 'position_at_workplace')
        }),
        ('Other', {
            'fields': ('field_of_interest', 'best_communication_channel', 'title_roles')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )