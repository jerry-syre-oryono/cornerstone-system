"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from onboarding import views as onboarding_views
from alumni import views as alumni_views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Onboarding / Auth
    path('api/onboarding/register/', onboarding_views.register_alumni, name='register_alumni'),
    path('api/onboarding/login/', onboarding_views.login_user, name='login_user'),
    path('api/onboarding/password-reset/', onboarding_views.password_reset, name='password_reset'),
    path('api/onboarding/password-reset-confirm/', onboarding_views.password_reset_confirm, name='password_reset_confirm'),
    
    # Alumni
    path('api/alumni/', alumni_views.list_alumni, name='list_alumni'),
    path('api/alumni/directory/', alumni_views.list_registered_alumni, name='list_registered_alumni'),

    
    # API Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]