from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from .models import Resource

class ResourceTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username="admin@example.com",
            email="admin@example.com",
            password="adminpassword"
        )
        self.client.force_authenticate(user=self.admin_user)
        self.list_url = reverse('list_resources')
        self.upload_url = reverse('upload_resource')

    def test_upload_resource(self):
        data = {
            "title": "CLA Handbook",
            "category": "Handbook",
            "file_type": "PDF",
            "file_url": "https://example.com/handbook.pdf",
            "description": "Important handbook"
        }
        response = self.client.post(self.upload_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Resource.objects.count(), 1)
        self.assertEqual(Resource.objects.first().title, "CLA Handbook")

    def test_list_resources(self):
        Resource.objects.create(
            title="Res 1",
            category="Guide",
            file_type="PDF",
            file_url="https://example.com/1",
            uploaded_by=self.admin_user
        )
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
