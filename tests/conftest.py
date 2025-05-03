import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def authenticated_api_client(user, api_client):
    api_client.force_authenticate(user=user)
    return api_client
