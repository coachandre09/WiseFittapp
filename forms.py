
from django import forms
from .models import WiseFittOnboardingForm, TrainerRecommendation

class WiseFittOnboardingFormForm(forms.ModelForm):
    class Meta:
        model = WiseFittOnboardingForm
        exclude = ['user', 'submitted_at']

class TrainerRecommendationForm(forms.ModelForm):
    class Meta:
        model = TrainerRecommendation
        fields = ['notes']
