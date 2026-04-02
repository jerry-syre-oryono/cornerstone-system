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

class LoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.person = Person.objects.create(
            full_name="Jane Smith",
            first_name="Jane",
            sir_name="Smith",
            graduation_year=2020,
            email="jane@example.com"
        )
        self.user = User.objects.create_user(
            username="jane@example.com",
            email="jane@example.com",
            password="password123",
            is_alumni=True
        )
        AlumniAccount.objects.create(user=self.user, person=self.person)
        self.url = reverse('login_user')

    def test_successful_login(self):
        data = {
            "email": "jane@example.com",
            "password": "password123"
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], "logged_in")
        self.assertEqual(response.data['person_id'], self.person.id)
        self.assertEqual(response.data['user_id'], self.user.id)

    def test_invalid_credentials(self):
        data = {
            "email": "jane@example.com",
            "password": "wrongpassword"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid email or password", response.data['error'])

    def test_login_user_without_profile(self):
        # Create a user without an alumni profile (e.g. a staff user)
        staff_user = User.objects.create_user(
            username="staff@example.com",
            email="staff@example.com",
            password="password123",
            is_staff=True,
            is_alumni=False
        )
        data = {
            "email": "staff@example.com",
            "password": "password123"
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], "logged_in")
        self.assertIsNone(response.data['person_id'])
        self.assertFalse(response.data['is_alumni'])


