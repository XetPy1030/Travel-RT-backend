from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tests.accounts.factories import UserFactory
from travel.news.models import News


class NewsViewSetTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.news = News.objects.create(
            title="Test News",
            description="Test Description",
            content="Test Content",
            created_by=self.user,
        )
        self.url = reverse("news-list")

    def test_list_news(self):
        """Test listing news items."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test News")

    def test_retrieve_news(self):
        """Test retrieving a single news item."""
        url = reverse("news-detail", args=[self.news.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test News")
        self.assertEqual(response.data["description"], "Test Description")
        self.assertEqual(response.data["content"], "Test Content")

    def test_search_news(self):
        """Test searching news items."""
        response = self.client.get(f"{self.url}?search=Test")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_ordering_news(self):
        """Test ordering news items."""
        # Create another news item
        News.objects.create(
            title="Another News",
            description="Another Description",
            content="Another Content",
            created_by=self.user,
        )

        # Test ordering by title ascending
        response = self.client.get(f"{self.url}?ordering=title")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["title"], "Another News")

        # Test ordering by title descending
        response = self.client.get(f"{self.url}?ordering=-title")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["title"], "Test News")

        # Test ordering by created_at descending (default)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["title"], "Another News")
