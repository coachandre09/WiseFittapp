from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import (
    Profile, MemberProfile, MembershipPackage, ProductAddon, PackageAddon, Membership,
    Program, WorkoutTemplate, Session, FunctionalWOD, Booking, WorkoutInstance, WorkoutLog,
    TreatmentType, TreatmentBooking, FinanceEntry, Lead, LeadActivity, LeadTask,
    LeadIntegrationEvent, ConversionEvent, OverheadConfig, OfflineConversionConnector, ConnectorRun,
    MobilityAssessment, MobilityExercise, MobilityPlan, MobilityPlanItem
)
from .permissions import IsStaffRole, IsAdmin
from .serializers import (
    ProfileSerializer, MembershipPackageSerializer, ProductAddonSerializer, PackageAddonSerializer, MembershipSerializer,
    ProgramSerializer, WorkoutTemplateSerializer, SessionSerializer, FunctionalWODSerializer, BookingSerializer,
    WorkoutInstanceSerializer, WorkoutLogSerializer, TreatmentTypeSerializer, TreatmentBookingSerializer,
    FinanceEntrySerializer, LeadSerializer, LeadActivitySerializer, LeadTaskSerializer,
    ConversionEventSerializer, OverheadConfigSerializer,
    OfflineConversionConnectorSerializer, ConnectorRunSerializer,
    MobilityAssessmentSerializer, MobilityExerciseSerializer, MobilityPlanSerializer, MobilityPlanItemSerializer
)


class DefaultViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]


class ProfileViewSet(DefaultViewSet):
    queryset = Profile.objects.select_related("user").all()
    serializer_class = ProfileSerializer


class MembershipPackageViewSet(DefaultViewSet):
    queryset = MembershipPackage.objects.all()
    serializer_class = MembershipPackageSerializer


class ProductAddonViewSet(DefaultViewSet):
    queryset = ProductAddon.objects.all()
    serializer_class = ProductAddonSerializer


class PackageAddonViewSet(DefaultViewSet):
    queryset = PackageAddon.objects.all()
    serializer_class = PackageAddonSerializer


