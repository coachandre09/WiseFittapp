from datetime import timedelta
from random import randint, choice
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from gymapp.models import (
    Profile, MemberProfile, MembershipPackage, Membership, Program, WorkoutTemplate,
    Session, FunctionalWOD, Booking, WorkoutInstance, TreatmentType, TreatmentBooking,
    FinanceEntry, Lead
)


class Command(BaseCommand):
    help = "Seed demo data for WiseFitt"

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(username="admin", defaults={"email": "admin@wisefitt.com"})
        admin.set_password("admin1234")
        admin.save()
        Profile.objects.get_or_create(user=admin, defaults={"role": "admin"})

        coaches = []
        for i in range(2):
            u, _ = User.objects.get_or_create(username=f"coach{i+1}")
            u.set_password("pass1234")
            u.save()
            Profile.objects.get_or_create(user=u, defaults={"role": "coach"})
            coaches.append(u)

        practitioners = []
        for i in range(2):
            u, _ = User.objects.get_or_create(username=f"practitioner{i+1}")
            u.set_password("pass1234")
            u.save()
            Profile.objects.get_or_create(user=u, defaults={"role": "practitioner"})
            practitioners.append(u)

        members = []
        for i in range(20):
            u, _ = User.objects.get_or_create(username=f"member{i+1}", defaults={"email": f"member{i+1}@mail.com"})
            u.set_password("pass1234")
            u.save()
            Profile.objects.get_or_create(user=u, defaults={"role": "member"})
            MemberProfile.objects.get_or_create(user=u, defaults={"waiver_signed": True})
            members.append(u)

        pkg, _ = MembershipPackage.objects.get_or_create(name="Premium Unlimited", defaults={"price": 189, "billing_cycle": "monthly", "unlimited_classes": True})
        for m in members:
            Membership.objects.get_or_create(member=m, package=pkg, start_date=timezone.now().date())

        program, _ = Program.objects.get_or_create(name="SGPT Base Program")
        wt, _ = WorkoutTemplate.objects.get_or_create(program=program, week=1, day=1, title="Lower Body Strength", defaults={"content": {"blocks": [{"exercise": "Back Squat", "sets": 5, "reps": 5}]}})

        now = timezone.now().replace(hour=6, minute=0, second=0, microsecond=0)
        sessions = []
        for d in range(7):
            sgpt = Session.objects.create(session_type="sgpt", room="sgpt_room", title=f"SGPT Day {d+1}", coach=coaches[d % 2], start_time=now + timedelta(days=d), end_time=now + timedelta(days=d, hours=1), capacity=5)
            fn = Session.objects.create(session_type="functional", room="functional_room", title=f"Functional Day {d+1}", coach=coaches[d % 2], start_time=now + timedelta(days=d, hours=1), end_time=now + timedelta(days=d, hours=2), capacity=12)
            FunctionalWOD.objects.create(session=fn, workout={"warmup": "500m row", "wod": "21-15-9 thrusters/pullups"})
            sessions.extend([sgpt, fn])

        for i, m in enumerate(members[:10]):
            booking, _ = Booking.objects.get_or_create(member=m, session=sessions[i % len(sessions)], defaults={"status": "booked"})
            if booking.session.session_type == "sgpt":
                WorkoutInstance.objects.get_or_create(booking=booking, defaults={"snapshot": wt.content})

        treatment, _ = TreatmentType.objects.get_or_create(name="Massage", duration_minutes=60, defaults={"price": 90})
        TreatmentBooking.objects.get_or_create(member=members[0], practitioner=practitioners[0], treatment_type=treatment, start_time=now, end_time=now + timedelta(hours=1), consent_checked=True)

        for _ in range(25):
            FinanceEntry.objects.create(service_line=choice(["sgpt", "functional", "treatments", "retail"]), kind="income", category="Sales", amount=randint(30, 300))
        for _ in range(25):
            FinanceEntry.objects.create(service_line=choice(["sgpt", "functional", "treatments", "retail"]), kind="expense", category="Costs", amount=randint(10, 120))

        for i in range(50):
            Lead.objects.get_or_create(full_name=f"Lead {i+1}", defaults={"email": f"lead{i+1}@mail.com", "phone": f"+9715000{i:03d}", "source": "Meta Ads"})

        self.stdout.write(self.style.SUCCESS("Seed data created."))
