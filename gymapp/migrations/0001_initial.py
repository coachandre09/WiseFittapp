# Generated manually for MVP scaffold
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name='Program',
            fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)), ('name', models.CharField(max_length=120)), ('description', models.TextField(blank=True))],
        ),
        migrations.CreateModel(
            name='MembershipPackage',
            fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)), ('name', models.CharField(max_length=120)), ('price', models.DecimalField(decimal_places=2, max_digits=10)), ('billing_cycle', models.CharField(choices=[('monthly', 'Monthly'), ('weekly', 'Weekly')], max_length=20)), ('included_credits', models.PositiveIntegerField(blank=True, null=True)), ('unlimited_classes', models.BooleanField(default=False)), ('freeze_rules', models.TextField(blank=True)), ('cancellation_terms', models.TextField(blank=True))],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)), ('session_type', models.CharField(choices=[('sgpt', 'SGPT'), ('functional', 'Functional Fitness'), ('treatment', 'Treatment')], max_length=20)), ('room', models.CharField(choices=[('sgpt_room', 'SGPT Room'), ('functional_room', 'Functional Room'), ('treatment_room', 'Treatment Room')], max_length=30)), ('title', models.CharField(max_length=120)), ('start_time', models.DateTimeField()), ('end_time', models.DateTimeField()), ('capacity', models.PositiveIntegerField(default=1)), ('recurrence_rule', models.CharField(blank=True, max_length=120)), ('coach', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='coaching_sessions', to=settings.AUTH_USER_MODEL))],
        ),
        migrations.RunPython(migrations.RunPython.noop),
    ]
