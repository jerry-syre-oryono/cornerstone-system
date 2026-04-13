from django.contrib import admin
from .models import LoginToken, SignupRequest

@admin.register(LoginToken)
class LoginTokenAdmin(admin.ModelAdmin):
    list_display = ('person', 'token', 'created_at', 'expires_at')
    search_fields = ('person__full_name', 'token')

@admin.register(SignupRequest)
class SignupRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'graduation_year', 'status', 'created_at')
    list_filter = ('status', 'graduation_year')
    search_fields = ('full_name', 'email')
    readonly_fields = ('created_at', 'updated_at')
