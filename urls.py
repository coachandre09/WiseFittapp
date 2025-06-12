
from django.urls import path
from . import views

urlpatterns = [
    path('onboarding/', views.onboarding_view, name='onboarding'),
    path('onboarding/complete/', views.onboarding_complete, name='onboarding_complete'),
    path('recommendation/<int:user_id>/', views.recommendation_view, name='recommendation'),
]
