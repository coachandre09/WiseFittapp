from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import (
    Profile, MemberProfile, MembershipPackage, ProductAddon, PackageAddon, Membership,
    Program, WorkoutTemplate, Session, FunctionalWOD, Booking, WorkoutInstance, WorkoutLog,
    TreatmentType, TreatmentBooking, FinanceEntry, Lead, LeadActivity, LeadTask,
    LeadIntegrationEvent, ConversionEvent, OverheadConfig, OfflineConversionConnector, ConnectorRun
)
from .permissions import IsStaffRole
from .serializers import (
    ProfileSerializer, MembershipPackageSerializer, ProductAddonSerializer, PackageAddonSerializer, MembershipSerializer,
    ProgramSerializer, WorkoutTemplateSerializer, SessionSerializer, FunctionalWODSerializer, BookingSerializer,
    WorkoutInstanceSerializer, WorkoutLogSerializer, TreatmentTypeSerializer, TreatmentBookingSerializer,
    FinanceEntrySerializer, LeadSerializer, LeadActivitySerializer, LeadTaskSerializer,
    LeadIntegrationEventSerializer, ConversionEventSerializer, OverheadConfigSerializer,
    OfflineConversionConnectorSerializer, ConnectorRunSerializer
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
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer


class LeadActivityViewSet(DefaultViewSet):
    queryset = LeadActivity.objects.all()
    serializer_class = LeadActivitySerializer


class LeadTaskViewSet(DefaultViewSet):
    queryset = LeadTask.objects.all()
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
