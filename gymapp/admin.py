from django.contrib import admin
from .models import (
    Profile, MemberProfile, MembershipPackage, Membership, ProductAddon, PackageAddon,
    Program, WorkoutTemplate, Session, FunctionalWOD, Booking, WorkoutInstance, WorkoutLog,
    TreatmentType, TreatmentBooking, FinanceEntry, Lead, LeadActivity, LeadTask,
    LeadIntegrationEvent, ConversionEvent, OverheadConfig, OfflineConversionConnector, ConnectorRun,
    MobilityAssessment, MobilityExercise, MobilityPlan, MobilityPlanItem
)

admin.site.register([
    Profile, MemberProfile, MembershipPackage, Membership, ProductAddon, PackageAddon,
    Program, WorkoutTemplate, Session, FunctionalWOD, Booking, WorkoutInstance, WorkoutLog,
    TreatmentType, TreatmentBooking, FinanceEntry, Lead, LeadActivity, LeadTask,
    LeadIntegrationEvent, ConversionEvent, OverheadConfig, OfflineConversionConnector, ConnectorRun,
    MobilityAssessment, MobilityExercise, MobilityPlan, MobilityPlanItem,
])
