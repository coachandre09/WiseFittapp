from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('gymapp', '0002_lead_conversion_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MobilityAssessment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assessed_on', models.DateField()),
                ('pain_flag', models.BooleanField(default=False)),
                ('ankle_left_score', models.PositiveSmallIntegerField(default=2)),
                ('ankle_right_score', models.PositiveSmallIntegerField(default=2)),
                ('ankle_left_dorsiflexion_cm', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('ankle_right_dorsiflexion_cm', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('aslr_left_score', models.PositiveSmallIntegerField(default=2)),
                ('aslr_right_score', models.PositiveSmallIntegerField(default=2)),
                ('shoulder_left_score', models.PositiveSmallIntegerField(default=2)),
                ('shoulder_right_score', models.PositiveSmallIntegerField(default=2)),
                ('overhead_squat_score', models.PositiveSmallIntegerField(default=2)),
                ('wall_angels_score', models.PositiveSmallIntegerField(default=2)),
                ('ankle_final_score', models.PositiveSmallIntegerField(default=2)),
                ('aslr_final_score', models.PositiveSmallIntegerField(default=2)),
                ('shoulder_final_score', models.PositiveSmallIntegerField(default=2)),
                ('notes', models.TextField(blank=True)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mobility_assessments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MobilityExercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=160)),
                ('category', models.CharField(choices=[('ankle', 'Ankle'), ('hip', 'Hip'), ('thoracic', 'Thoracic'), ('shoulder', 'Shoulder'), ('stability', 'Stability')], max_length=20)),
                ('level', models.CharField(choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')], default='beginner', max_length=20)),
                ('description', models.TextField(blank=True)),
                ('media_url', models.URLField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='MobilityPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plans', to='gymapp.mobilityassessment')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mobility_plans', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MobilityPlanItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('sets', models.PositiveSmallIntegerField(default=2)),
                ('reps_or_time', models.CharField(default='30-60s', max_length=80)),
                ('frequency_per_week', models.PositiveSmallIntegerField(default=3)),
                ('notes', models.CharField(blank=True, max_length=240)),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gymapp.mobilityexercise')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='gymapp.mobilityplan')),
            ],
        ),
    ]
