from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Profile(TimeStampedModel):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        COACH = "coach", "Coach"
        RECEPTION = "reception", "Reception"
        MEMBER = "member", "Member"
        PRACTITIONER = "practitioner", "Practitioner"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=Role.choices)
    phone = models.CharField(max_length=30, blank=True)


class MemberProfile(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="member_profile")
    waiver_signed = models.BooleanField(default=False)
    parq_flag = models.BooleanField(default=False)
    emergency_contact = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)


class MembershipPackage(TimeStampedModel):
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    billing_cycle = models.CharField(max_length=20, choices=[("monthly", "Monthly"), ("weekly", "Weekly")])
    included_credits = models.PositiveIntegerField(null=True, blank=True)
    unlimited_classes = models.BooleanField(default=False)
    freeze_rules = models.TextField(blank=True)
    cancellation_terms = models.TextField(blank=True)


class ProductAddon(TimeStampedModel):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)


class PackageAddon(TimeStampedModel):
    package = models.ForeignKey(MembershipPackage, on_delete=models.CASCADE, related_name="addons")
    addon = models.ForeignKey(ProductAddon, on_delete=models.CASCADE)


class Membership(TimeStampedModel):
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    package = models.ForeignKey(MembershipPackage, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)


class Program(TimeStampedModel):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)


class WorkoutTemplate(TimeStampedModel):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="workouts")
    week = models.PositiveIntegerField(default=1)
    day = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=120)
    content = models.JSONField(default=dict)


class Session(TimeStampedModel):
    class SessionType(models.TextChoices):
        SGPT = "sgpt", "SGPT"
        FUNCTIONAL = "functional", "Functional Fitness"
        TREATMENT = "treatment", "Treatment"

    class Room(models.TextChoices):
        SGPT_ROOM = "sgpt_room", "SGPT Room"
        FUNCTIONAL_ROOM = "functional_room", "Functional Room"
        TREATMENT_ROOM = "treatment_room", "Treatment Room"

    session_type = models.CharField(max_length=20, choices=SessionType.choices)
    room = models.CharField(max_length=30, choices=Room.choices)
    title = models.CharField(max_length=120)
    coach = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="coaching_sessions")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.PositiveIntegerField(default=1)
    recurrence_rule = models.CharField(max_length=120, blank=True)


class FunctionalWOD(TimeStampedModel):
    session = models.OneToOneField(Session, on_delete=models.CASCADE, related_name="functional_wod")
    workout = models.JSONField(default=dict)


class Booking(TimeStampedModel):
    class Status(models.TextChoices):
        BOOKED = "booked", "Booked"
        WAITLIST = "waitlist", "Waitlist"
        CANCELED = "canceled", "Canceled"
        CHECKED_IN = "checked_in", "Checked In"

    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="bookings")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.BOOKED)

    class Meta:
        unique_together = ("member", "session")


class WorkoutInstance(TimeStampedModel):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="workout_instance")
    snapshot = models.JSONField(default=dict)


class WorkoutLog(TimeStampedModel):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="logs")
    exercise = models.CharField(max_length=120)
    sets = models.PositiveIntegerField()
    reps = models.PositiveIntegerField()
    load = models.FloatField(default=0)
    rpe = models.FloatField(default=0)
    notes = models.TextField(blank=True)


class TreatmentType(TimeStampedModel):
    name = models.CharField(max_length=120)
    duration_minutes = models.PositiveIntegerField(default=60)
    price = models.DecimalField(max_digits=10, decimal_places=2)


class TreatmentBooking(TimeStampedModel):
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="treatment_bookings")
    practitioner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="practitioner_bookings")
    treatment_type = models.ForeignKey(TreatmentType, on_delete=models.PROTECT)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    consent_checked = models.BooleanField(default=False)
    notes = models.TextField(blank=True)


class FinanceEntry(TimeStampedModel):
    class Kind(models.TextChoices):
        INCOME = "income", "Income"
        EXPENSE = "expense", "Expense"

    service_line = models.CharField(max_length=30, choices=[("sgpt", "SGPT"), ("functional", "Functional"), ("treatments", "Treatments"), ("retail", "Retail")])
    kind = models.CharField(max_length=20, choices=Kind.choices)
    category = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=60, blank=True)
    vat_included = models.BooleanField(default=False)
    tags = models.CharField(max_length=240, blank=True)
    attachment_url = models.URLField(blank=True)


class Lead(TimeStampedModel):
    class Stage(models.TextChoices):
        NEW = "new", "New Lead"
        CONTACTED = "contacted", "Contacted"
        BOOKED_CONSULTATION = "booked_consultation", "Booked Consultation"
        ATTENDED = "attended", "Attended"
        TRIAL_STARTED = "trial_started", "Trial Started"
        CONVERTED = "converted", "Converted"
        ACTIVE_MEMBER = "active_member", "Active Member"
        AT_RISK = "at_risk", "At Risk"
        CHURNED = "churned", "Churned"

    full_name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    stage = models.CharField(max_length=30, choices=Stage.choices, default=Stage.NEW)
    source = models.CharField(max_length=120, blank=True)
    campaign = models.CharField(max_length=120, blank=True)
    adset = models.CharField(max_length=120, blank=True)
    ad = models.CharField(max_length=120, blank=True)
    utm_source = models.CharField(max_length=120, blank=True)
    utm_medium = models.CharField(max_length=120, blank=True)
    utm_campaign = models.CharField(max_length=120, blank=True)
    click_id = models.CharField(max_length=180, blank=True)
    expected_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    probability = models.PositiveIntegerField(default=0)
    won_at = models.DateTimeField(null=True, blank=True)
    converted_member = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="converted_from_leads")
    lost_reason = models.CharField(max_length=240, blank=True)
    notes = models.TextField(blank=True)


class LeadActivity(TimeStampedModel):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="activities")
    activity_type = models.CharField(max_length=40)
    content = models.TextField(blank=True)
    next_action_date = models.DateField(null=True, blank=True)


class LeadTask(TimeStampedModel):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=120)
    due_date = models.DateField()
    completed = models.BooleanField(default=False)


class LeadIntegrationEvent(TimeStampedModel):
    provider = models.CharField(max_length=60, default="generic")
    raw_payload = models.JSONField(default=dict)
    mapped_email = models.EmailField(blank=True)
    mapped_phone = models.CharField(max_length=30, blank=True)


class ConversionEvent(TimeStampedModel):
    event_type = models.CharField(max_length=60)
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)
    metadata = models.JSONField(default=dict)


class OverheadConfig(TimeStampedModel):
    method = models.CharField(max_length=30, choices=[("per_active_member", "Per Active Member"), ("revenue_share", "Revenue Share")], default="per_active_member")
    monthly_overhead = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class OfflineConversionConnector(TimeStampedModel):
    provider = models.CharField(max_length=40)
    enabled = models.BooleanField(default=False)
    config = models.JSONField(default=dict)


class ConnectorRun(TimeStampedModel):
    connector = models.ForeignKey(OfflineConversionConnector, on_delete=models.CASCADE, related_name="runs")
    status = models.CharField(max_length=20, default="stubbed")
    response = models.JSONField(default=dict)
