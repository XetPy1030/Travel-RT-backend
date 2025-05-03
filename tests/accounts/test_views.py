from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class UserAPITest(APITestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }
        self.register_url = reverse("user-register")
        self.profile_url = reverse("user-profile")

    def test_create_user(self):
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], self.user_data["email"])
        self.assertEqual(response.data["first_name"], self.user_data["first_name"])
        self.assertEqual(response.data["last_name"], self.user_data["last_name"])

    def test_get_user_profile(self):
        # First create a user
        self.client.post(self.register_url, self.user_data, format="json")

        # Get JWT token
        token_url = reverse("token_obtain_pair")
        token_response = self.client.post(
            token_url,
            {"email": self.user_data["email"], "password": self.user_data["password"]},
            format="json",
        )

        # Set the token in the Authorization header
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}"
        )

        # Get user profile
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user_data["email"])
