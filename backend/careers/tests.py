from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from .models import Opportunity

class OpportunityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User"
        )
        self.client.force_authenticate(user=self.user)
        
        self.list_url = reverse('list_opportunities')
        self.create_url = reverse('create_opportunity')

    def test_create_opportunity(self):
        data = {
            "title": "Junior Software Engineer",
            "organisation": "Stanbic Bank Uganda",
            "type": "Job",
            "deadline": "2026-12-31",
            "location": "Kampala",
            "description": "Develop awesome things",
            "requirements": "CS Degree",
            "application_link": "https://example.com/apply"
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Opportunity.objects.count(), 1)
        self.assertEqual(Opportunity.objects.first().title, "Junior Software Engineer")
        self.assertEqual(Opportunity.objects.first().posted_by, self.user)

    def test_list_opportunities(self):
        Opportunity.objects.create(
            title="Opp 1",
            organisation="Org 1",
            type="Job",
            deadline="2026-12-31",
            description="Desc 1",
            posted_by=self.user
        )
        Opportunity.objects.create(
            title="Opp 2",
            organisation="Org 2",
            type="Scholarship",
            deadline="2026-12-31",
            description="Desc 2",
            posted_by=self.user
        )
        
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_opportunity_detail(self):
        opp = Opportunity.objects.create(
            title="Detail Opp",
            organisation="Org",
            type="Job",
            deadline="2026-12-31",
            description="Desc",
            posted_by=self.user
        )
        url = reverse('get_opportunity', kwargs={'pk': opp.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Detail Opp")
