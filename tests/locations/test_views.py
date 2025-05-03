from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from travel.locations.models import District, Settlement


class DistrictViewSetTest(APITestCase):
    def setUp(self):
        self.district = District.objects.create(name="Test District")
        self.url = reverse("district-list")

    def test_list_districts(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Test District")

    def test_retrieve_district(self):
        url = reverse("district-detail", args=[self.district.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test District")

    def test_search_districts(self):
        response = self.client.get(f"{self.url}?search=Test")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_districts(self):
        response = self.client.get(f"{self.url}?name=Test District")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)


class SettlementViewSetTest(APITestCase):
    def setUp(self):
        self.district = District.objects.create(name="Test District")
        self.settlement = Settlement.objects.create(
            name="Test City",
            type=Settlement.SettlementType.CITY,
            district=self.district,
        )
        self.url = reverse("settlement-list")

    def test_list_settlements(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Test City")

    def test_retrieve_settlement(self):
        url = reverse("settlement-detail", args=[self.settlement.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test City")
        self.assertEqual(response.data["type"], "city")
        self.assertEqual(response.data["type_display"], "Город")

    def test_search_settlements(self):
        response = self.client.get(f"{self.url}?search=Test")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_settlements(self):
        response = self.client.get(f"{self.url}?name=Test City")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_settlements_by_type(self):
        response = self.client.get(f"{self.url}?type=city")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_settlements_by_district(self):
        response = self.client.get(f"{self.url}?district={self.district.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
