from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Person, AlumniAccount
from users.models import User

class AlumniDirectoryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # 1. Registered alumni
        self.registered_person = Person.objects.create(
            full_name="Registered User",
            graduation_year=2020,
            email="reg@example.com"
        )
        self.user = User.objects.create_user(
            username="reg@example.com",
            email="reg@example.com",
            password="password123"
        )
        AlumniAccount.objects.create(user=self.user, person=self.registered_person)
        
        # 2. Pending alumni (no account)
        self.pending_person = Person.objects.create(
            full_name="Pending User",
            graduation_year=2021
        )
        
        # 3. Admin user
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword"
        )
        
        self.directory_url = reverse('list_registered_alumni')
        self.admin_list_url = reverse('list_alumni')

    def test_directory_requires_auth(self):
        response = self.client.get(self.directory_url)
        self.assertEqual(response.status_code, 403)

    def test_directory_returns_only_registered(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.directory_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['full_name'], "Registered User")

    def test_admin_list_requires_staff(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.admin_list_url)
        self.assertEqual(response.status_code, 403)

    def test_admin_list_returns_all(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.admin_list_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
