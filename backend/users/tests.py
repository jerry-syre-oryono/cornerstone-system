from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User

class UserSearchAndRoleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username="admin@example.com",
            email="admin@example.com",
            password="adminpassword"
        )
        self.client.force_authenticate(user=self.admin_user)
        
        self.other_user = User.objects.create_user(
            username="other@example.com",
            email="other@example.com",
            password="password123",
            first_name="Jane",
            last_name="Doe"
        )
        
        self.search_url = reverse('search_users')

    def test_search_users(self):
        # Search by first name
        response = self.client.get(self.search_url, {'q': 'Jane'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], "other@example.com")

        # Search by email
        response = self.client.get(self.search_url, {'q': 'other@'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_assign_admin_role(self):
        url = reverse('change_user_role', kwargs={'pk': self.other_user.pk})
        response = self.client.post(url, {'role': 'admin'})
        self.assertEqual(response.status_code, 200)
        
        self.other_user.refresh_from_db()
        self.assertTrue(self.other_user.is_staff)
        self.assertTrue(self.other_user.is_superuser)
