from django.contrib import admin
from .models import Person
from careers.models import Employment
from onboarding.models import LoginToken

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'graduation_year', 'email', 'account_created']
    search_fields = ['full_name', 'email']
    list_filter = ['graduation_year', 'account_created']

admin.site.register(Employment)
admin.site.register(LoginToken)