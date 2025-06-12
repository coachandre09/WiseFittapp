from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework import status
from .models import TrainingProgram, TrainingDay, TrainingBlock, TrainingExerciseBlock

class TrainingProgramTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='coach', password='pass1234')
        self.program = TrainingProgram.objects.create(name='Beginner Program', coach=self.user)
        self.day = TrainingDay.objects.create(program=self.program, day_number=1)
        self.block = TrainingBlock.objects.create(day=self.day, title='Strength Block', block_type='strength')
        self.exercise = TrainingExerciseBlock.objects.create(
            block=self.block,
            name='Squat',
            sets=3,
            reps=10,
            tempo='20X1',
            rest='60s',
            notes='Full depth'
        )

    def test_program_str(self):
        self.assertEqual(str(self.program), 'Beginner Program')

    def test_day_str(self):
        self.assertEqual(str(self.day), 'Beginner Program - Day 1')

    def test_block_str(self):
        self.assertEqual(str(self.block), 'STRENGTH - Strength Block')

    def test_exercise_str(self):
        self.assertEqual(str(self.exercise), 'Squat')

    def test_api_get_programs(self):
        response = self.client.get('/programs/')
        self.assertEqual(response.status_code, 200)

    def test_api_get_days(self):
        response = self.client.get('/days/')
        self.assertEqual(response.status_code, 200)

    def test_api_get_blocks(self):
        response = self.client.get('/blocks/')
        self.assertEqual(response.status_code, 200)

    def test_api_get_exercises(self):
        response = self.client.get('/exercises/')
        self.assertEqual(response.status_code, 200)

class AuthPermissionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='coach', password='pass1234')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_create_program_authenticated(self):
        data = {'name': 'Test Program', 'coach': self.user.id}
        response = self.client.post('/programs/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_program_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {'name': 'Test Program', 'coach': self.user.id}
        response = self.client.post('/programs/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
