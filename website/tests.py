import datetime
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from .models import (
    Department, Programme, AdmissionInfo, FeeInfo,
    Announcement, Event, KnowledgeDocument
)

class WebsiteAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create sample department and programme
        self.dept = Department.objects.create(
            name="Test Computer Science",
            description="Testing computer science department",
            head_name="Prof. Test Head"
        )
        self.dept2 = Department.objects.create(
            name="Test Management",
            description="Testing management department",
            head_name="Prof. Business Head"
        )

        self.prog_ug = Programme.objects.create(
            department=self.dept,
            name="B.Tech in Artificial Intelligence",
            level="UG",
            duration="4 Years",
            eligibility="10+2 with 60%",
            description="AI engineering",
            is_active=True
        )
        self.prog_pg = Programme.objects.create(
            department=self.dept2,
            name="MBA in Finance",
            level="PG",
            duration="2 Years",
            eligibility="Graduation with 50%",
            description="Finance MBA",
            is_active=True
        )

        # Create FeeInfo
        self.fee = FeeInfo.objects.create(
            programme=self.prog_ug,
            fee_type="Tuition Fee",
            amount=150000.00,
            currency="INR",
            notes="Annual tuition"
        )

        # Create AdmissionInfo
        self.adm_faq = AdmissionInfo.objects.create(
            category="faq",
            title="How to apply?",
            content="Apply via the online admissions portal.",
            display_order=1
        )
        self.adm_proc = AdmissionInfo.objects.create(
            category="procedure",
            title="Step 1",
            content="Submit online application.",
            display_order=2
        )

        # Create Announcement
        self.announcement = Announcement.objects.create(
            title="Admissions 2026 Open",
            body="Applications live now.",
            category="Admission",
            published_at=timezone.now(),
            is_published=True
        )

        # Create Event
        self.event = Event.objects.create(
            title="Annual Tech Symposium 2026",
            description="Annual technical symposium",
            venue="Main Auditorium",
            start_datetime=timezone.now() + datetime.timedelta(days=10),
            end_datetime=timezone.now() + datetime.timedelta(days=12)
        )

        # Create KnowledgeDocument
        self.doc = KnowledgeDocument.objects.create(
            topic="hostel",
            title="Hostel Accommodation",
            content="Twin sharing rooms with mess facility.",
            keywords="hostel, room, mess",
            is_active=True
        )

    def test_health_check_endpoint(self):
        url = reverse('health-check')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"status": "ok"})

    def test_home_summary_endpoint(self):
        url = reverse('home-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("statistics", response.data)
        self.assertIn("featured_programmes", response.data)
        self.assertIn("latest_announcements", response.data)
        self.assertIn("upcoming_events", response.data)
        self.assertIn("departments", response.data)
        self.assertEqual(response.data["statistics"]["naac_rating"], "NAAC A+")

    def test_departments_list(self):
        url = reverse('department-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], "Test Computer Science")

    def test_programmes_list_and_filtering(self):
        url = reverse('programme-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Filter by level UG
        response_ug = self.client.get(url, {'level': 'UG'})
        self.assertEqual(response_ug.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_ug.data), 1)
        self.assertEqual(response_ug.data[0]["level"], "UG")

        # Filter by department
        response_dept = self.client.get(url, {'department': str(self.dept.id)})
        self.assertEqual(response_dept.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_dept.data), 1)
        self.assertEqual(response_dept.data[0]["department_name"], "Test Computer Science")

    def test_admissions_grouped(self):
        url = reverse('admissions-grouped')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("faq", response.data)
        self.assertIn("procedure", response.data)
        self.assertEqual(len(response.data["faq"]), 1)
        self.assertEqual(response.data["faq"][0]["title"], "How to apply?")

    def test_announcements_list_and_filter(self):
        url = reverse('announcement-list')
        response = self.client.get(url, {'category': 'Admission'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response_empty = self.client.get(url, {'category': 'Examination'})
        self.assertEqual(response_empty.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_empty.data), 0)

    def test_events_list(self):
        url = reverse('event-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Annual Tech Symposium 2026")

    def test_knowledge_list_and_filter(self):
        url = reverse('knowledge-list')
        response = self.client.get(url, {'topic': 'hostel'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["topic"], "hostel")
