from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_resources, name='list_resources'),
    path('upload/', views.upload_resource, name='upload_resource'),
    path('<int:pk>/', views.get_resource, name='get_resource'),
]