class MembershipViewSet(DefaultViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer


class ProgramViewSet(DefaultViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer


class WorkoutTemplateViewSet(DefaultViewSet):
    queryset = WorkoutTemplate.objects.all()
    serializer_class = WorkoutTemplateSerializer


class SessionViewSet(DefaultViewSet):
    queryset = Session.objects.all().order_by("start_time")
    serializer_class = SessionSerializer


class FunctionalWODViewSet(DefaultViewSet):
    queryset = FunctionalWOD.objects.all()
    serializer_class = FunctionalWODSerializer


class BookingViewSet(DefaultViewSet):
    queryset = Booking.objects.select_related("session", "member").all()
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        booking = serializer.save()
        session = booking.session
        booked_count = Booking.objects.filter(session=session, status=Booking.Status.BOOKED).count()
        if booked_count > session.capacity:
            booking.status = Booking.Status.WAITLIST
            booking.save(update_fields=["status"])
            return
        if session.session_type == Session.SessionType.SGPT:
            template = WorkoutTemplate.objects.filter(program__name__icontains="sgpt").order_by("week", "day").first()
            snapshot = template.content if template else {"message": "Coach assigns workout"}
            WorkoutInstance.objects.update_or_create(booking=booking, defaults={"snapshot": snapshot})


class WorkoutInstanceViewSet(DefaultViewSet):
    queryset = WorkoutInstance.objects.select_related("booking", "booking__session", "booking__member").all()
    serializer_class = WorkoutInstanceSerializer


class WorkoutLogViewSet(DefaultViewSet):
    queryset = WorkoutLog.objects.all()
    serializer_class = WorkoutLogSerializer


class TreatmentTypeViewSet(DefaultViewSet):
    queryset = TreatmentType.objects.all()
    serializer_class = TreatmentTypeSerializer


class TreatmentBookingViewSet(DefaultViewSet):
    queryset = TreatmentBooking.objects.all()
    serializer_class = TreatmentBookingSerializer


class FinanceEntryViewSet(DefaultViewSet):
    queryset = FinanceEntry.objects.all()
    serializer_class = FinanceEntrySerializer

    @action(detail=False, methods=["get"])
    def dashboard(self, request):
        income = FinanceEntry.objects.filter(kind="income").aggregate(total=Sum("amount"))["total"] or Decimal("0")
        expense = FinanceEntry.objects.filter(kind="expense").aggregate(total=Sum("amount"))["total"] or Decimal("0")
        by_line = list(FinanceEntry.objects.values("service_line", "kind").annotate(total=Sum("amount")))
        members = Membership.objects.filter(is_active=True).values("member").distinct().count()
        arpu = (income / members) if members else Decimal("0")
        churn = Membership.objects.filter(is_active=False).count()
        return Response({
            "income": income,
            "expense": expense,
            "gross_margin": income - expense,
            "by_service_line": by_line,
            "arpu": arpu,
            "churn_count": churn,
        })


class LeadViewSet(DefaultViewSet):
    serializer_class = LeadSerializer

    def get_queryset(self):
        qs = Lead.objects.all().order_by("-created_at")
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(Q(full_name__icontains=q) | Q(email__icontains=q) | Q(phone__icontains=q))
        stages = self.request.query_params.get("stages")
        if stages:
            qs = qs.filter(stage__in=[s.strip() for s in stages.split(",") if s.strip()])
        sources = self.request.query_params.get("sources")
        if sources:
            qs = qs.filter(source__in=[s.strip() for s in sources.split(",") if s.strip()])
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        if start_date:
            qs = qs.filter(created_at__date__gte=start_date)
        if end_date:
            qs = qs.filter(created_at__date__lte=end_date)
        return qs

    @action(detail=True, methods=["post"])
    def convert(self, request, pk=None):
        lead = self.get_object()
        if lead.converted_member_id:
            return Response(self.get_serializer(lead).data)

        email = lead.email or f"lead_{lead.id}@wisefitt.local"
        username = email.split("@")[0]
        base = username
        idx = 1
        while User.objects.filter(username=username).exists():
            idx += 1
            username = f"{base}{idx}"

        user = User.objects.create(username=username, email=lead.email)
        user.first_name = (lead.full_name.split(" ") or [""])[0]
        if " " in lead.full_name:
            user.last_name = " ".join(lead.full_name.split(" ")[1:])
        user.set_unusable_password()
        user.save()

        Profile.objects.get_or_create(user=user, defaults={"role": Profile.Role.MEMBER, "phone": lead.phone})
        MemberProfile.objects.get_or_create(user=user)

        lead.stage = Lead.Stage.CONVERTED
        lead.converted_member = user
        lead.won_at = timezone.now()
        lead.save(update_fields=["stage", "converted_member", "won_at"])

        ConversionEvent.objects.create(event_type="Membership Purchased", lead=lead, metadata={"converted_member_id": user.id})
        return Response(self.get_serializer(lead).data)

    @action(detail=True, methods=["post"])
    def mark_lost(self, request, pk=None):
        lead = self.get_object()
        lead.stage = Lead.Stage.CHURNED
        lead.lost_reason = request.data.get("lost_reason", "")
        lead.save(update_fields=["stage", "lost_reason"])
        return Response(self.get_serializer(lead).data)


class LeadActivityViewSet(DefaultViewSet):
    queryset = LeadActivity.objects.all().order_by("-created_at")
    serializer_class = LeadActivitySerializer


class LeadTaskViewSet(DefaultViewSet):
    queryset = LeadTask.objects.all().order_by("due_date")
    serializer_class = LeadTaskSerializer


class ConversionEventViewSet(DefaultViewSet):
    queryset = ConversionEvent.objects.all()
    serializer_class = ConversionEventSerializer


class OverheadConfigViewSet(DefaultViewSet):
    queryset = OverheadConfig.objects.all()
    serializer_class = OverheadConfigSerializer


class OfflineConversionConnectorViewSet(DefaultViewSet):
    queryset = OfflineConversionConnector.objects.all()
    serializer_class = OfflineConversionConnectorSerializer

    @action(detail=True, methods=["post"], permission_classes=[IsStaffRole])
    def run(self, request, pk=None):
        connector = self.get_object()
        run = ConnectorRun.objects.create(connector=connector, status="stubbed", response={"message": "stub adapter"})
        return Response(ConnectorRunSerializer(run).data)


class ConnectorRunViewSet(DefaultViewSet):
    queryset = ConnectorRun.objects.all()
    serializer_class = ConnectorRunSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def sgpt_screen(request):
    now = timezone.now()
    session = Session.objects.filter(session_type="sgpt", start_time__lte=now, end_time__gte=now).first()
    if not session:
        return Response({"message": "No active SGPT session"})
    rows = []
    for booking in Booking.objects.filter(session=session, status__in=["booked", "checked_in"]).select_related("member"):
        instance = getattr(booking, "workout_instance", None)
        rows.append({"member": booking.member.get_full_name() or booking.member.username, "workout": instance.snapshot if instance else {}})
    return Response({"session": session.title, "roster": rows})


@api_view(["GET"])
@permission_classes([AllowAny])
def functional_screen(request):
    now = timezone.now()
    session = Session.objects.filter(session_type="functional", start_time__lte=now, end_time__gte=now).first()
    if not session:
        return Response({"message": "No active Functional session"})
    wod = getattr(session, "functional_wod", None)
    return Response({
        "session": session.title,
        "wod": wod.workout if wod else {},
        "attendance": Booking.objects.filter(session=session, status__in=["booked", "checked_in"]).count()
    })


@api_view(["POST"])
@permission_classes([AllowAny])
def lead_webhook(request):
    payload = request.data
    event = LeadIntegrationEvent.objects.create(
        provider=payload.get("provider", "generic"),
        raw_payload=payload,
        mapped_email=payload.get("email", ""),
        mapped_phone=payload.get("phone", ""),
    )
    email = payload.get("email", "")
    phone = payload.get("phone", "")
    lead = None
    if email:
        lead = Lead.objects.filter(email=email).first()
    if not lead and phone:
        lead = Lead.objects.filter(phone=phone).first()
    if not lead:
        lead = Lead.objects.create(
            full_name=payload.get("name", "Unknown Lead"),
            email=email,
            phone=phone,
            source=payload.get("source", event.provider),
            campaign=payload.get("campaign", ""),
            adset=payload.get("adset", ""),
            ad=payload.get("ad", ""),
            utm_source=payload.get("utm_source", ""),
            utm_medium=payload.get("utm_medium", ""),
            utm_campaign=payload.get("utm_campaign", ""),
            click_id=payload.get("fbclid", payload.get("gclid", "")),
        )
    return Response({"lead_id": lead.id, "event_id": event.id}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def consultation_booked(request, lead_id):
    lead = Lead.objects.get(id=lead_id)
    lead.stage = Lead.Stage.BOOKED_CONSULTATION
    lead.save(update_fields=["stage"])
    ConversionEvent.objects.create(event_type="Consultation Booked", lead=lead, metadata={"source": "automation"})
    return Response({"status": "ok"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def conversion_metrics(request):
    days = int(request.query_params.get("days", 30))
    source = request.query_params.get("source")
    start = timezone.now() - timedelta(days=days)

    leads = Lead.objects.filter(created_at__gte=start)
    if source:
        leads = leads.filter(source__iexact=source)

    total = leads.count()
    converted = leads.filter(stage=Lead.Stage.CONVERTED).count()
    new_7_days = leads.filter(created_at__gte=timezone.now() - timedelta(days=7)).count()

    grouped = (
        leads.extra(select={"day": "date(created_at)"})
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )
    by_source = list(leads.values("source").annotate(total=Count("id")).order_by("-total"))

    return Response(
        {
            "total_prospects": total,
            "converted": converted,
            "conversion_rate": round((converted / total) * 100, 2) if total else 0,
            "new_prospects_7d": new_7_days,
            "timeseries": [{"date": str(r["day"]), "count": r["count"]} for r in grouped],
            "by_source": by_source,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def members_overview(request):
    users = User.objects.filter(profile__role=Profile.Role.MEMBER).select_related("member_profile")
    payload = []
    for u in users:
        active = Membership.objects.filter(member=u, is_active=True).select_related("package").order_by("-start_date").first()
        payload.append(
            {
                "id": u.id,
                "name": u.get_full_name() or u.username,
                "email": u.email,
                "phone": getattr(u.profile, "phone", ""),
                "active_membership": bool(active),
                "package": active.package.name if active else "-",
                "start_date": str(active.start_date) if active else None,
            }
        )
    return Response(payload)


WISEFITT_PRIORITY_ORDER = ["hip", "shoulder", "ankle", "thoracic"]


def _library_pick(category, limit=2):
    return list(MobilityExercise.objects.filter(category=category).order_by("level", "name")[:limit])


def _build_mobility_plan_for_assessment(assessment: MobilityAssessment):
    if assessment.pain_flag:
        assessment.ankle_left_score = assessment.ankle_right_score = 1
        assessment.aslr_left_score = assessment.aslr_right_score = 1
        assessment.shoulder_left_score = assessment.shoulder_right_score = 1
        assessment.overhead_squat_score = 1
        assessment.wall_angels_score = 1

    assessment.ankle_final_score = min(assessment.ankle_left_score, assessment.ankle_right_score)
    assessment.aslr_final_score = min(assessment.aslr_left_score, assessment.aslr_right_score)
    assessment.shoulder_final_score = min(assessment.shoulder_left_score, assessment.shoulder_right_score)
    assessment.save(update_fields=[
        "ankle_left_score", "ankle_right_score", "aslr_left_score", "aslr_right_score",
        "shoulder_left_score", "shoulder_right_score", "overhead_squat_score", "wall_angels_score",
        "ankle_final_score", "aslr_final_score", "shoulder_final_score",
    ])

    MobilityPlan.objects.filter(member=assessment.member, is_active=True).update(is_active=False)
    plan = MobilityPlan.objects.create(member=assessment.member, assessment=assessment, is_active=True)

    picks = []
    if assessment.aslr_final_score <= 2:
        picks += _library_pick("hip", 2)
    if assessment.shoulder_final_score <= 2:
        picks += _library_pick("shoulder", 2)
    if assessment.ankle_final_score <= 2:
        picks += _library_pick("ankle", 2)
    if assessment.wall_angels_score <= 2:
        picks += _library_pick("thoracic", 2)

    # de-duplicate and cap 5 exercises
    unique = []
    seen = set()
    for ex in picks:
        if ex.id not in seen:
            seen.add(ex.id)
            unique.append(ex)
        if len(unique) >= 5:
            break

    if not unique:
        unique = _library_pick("stability", 2) or _library_pick("hip", 2)

    for exercise in unique[:5]:
        MobilityPlanItem.objects.create(
            plan=plan, exercise=exercise, sets=2, reps_or_time="30-60s or 8-12 reps", frequency_per_week=3,
            notes="Pain-free range only",
        )
    return plan


class MobilityAssessmentViewSet(DefaultViewSet):
    queryset = MobilityAssessment.objects.all().order_by("-assessed_on", "-created_at")
    serializer_class = MobilityAssessmentSerializer

    def perform_create(self, serializer):
        obj = serializer.save()
        obj.ankle_final_score = min(obj.ankle_left_score, obj.ankle_right_score)
        obj.aslr_final_score = min(obj.aslr_left_score, obj.aslr_right_score)
        obj.shoulder_final_score = min(obj.shoulder_left_score, obj.shoulder_right_score)
        obj.save(update_fields=["ankle_final_score", "aslr_final_score", "shoulder_final_score"])

    @action(detail=True, methods=["post"], url_path="generate-plan")
    def generate_plan(self, request, pk=None):
        assessment = self.get_object()
        plan = _build_mobility_plan_for_assessment(assessment)
        return Response(MobilityPlanSerializer(plan).data, status=status.HTTP_201_CREATED)


class MobilityExerciseViewSet(DefaultViewSet):
    queryset = MobilityExercise.objects.all().order_by("category", "name")
    serializer_class = MobilityExerciseSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdmin()]
        return [IsAuthenticated()]


class MobilityPlanViewSet(DefaultViewSet):
    queryset = MobilityPlan.objects.all().order_by("-created_at")
    serializer_class = MobilityPlanSerializer


class MobilityPlanItemViewSet(DefaultViewSet):
    queryset = MobilityPlanItem.objects.all().order_by("id")
    serializer_class = MobilityPlanItemSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def latest_mobility_for_member(request, member_id):
    assessment = MobilityAssessment.objects.filter(member_id=member_id).order_by("-assessed_on", "-created_at").first()
    if not assessment:
        return Response({"assessment": None, "plan": None})
    plan = MobilityPlan.objects.filter(member_id=member_id, is_active=True).order_by("-created_at").first()
    return Response({
        "assessment": MobilityAssessmentSerializer(assessment).data,
        "plan": MobilityPlanSerializer(plan).data if plan else None,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mobility_block_for_member(request, member_id):
    plan = MobilityPlan.objects.filter(member_id=member_id, is_active=True).order_by("-created_at").first()
    if not plan:
        return Response({"mobility_block": []})
    items = list(plan.items.select_related("exercise")[:2])
    payload = [
        {
            "exercise": i.exercise.name,
            "category": i.exercise.category,
            "sets": i.sets,
            "reps_or_time": i.reps_or_time,
            "frequency_per_week": i.frequency_per_week,
        }
        for i in items
    ]
    return Response({"mobility_block": payload})
