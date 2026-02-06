from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("profiles", views.ProfileViewSet)
router.register("membership-packages", views.MembershipPackageViewSet)
router.register("product-addons", views.ProductAddonViewSet)
router.register("package-addons", views.PackageAddonViewSet)
router.register("memberships", views.MembershipViewSet)
router.register("programs", views.ProgramViewSet)
router.register("workout-templates", views.WorkoutTemplateViewSet)
router.register("sessions", views.SessionViewSet)
router.register("functional-wods", views.FunctionalWODViewSet)
router.register("bookings", views.BookingViewSet)
router.register("workout-instances", views.WorkoutInstanceViewSet)
router.register("workout-logs", views.WorkoutLogViewSet)
router.register("treatment-types", views.TreatmentTypeViewSet)
router.register("treatment-bookings", views.TreatmentBookingViewSet)
router.register("finance-entries", views.FinanceEntryViewSet)
router.register("leads", views.LeadViewSet)
router.register("lead-activities", views.LeadActivityViewSet)
router.register("lead-tasks", views.LeadTaskViewSet)
router.register("conversion-events", views.ConversionEventViewSet)
router.register("overhead-configs", views.OverheadConfigViewSet)
router.register("offline-connectors", views.OfflineConversionConnectorViewSet)
router.register("connector-runs", views.ConnectorRunViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("screens/sgpt/", views.sgpt_screen),
    path("screens/functional/", views.functional_screen),
    path("integrations/leads/webhook/", views.lead_webhook),
    path("crm/leads/<int:lead_id>/consultation-booked/", views.consultation_booked),
]
