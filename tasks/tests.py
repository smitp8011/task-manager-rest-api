from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Category, Task


class TaskManagerAPITests(APITestCase):
    def setUp(self):
        # Create User 1
        self.user1 = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='Password123!'
        )
        self.token1 = Token.objects.create(user=self.user1)

        # Create User 2
        self.user2 = User.objects.create_user(
            username='bob',
            email='bob@example.com',
            password='Password123!'
        )
        self.token2 = Token.objects.create(user=self.user2)

        # Alice's category
        self.category1 = Category.objects.create(
            user=self.user1,
            name='Work',
            description='Work related tasks'
        )

        # Alice's task
        self.task1 = Task.objects.create(
            user=self.user1,
            category=self.category1,
            title='Prepare Sprint Planning',
            description='Draft initial backlog items',
            priority='HIGH',
            status='PENDING',
            due_date=timezone.now() + timedelta(days=2)
        )

    def test_user_registration(self):
        url = '/api/auth/register/'
        payload = {
            'username': 'charlie',
            'email': 'charlie@example.com',
            'password': 'StrongPassword123!',
            'password2': 'StrongPassword123!'
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], 'charlie')

    def test_user_login(self):
        url = '/api/auth/login/'
        payload = {
            'username': 'alice',
            'password': 'Password123!'
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['token'], self.token1.key)

    def test_unauthenticated_request_blocked(self):
        url = '/api/tasks/'
        response = self.client.get(url)
        # Should return 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_create_task(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        url = '/api/tasks/'
        payload = {
            'title': 'Deploy to Production',
            'description': 'Release v1.0.0 API',
            'priority': 'HIGH',
            'status': 'PENDING',
            'category': self.category1.id,
            'due_date': (timezone.now() + timedelta(days=5)).isoformat()
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Deploy to Production')
        self.assertEqual(response.data['priority'], 'HIGH')

    def test_granular_permission_user_cannot_access_other_user_task(self):
        # Bob tries to access Alice's task
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        url = f'/api/tasks/{self.task1.id}/'
        response = self.client.get(url)
        # Because get_queryset filters by request.user, it returns 404 (or 403)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Bob tries to update Alice's task
        response = self.client.patch(url, {'title': 'Hacked Title'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_assign_another_users_category(self):
        # Bob creates a category
        bob_category = Category.objects.create(user=self.user2, name='Bob Private')
        
        # Alice tries to assign Bob's category to her task
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        url = '/api/tasks/'
        payload = {
            'title': 'Sneaky Task',
            'category': bob_category.id
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category', response.data)

    def test_custom_action_mark_completed(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        url = f'/api/tasks/{self.task1.id}/mark-completed/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, 'COMPLETED')

    def test_task_summary_endpoint(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        url = '/api/tasks/summary/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_tasks'], 1)
        self.assertEqual(response.data['urgent_high_priority_tasks'], 1)
