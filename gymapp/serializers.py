from django.contrib.auth.models import User
from rest_framework import serializers
from .models import (
    Profile, MemberProfile, MembershipPackage, ProductAddon, PackageAddon, Membership,
    Program, WorkoutTemplate, Session, FunctionalWOD, Booking, WorkoutInstance, WorkoutLog,
    TreatmentType, TreatmentBooking, FinanceEntry, Lead, LeadActivity, LeadTask,
    LeadIntegrationEvent, ConversionEvent, OverheadConfig, OfflineConversionConnector, ConnectorRun
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = "__all__"


class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"


class MembershipPackageSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = MembershipPackage


class ProductAddonSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = ProductAddon


class PackageAddonSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = PackageAddon


class MembershipSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = Membership


class ProgramSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = Program


class WorkoutTemplateSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = WorkoutTemplate


class SessionSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = Session


class FunctionalWODSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = FunctionalWOD


class WorkoutInstanceSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = WorkoutInstance


class BookingSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = Booking


class WorkoutLogSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = WorkoutLog


class TreatmentTypeSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = TreatmentType


class TreatmentBookingSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = TreatmentBooking


class FinanceEntrySerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = FinanceEntry


class LeadSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = Lead


class LeadActivitySerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = LeadActivity


class LeadTaskSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = LeadTask


class LeadIntegrationEventSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = LeadIntegrationEvent


class ConversionEventSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = ConversionEvent


class OverheadConfigSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = OverheadConfig


class OfflineConversionConnectorSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = OfflineConversionConnector


class ConnectorRunSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = ConnectorRun
