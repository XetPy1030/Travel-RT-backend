from django.core.exceptions import ValidationError
from django.test import TestCase

from tests.locations.factories import DistrictFactory, SettlementFactory
from travel.places.models import Place, PlaceImage


class PlaceModelTest(TestCase):
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

    def test_create_place(self):
        """Test creating a place."""
        self.assertEqual(self.place.title, "Test Place")
        self.assertEqual(self.place.short_description, "Short description")
        self.assertEqual(self.place.full_description, "Full description")
        self.assertEqual(self.place.district, self.district)
        self.assertEqual(self.place.settlement, self.settlement)
        self.assertIsNotNone(self.place.created_at)
        self.assertIsNotNone(self.place.updated_at)

    def test_place_str(self):
        """Test the string representation of a place."""
        self.assertEqual(str(self.place), "Test Place")

    def test_place_verbose_names(self):
        """Test the verbose names of the Place model."""
        self.assertEqual(Place._meta.verbose_name, "Интересное место")
        self.assertEqual(Place._meta.verbose_name_plural, "Интересные места")

    def test_place_validation(self):
        """Test place validation."""
        # Test creating a place without district and settlement
        place = Place(
            title="Invalid Place",
            short_description="Short description",
            full_description="Full description",
        )
        with self.assertRaises(ValidationError):
            place.full_clean()

        # Test creating a place with only district
        place = Place(
            title="Valid Place",
            short_description="Short description",
            full_description="Full description",
            district=self.district,
        )
        place.full_clean()  # Should not raise an error

        # Test creating a place with only settlement
        place = Place(
            title="Valid Place",
            short_description="Short description",
            full_description="Full description",
            settlement=self.settlement,
        )
        place.full_clean()  # Should not raise an error


class PlaceImageModelTest(TestCase):
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
        self.place_image = PlaceImage.objects.create(place=self.place, order=1)

    def test_create_place_image(self):
        """Test creating a place image."""
        self.assertEqual(self.place_image.place, self.place)
        self.assertEqual(self.place_image.order, 1)

    def test_place_image_str(self):
        """Test the string representation of a place image."""
        self.assertEqual(str(self.place_image), f"Изображение для {self.place.title}")

    def test_place_image_verbose_names(self):
        """Test the verbose names of the PlaceImage model."""
        self.assertEqual(PlaceImage._meta.verbose_name, "Изображение места")
        self.assertEqual(PlaceImage._meta.verbose_name_plural, "Изображения мест")
