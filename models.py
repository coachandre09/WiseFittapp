
from django.db import models
from django.contrib.auth.models import User

# Categorias de bloco
BLOCK_TYPES = [
    ("warmup", "Warm-Up"),
    ("strength", "Strength"),
    ("conditioning", "Conditioning"),
    ("accessory", "Accessory"),
    ("mobility", "Mobility")
]

class TrainingProgram(models.Model):
    name = models.CharField(max_length=255)
    coach = models.ForeignKey(User, on_delete=models.CASCADE, related_name="programs")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class TrainingDay(models.Model):
    program = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE, related_name="days")
    day_number = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.program.name} - Day {self.day_number}"

class TrainingBlock(models.Model):
    day = models.ForeignKey(TrainingDay, on_delete=models.CASCADE, related_name="blocks")
    title = models.CharField(max_length=100)
    block_type = models.CharField(max_length=30, choices=BLOCK_TYPES)

    def __str__(self):
        return f"{self.block_type.upper()} - {self.title}"

class TrainingExerciseBlock(models.Model):
    block = models.ForeignKey(TrainingBlock, on_delete=models.CASCADE, related_name="exercises")
    name = models.CharField(max_length=255)
    sets = models.CharField(max_length=10)
    reps = models.CharField(max_length=10)
    tempo = models.CharField(max_length=20, blank=True)
    rest = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name
