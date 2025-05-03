from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from tests.locations.factories import DistrictFactory, SettlementFactory
from travel.routers.models import Router


class RouterViewSetTest(APITestCase):
    def setUp(self):
        self.district = DistrictFactory()
        self.settlement = SettlementFactory()
        self.router = Router.objects.create(
            title="Test Router",
            short_description="Short description",
            full_description="Full description",
            duration=timezone.timedelta(hours=2),
            difficulty=Router.Difficulty.MEDIUM,
            district=self.district,
            settlement=self.settlement,
        )
        self.url = reverse("router-list")

    def test_list_routers(self):
        """Test listing routers."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Router")
        self.assertEqual(
            response.data["results"][0]["short_description"], "Short description"
        )
        self.assertEqual(response.data["results"][0]["duration"], "02:00:00")
        self.assertEqual(response.data["results"][0]["difficulty"], "medium")
        self.assertEqual(
            response.data["results"][0]["district_name"], self.district.name
        )
        self.assertEqual(
            response.data["results"][0]["settlement_name"], self.settlement.name
        )

    def test_retrieve_router(self):
        """Test retrieving a single router."""
        url = reverse("router-detail", args=[self.router.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Router")
        self.assertEqual(response.data["short_description"], "Short description")
        self.assertEqual(response.data["full_description"], "Full description")
        self.assertEqual(response.data["duration"], "02:00:00")
        self.assertEqual(response.data["difficulty"], "medium")
        self.assertEqual(response.data["district_name"], self.district.name)
        self.assertEqual(response.data["settlement_name"], self.settlement.name)

    def test_search_routers(self):
        """Test searching routers."""
        response = self.client.get(f"{self.url}?search=Test")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_routers_by_district(self):
        """Test filtering routers by district."""
        response = self.client.get(f"{self.url}?district={self.district.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_routers_by_settlement(self):
        """Test filtering routers by settlement."""
        response = self.client.get(f"{self.url}?settlement={self.settlement.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_ordering_routers(self):
        """Test ordering routers."""
        # Create another router
        Router.objects.create(
            title="Another Router",
            short_description="Another description",
            full_description="Another full description",
            duration=timezone.timedelta(hours=1),
            difficulty=Router.Difficulty.EASY,
            district=self.district,
            settlement=self.settlement,
        )

        # Test ordering by title ascending (default)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["title"], "Another Router")

        # Test ordering by title descending
        response = self.client.get(f"{self.url}?ordering=-title")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["title"], "Test Router")

        # Test ordering by created_at
        response = self.client.get(f"{self.url}?ordering=created_at")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["title"], "Test Router")
