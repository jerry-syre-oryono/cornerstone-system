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
        self.stats_url = reverse('dashboard_stats')
        self.update_url = reverse('update_profile')

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

    def test_dashboard_stats(self):
        from alumni.models import Person
        Person.objects.create(full_name="Alumni 1", gender='M', employment_status='EMPLOYED')
        Person.objects.create(full_name="Alumni 2", gender='F', employment_status='Student')
        
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_alumni'], 2)
        self.assertEqual(response.data['total_male_alumni'], 1)
        self.assertEqual(response.data['total_female_alumni'], 1)
        self.assertEqual(response.data['total_employed_alumni'], 1)
        self.assertEqual(response.data['total_students_alumni'], 1)

    def test_partial_update_profile(self):
        self.client.force_authenticate(user=self.other_user)
        # Update only one field
        response = self.client.patch(self.update_url, {'phone_number': '123456789'})
        self.assertEqual(response.status_code, 200)
        self.other_user.refresh_from_db()
        self.assertEqual(self.other_user.phone_number, '123456789')
        # Ensure other fields are not wiped
        self.assertEqual(self.other_user.first_name, 'Jane')

        # Test PUT with partial data (should work because we use partial=True in view)
        response = self.client.put(self.update_url, {'nationality': 'Ugandan'})
        self.assertEqual(response.status_code, 200)
        self.other_user.refresh_from_db()
        self.assertEqual(self.other_user.nationality, 'Ugandan')
        self.assertEqual(self.other_user.phone_number, '123456789')
