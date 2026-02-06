from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase

from gymapp.models import Profile, Program, WorkoutTemplate, Session, Booking, FunctionalWOD, Lead


class BookingWorkoutLinkTests(APITestCase):
    def setUp(self):
        self.coach = User.objects.create_user("coach", password="pass1234")
        Profile.objects.create(user=self.coach, role="coach")
        self.member = User.objects.create_user("member", password="pass1234")
        Profile.objects.create(user=self.member, role="member")
        self.program = Program.objects.create(name="SGPT Strength")
        WorkoutTemplate.objects.create(program=self.program, title="Day A", content={"exercise": "Deadlift"})
        now = timezone.now()
        self.sgpt = Session.objects.create(session_type="sgpt", room="sgpt_room", title="SGPT", coach=self.coach, start_time=now, end_time=now + timedelta(hours=1), capacity=5)

    def test_booking_generates_workout_instance(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.post("/api/bookings/", {"member": self.member.id, "session": self.sgpt.id, "status": "booked"})
        self.assertEqual(response.status_code, 201)
        booking = Booking.objects.get(id=response.data["id"])
        self.assertTrue(hasattr(booking, "workout_instance"))


class ScreenTests(APITestCase):
    def setUp(self):
        coach = User.objects.create_user("coach2", password="pass1234")
        Profile.objects.create(user=coach, role="coach")
        member = User.objects.create_user("member2", password="pass1234")
        Profile.objects.create(user=member, role="member")
        now = timezone.now()
        self.fn_session = Session.objects.create(session_type="functional", room="functional_room", title="Fn", coach=coach, start_time=now - timedelta(minutes=5), end_time=now + timedelta(minutes=55), capacity=12)
        FunctionalWOD.objects.create(session=self.fn_session, workout={"wod": "AMRAP 15"})
        Booking.objects.create(member=member, session=self.fn_session, status="booked")

    def test_functional_screen(self):
        response = self.client.get("/api/screens/functional/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("wod", response.data)


class LeadWorkflowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("admin", password="pass1234")
        Profile.objects.create(user=self.user, role="admin")
        self.client.force_authenticate(user=self.user)

    def test_deduplicates_by_email(self):
        Lead.objects.create(full_name="A", email="a@mail.com")
        self.client.force_authenticate(user=None)
        response = self.client.post("/api/integrations/leads/webhook/", {"email": "a@mail.com", "name": "New"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Lead.objects.filter(email="a@mail.com").count(), 1)

    def test_convert_lead(self):
        self.client.force_authenticate(user=self.user)
        lead = Lead.objects.create(full_name="Lead User", email="lead@x.com", stage="new")
        res = self.client.post(f"/api/leads/{lead.id}/convert/")
        self.assertEqual(res.status_code, 200)
        lead.refresh_from_db()
        self.assertEqual(lead.stage, "converted")
        self.assertIsNotNone(lead.converted_member)

    def test_metrics_endpoint(self):
        Lead.objects.create(full_name="L1", source="Meta", stage="new")
        Lead.objects.create(full_name="L2", source="Meta", stage="converted")
        response = self.client.get("/api/metrics/conversion/?days=30&source=Meta")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_prospects"], 2)


class MobilityTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user("adminmob", password="pass1234")
        Profile.objects.create(user=self.admin, role="admin")
        self.member = User.objects.create_user("membermob", password="pass1234")
        Profile.objects.create(user=self.member, role="member")
        self.client.force_authenticate(user=self.admin)

    def test_generate_mobility_plan(self):
        # seed minimal library
        self.client.post("/api/mobility/exercises/", {"name": "90/90 Hip Flow", "category": "hip", "level": "beginner"})
        self.client.post("/api/mobility/exercises/", {"name": "Wall Slide", "category": "shoulder", "level": "beginner"})
        self.client.post("/api/mobility/exercises/", {"name": "Knee to Wall", "category": "ankle", "level": "beginner"})

        assessment = self.client.post("/api/mobility/assessments/", {
            "member": self.member.id,
            "assessed_on": "2026-01-01",
            "ankle_left_score": 1,
            "ankle_right_score": 2,
            "aslr_left_score": 2,
            "aslr_right_score": 2,
            "shoulder_left_score": 2,
            "shoulder_right_score": 3,
            "overhead_squat_score": 2,
            "wall_angels_score": 2,
        }, format="json")
        self.assertEqual(assessment.status_code, 201)
        aid = assessment.data["id"]

        response = self.client.post(f"/api/mobility/assessments/{aid}/generate-plan/")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(len(response.data.get("items", [])) >= 1)

        latest = self.client.get(f"/api/mobility/members/{self.member.id}/latest/")
        self.assertEqual(latest.status_code, 200)
        self.assertIsNotNone(latest.data["assessment"])
