# MODELS – SMALL GROUP PERSONAL TRAINING SYSTEM
# GAMIFICATION SYSTEM – ENHANCED & HEART RATE MONITORING INTEGRATED
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now, timedelta
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

class GamificationProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="gamification_profile")
    total_points = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_check_in = models.DateTimeField(null=True)
    current_level = models.ForeignKey('Level', on_delete=models.SET_NULL, null=True)
    current_league = models.ForeignKey('League', on_delete=models.SET_NULL, null=True)
    total_medals = models.IntegerField(default=0)
    total_achievements = models.IntegerField(default=0)
    ranking_position = models.IntegerField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=['-total_points']),
            models.Index(fields=['-current_streak']),
        ]

    def update_streak(self):
        if not self.last_check_in:
            self.current_streak = 1
        else:
            time_diff = now() - self.last_check_in
            if time_diff.days == 1:
                self.current_streak += 1
            elif time_diff.days > 1:
                self.current_streak = 0
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        self.last_check_in = now()
        self.save()

    def update_level(self):
        level = Level.objects.filter(min_points__lte=self.total_points).order_by('-min_points').first()
        if level:
            self.current_level = level
            self.save()

    def update_ranking(self):
        ranked_profiles = GamificationProfile.objects.order_by('-total_points')
        for idx, profile in enumerate(ranked_profiles, start=1):
            profile.ranking_position = idx
            profile.save()

class HeartRateZone(models.Model):
    name = models.CharField(max_length=100)
    min_bpm = models.IntegerField()
    max_bpm = models.IntegerField()
    points_per_minute = models.IntegerField()

    def __str__(self):
        return f"{self.name} ({self.min_bpm}-{self.max_bpm} bpm)"

class HeartRateSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='heart_rate_sessions')
    session_date = models.DateTimeField(default=now)
    duration_minutes = models.IntegerField()
    zone_times = models.JSONField(default=dict)
    total_points = models.IntegerField(default=0)
    bpm_stream = models.JSONField(default=list, blank=True)

    def calculate_points(self):
        points = 0
        for zone_name, minutes in self.zone_times.items():
            try:
                zone = HeartRateZone.objects.get(name=zone_name)
                points += minutes * zone.points_per_minute
            except HeartRateZone.DoesNotExist:
                continue
        self.total_points = points
        self.save()
        profile = self.user.gamification_profile
        profile.total_points += points
        profile.save()

    def get_top_zone(self):
        if not self.zone_times:
            return None
        return max(self.zone_times.items(), key=lambda x: x[1])[0]

    def get_latest_bpm(self):
        if not self.bpm_stream:
            return None
        return self.bpm_stream[-1]

    def get_display_data(self):
        return {
            'name': self.user.get_full_name() or self.user.username,
            'bpm': self.get_latest_bpm(),
            'zone': self.get_top_zone(),
            'minutes': self.zone_times.get(self.get_top_zone(), 0)
        }

def heart_rate_display_view(request):
    today_sessions = HeartRateSession.objects.filter(session_date__date=now().date()).order_by('-session_date')[:12]
    data = [session.get_display_data() for session in today_sessions if session.bpm_stream]
    return JsonResponse(data, safe=False)

def heart_rate_dashboard(request):
    sessions = HeartRateSession.objects.select_related('user').order_by('-session_date')[:50]
    return render(request, 'gamification/dashboard.html', {'sessions': sessions})
