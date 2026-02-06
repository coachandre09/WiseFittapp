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
        self.sgpt = Session.objects.create(session_type="sgpt", room="sgpt_room", title="SGPT", coach=self.coach, start_time=now, end_time=now + timezone.timedelta(hours=1), capacity=5)

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
        self.fn_session = Session.objects.create(session_type="functional", room="functional_room", title="Fn", coach=coach, start_time=now - timezone.timedelta(minutes=5), end_time=now + timezone.timedelta(minutes=55), capacity=12)
        FunctionalWOD.objects.create(session=self.fn_session, workout={"wod": "AMRAP 15"})
        Booking.objects.create(member=member, session=self.fn_session, status="booked")

    def test_functional_screen(self):
        response = self.client.get("/api/screens/functional/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("wod", response.data)


class LeadWebhookTests(APITestCase):
    def test_deduplicates_by_email(self):
        Lead.objects.create(full_name="A", email="a@mail.com")
        response = self.client.post("/api/integrations/leads/webhook/", {"email": "a@mail.com", "name": "New"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Lead.objects.filter(email="a@mail.com").count(), 1)
