from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from tests.accounts.factories import UserFactory


class TokenObtainPairViewTest(APITestCase):
    def setUp(self):
        self.url = reverse("token_obtain_pair")
        self.user = UserFactory(email="test@example.com", password="test_password123")
        self.valid_credentials = {
            "email": "test@example.com",
            "password": "test_password123",
        }
        self.invalid_credentials = {
            "email": "test@example.com",
            "password": "wrong_password",
        }

    def test_obtain_token_pair_success(self):
        """Test successful token pair obtaining"""
        response = self.client.post(self.url, self.valid_credentials)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_obtain_token_pair_invalid_credentials(self):
        """Test token pair obtaining with invalid credentials"""
        response = self.client.post(self.url, self.invalid_credentials)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenRefreshViewTest(APITestCase):
    def setUp(self):
        self.url = reverse("token_refresh")
        self.user = UserFactory(password="test_password123")
        self.refresh_token = RefreshToken.for_user(self.user)

    def test_refresh_token_success(self):
        """Test successful access token refresh"""
        data = {"refresh": str(self.refresh_token)}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_refresh_token_invalid(self):
        """Test token refresh with invalid refresh token"""
        data = {"refresh": "invalid_token"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenVerifyViewTest(APITestCase):
    def setUp(self):
        self.url = reverse("token_verify")
        self.user = UserFactory(password="test_password123")
        self.refresh_token = RefreshToken.for_user(self.user)
        self.access_token = self.refresh_token.access_token

    def test_verify_token_success(self):
        """Test successful token verification"""
        data = {"token": str(self.access_token)}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_verify_token_invalid(self):
        """Test token verification with invalid token"""
        data = {"token": "invalid_token"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenBlacklistTest(APITestCase):
    def setUp(self):
        self.user = UserFactory(password="test_password123")
        self.refresh_token = RefreshToken.for_user(self.user)
        self.access_token = self.refresh_token.access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_token_blacklist_on_logout(self):
        """Test that refresh token is blacklisted after logout"""
        url = reverse("logout")
        data = {"refresh": str(self.refresh_token)}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

        # Try to use the blacklisted refresh token
        refresh_url = reverse("token_refresh")
        response = self.client.post(refresh_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticationIntegrationTest(APITestCase):
    def setUp(self):
        self.user = UserFactory(
            email="integration@test.com", password="integration_pass123"
        )
        self.credentials = {
            "email": "integration@test.com",
            "password": "integration_pass123",
        }

    def test_full_authentication_flow(self):
        """Test the complete authentication flow:
        1. Obtain tokens
        2. Access protected resource
        3. Refresh token
        4. Verify token
        5. Logout
        """
        # 1. Obtain tokens
        token_url = reverse("token_obtain_pair")
        response = self.client.post(token_url, self.credentials)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        tokens = response.data
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        # 2. Access protected resource
        protected_url = reverse("user-profile")
        response = self.client.get(protected_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 3. Refresh token
        refresh_url = reverse("token_refresh")
        response = self.client.post(refresh_url, {"refresh": tokens["refresh"]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 4. Verify new token
        verify_url = reverse("token_verify")
        response = self.client.post(verify_url, {"token": response.data["access"]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 5. Logout
        logout_url = reverse("logout")
        response = self.client.post(logout_url, {"refresh": tokens["refresh"]})
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
