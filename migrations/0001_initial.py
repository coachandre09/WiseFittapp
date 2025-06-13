from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TrainingProgram',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('coach', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='programs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TrainingDay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_number', models.PositiveIntegerField()),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='days', to='WiseFittapp.trainingprogram')),
            ],
        ),
        migrations.CreateModel(
            name='TrainingBlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('block_type', models.CharField(choices=[('warmup', 'Warm-Up'), ('strength', 'Strength'), ('conditioning', 'Conditioning'), ('accessory', 'Accessory'), ('mobility', 'Mobility')], max_length=30)),
                ('day', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocks', to='WiseFittapp.trainingday')),
            ],
        ),
        migrations.CreateModel(
            name='TrainingExerciseBlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('sets', models.CharField(max_length=10)),
                ('reps', models.CharField(max_length=10)),
                ('tempo', models.CharField(blank=True, max_length=20)),
                ('rest', models.CharField(blank=True, max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('block', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exercises', to='WiseFittapp.trainingblock')),
            ],
        ),
    ]
