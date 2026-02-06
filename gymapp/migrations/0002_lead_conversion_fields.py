from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('gymapp', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='converted_member',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='converted_from_leads', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='lead',
            name='lost_reason',
            field=models.CharField(blank=True, max_length=240),
        ),
        migrations.AddField(
            model_name='lead',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='won_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
