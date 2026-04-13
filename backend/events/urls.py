from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminEventViewSet, EventListView, rsvp_to_event

router = DefaultRouter()
router.register(r'admin/events', AdminEventViewSet, basename='admin-events')

urlpatterns = [
    path('', include(router.urls)),
    path('user/events/', EventListView.as_view(), name='event-list'),
    path('user/events/<int:event_id>/rsvp/', rsvp_to_event, name='event-rsvp'),
]
