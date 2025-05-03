from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class UserCreateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.create_url = reverse("user-register")
        self.valid_payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }

    def test_create_valid_user(self):
        """Test creating user with valid payload is successful"""
        response = self.client.post(self.create_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get()
        self.assertEqual(user.email, self.valid_payload["email"])
        self.assertEqual(user.first_name, self.valid_payload["first_name"])
        self.assertEqual(user.last_name, self.valid_payload["last_name"])
        self.assertTrue(user.check_password(self.valid_payload["password"]))

    def test_create_invalid_email(self):
        """Test creating user with invalid email fails"""
        payload = self.valid_payload.copy()
        payload["email"] = "invalid-email"
        response = self.client.post(self.create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_create_user_without_password(self):
        """Test creating user without password fails"""
        payload = self.valid_payload.copy()
        del payload["password"]
        response = self.client.post(self.create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_create_user_with_existing_email(self):
        """Test creating user with existing email fails"""
        self.client.post(self.create_url, self.valid_payload)
        response = self.client.post(self.create_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
