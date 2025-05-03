from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tests.locations.factories import DistrictFactory, SettlementFactory
from travel.places.models import Place


class PlaceViewSetTest(APITestCase):
    def setUp(self):
        self.district = DistrictFactory()
        self.settlement = SettlementFactory()
        self.place = Place.objects.create(
            title="Test Place",
            short_description="Short description",
            full_description="Full description",
            district=self.district,
            settlement=self.settlement,
        )
        self.url = reverse("place-list")

    def test_list_places(self):
        """Test listing places."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Place")
        self.assertEqual(
            response.data["results"][0]["short_description"], "Short description"
        )
        self.assertEqual(
            response.data["results"][0]["district_name"], self.district.name
        )
        self.assertEqual(
            response.data["results"][0]["settlement_name"], self.settlement.name
        )

    def test_retrieve_place(self):
        """Test retrieving a single place."""
        url = reverse("place-detail", args=[self.place.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Place")
        self.assertEqual(response.data["short_description"], "Short description")
        self.assertEqual(response.data["full_description"], "Full description")
        self.assertEqual(response.data["district_name"], self.district.name)
        self.assertEqual(response.data["settlement_name"], self.settlement.name)

    def test_search_places(self):
        """Test searching places."""
        response = self.client.get(f"{self.url}?search=Test")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_places_by_district(self):
        """Test filtering places by district."""
        response = self.client.get(f"{self.url}?district={self.district.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_places_by_settlement(self):
        """Test filtering places by settlement."""
        response = self.client.get(f"{self.url}?settlement={self.settlement.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_ordering_places(self):
        """Test ordering places."""
        # Create another place
        Place.objects.create(
            title="Another Place",
            short_description="Another description",
            full_description="Another full description",
            district=self.district,
            settlement=self.settlement,
        )

        # Test ordering by title ascending (default)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["title"], "Another Place")

        # Test ordering by title descending
        response = self.client.get(f"{self.url}?ordering=-title")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["title"], "Test Place")

        # Test ordering by created_at
        response = self.client.get(f"{self.url}?ordering=created_at")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["title"], "Test Place")
