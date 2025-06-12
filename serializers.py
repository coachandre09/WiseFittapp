from rest_framework import serializers
from .models import TrainingProgram, TrainingDay, TrainingBlock, TrainingExerciseBlock

class TrainingExerciseBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingExerciseBlock
        fields = '__all__'

class TrainingBlockSerializer(serializers.ModelSerializer):
    exercises = TrainingExerciseBlockSerializer(many=True, read_only=True)

    class Meta:
        model = TrainingBlock
        fields = '__all__'

class TrainingDaySerializer(serializers.ModelSerializer):
    blocks = TrainingBlockSerializer(many=True, read_only=True)

    class Meta:
        model = TrainingDay
        fields = '__all__'

class TrainingProgramSerializer(serializers.ModelSerializer):
    days = TrainingDaySerializer(many=True, read_only=True)

    class Meta:
        model = TrainingProgram
        fields = '__all__'
