from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from onboarding import views as onboarding_views
from alumni import views as alumni_views
from users import views as user_views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Onboarding / Auth
    path('api/onboarding/register/', onboarding_views.register_alumni, name='register_alumni'),
    path('api/onboarding/login/', onboarding_views.login_user, name='login_user'),
    path('api/onboarding/password-reset/', onboarding_views.password_reset, name='password_reset'),
    path('api/onboarding/password-reset-confirm/', onboarding_views.password_reset_confirm, name='password_reset_confirm'),
    
    # OTP Password Reset (New)
    path('api/onboarding/password-reset/request-otp/', onboarding_views.request_password_reset_otp, name='request_password_reset_otp'),
    path('api/onboarding/password-reset/verify-otp/', onboarding_views.verify_password_reset_otp, name='verify_password_reset_otp'),
    path('api/onboarding/password-reset/set-password/', onboarding_views.set_password_with_otp, name='set_password_with_otp'),
    
    # Signup Requests (New)
    path('api/onboarding/signup-request/', onboarding_views.submit_signup_request, name='submit_signup_request'),
    path('api/onboarding/signup-requests/pending/', onboarding_views.list_pending_signup_requests, name='list_pending_signup_requests'),
    path('api/onboarding/signup-requests/<int:pk>/approve/', onboarding_views.approve_signup_request, name='approve_signup_request'),
    path('api/onboarding/signup-requests/<int:pk>/reject/', onboarding_views.reject_signup_request, name='reject_signup_request'),
    path('api/onboarding/signup-requests/<int:pk>/delete/', onboarding_views.delete_signup_request, name='delete_signup_request'),
    
    # User Management (New)
    path('api/users/dashboard-stats/', user_views.dashboard_stats, name='dashboard_stats'),
    path('api/users/total/', onboarding_views.total_signed_up_users, name='total_signed_up_users'),
    path('api/users/create/', onboarding_views.admin_create_user, name='admin_create_user'),
    path('api/users/search/', user_views.search_users, name='search_users'),
    path('api/users/get-role/', onboarding_views.get_user_role, name='get_user_role'),
    path('api/users/admins/', onboarding_views.list_admin_users, name='list_admin_users'),
    path('api/users/<int:pk>/set-role/', onboarding_views.change_user_role, name='change_user_role'),
    path('api/users/me/', user_views.get_my_profile, name='get_my_profile'),
    path('api/users/me/update/', user_views.update_profile, name='update_profile'),

    # Events
    path('api/events/', include('events.urls')),

    # Careers / Opportunities
    path('api/opportunities/', include('careers.urls')),

    # Resources
    path('api/resources/', include('resources.urls')),

    # Alumni
    path('api/alumni/', alumni_views.list_alumni, name='list_alumni'),
    path('api/alumni/add/', alumni_views.add_alumni, name='add_alumni'),
    path('api/alumni/<int:pk>/edit/', alumni_views.edit_alumni, name='edit_alumni'),
    path('api/alumni/<int:pk>/archive/', alumni_views.archive_alumni, name='archive_alumni'),
    path('api/alumni/<int:pk>/unarchive/', alumni_views.unarchive_alumni, name='unarchive_alumni'),
    path('api/alumni/archived/', alumni_views.list_archived_alumni, name='list_archived_alumni'),
    path('api/alumni/directory/', alumni_views.list_registered_alumni, name='list_registered_alumni'),
    path('api/alumni/male/', alumni_views.list_male_alumni, name='list_male_alumni'),
    path('api/alumni/female/', alumni_views.list_female_alumni, name='list_female_alumni'),

    # Users
    path('api/users/male/', user_views.list_male_users, name='list_male_users'),
    path('api/users/female/', user_views.list_female_users, name='list_female_users'),

    # API Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
