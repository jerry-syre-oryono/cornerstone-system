from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from alumni.models import Person, AlumniAccount
from users.models import User

class RegistrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.person = Person.objects.create(
            full_name="John Doe",
            first_name="John",
            sir_name="Doe",
            graduation_year=2021,
            email=None
        )
        self.url = reverse('register_alumni')

    def test_successful_registration(self):
        data = {
            "full_name": "John Doe",
            "graduation_year": 2021,
            "email": "john@example.com",
            "password": "password123",
            "password_again": "password123"
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], "account_created")
        
        # Verify User was created
        user = User.objects.get(email="john@example.com")
        self.assertTrue(user.is_alumni)
        
        # Verify AlumniAccount link
        account = AlumniAccount.objects.get(user=user)
        self.assertEqual(account.person, self.person)
        
        # Verify Person email was updated
        self.person.refresh_from_db()
        self.assertEqual(self.person.email, "john@example.com")

    def test_duplicate_registration_fails(self):
        # Create an account first
        user = User.objects.create_user(username="old@ex.com", email="old@ex.com", password="pw")
        AlumniAccount.objects.create(user=user, person=self.person)
        
        data = {
            "full_name": "John Doe",
            "graduation_year": 2021,
            "email": "new@example.com",
            "password": "password123",
            "password_again": "password123"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Account already exists", response.data['error'])
