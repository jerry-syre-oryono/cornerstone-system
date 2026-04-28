from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_opportunities, name='list_opportunities'),
    path('create/', views.create_opportunity, name='create_opportunity'),
    path('<int:pk>/', views.get_opportunity, name='get_opportunity'),
]
