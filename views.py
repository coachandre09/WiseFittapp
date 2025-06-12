
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import WiseFittOnboardingFormForm, TrainerRecommendationForm
from .models import WiseFittOnboardingForm, TrainerRecommendation, GymProfile
from django.contrib.auth.models import User

@login_required
def onboarding_view(request):
    if hasattr(request.user, 'onboarding_form'):
        return redirect('onboarding_complete')

    if request.method == 'POST':
        form = WiseFittOnboardingFormForm(request.POST)
        if form.is_valid():
            onboarding = form.save(commit=False)
            onboarding.user = request.user
            onboarding.save()
            return redirect('onboarding_complete')
    else:
        form = WiseFittOnboardingFormForm()
    return render(request, 'onboarding/onboarding_form.html', {'form': form})

@login_required
def onboarding_complete(request):
    return render(request, 'onboarding/onboarding_complete.html')

@login_required
def recommendation_view(request, user_id):
    if not request.user.gym_profile.is_trainer:
        return redirect('home')
    client = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = TrainerRecommendationForm(request.POST)
        if form.is_valid():
            rec = form.save(commit=False)
            rec.trainer = request.user
            rec.user = client
            rec.save()
            return redirect('home')
    else:
        form = TrainerRecommendationForm()
    return render(request, 'onboarding/recommendation_form.html', {'form': form, 'client': client})
