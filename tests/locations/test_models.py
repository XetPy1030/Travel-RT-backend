from django.test import TestCase

from travel.locations.models import District, Settlement


class DistrictModelTest(TestCase):
    def test_create_district(self):
        district = District.objects.create(name="Test District")
        self.assertEqual(district.name, "Test District")
        self.assertIsNone(district.administrative_center)

    def test_district_str(self):
        district = District.objects.create(name="Test District")
        self.assertEqual(str(district), "Test District")


class SettlementModelTest(TestCase):
    def setUp(self):
        self.district = District.objects.create(name="Test District")

    def test_create_settlement(self):
        settlement = Settlement.objects.create(
            name="Test City",
            type=Settlement.SettlementType.CITY,
            district=self.district,
        )
        self.assertEqual(settlement.name, "Test City")
        self.assertEqual(settlement.type, Settlement.SettlementType.CITY)
        self.assertEqual(settlement.district, self.district)

    def test_create_city_district(self):
        settlement = Settlement.objects.create(
            name="Test City", type=Settlement.SettlementType.CITY
        )
        self.assertEqual(settlement.name, "Test City")
        self.assertEqual(settlement.type, Settlement.SettlementType.CITY)
        self.assertIsNone(settlement.district)
        self.assertTrue(settlement.is_city_district)

    def test_settlement_str(self):
        settlement = Settlement.objects.create(
            name="Test City",
            type=Settlement.SettlementType.CITY,
            district=self.district,
        )
        self.assertEqual(str(settlement), "Test City (Город)")
