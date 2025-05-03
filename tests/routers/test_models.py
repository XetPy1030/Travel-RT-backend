from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from tests.locations.factories import DistrictFactory, SettlementFactory
from travel.routers.models import Router


class RouterModelTest(TestCase):
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

    def test_create_router(self):
        """Test creating a router."""
        self.assertEqual(self.router.title, "Test Router")
        self.assertEqual(self.router.short_description, "Short description")
        self.assertEqual(self.router.full_description, "Full description")
        self.assertEqual(self.router.duration, timezone.timedelta(hours=2))
        self.assertEqual(self.router.difficulty, Router.Difficulty.MEDIUM)
        self.assertEqual(self.router.district, self.district)
        self.assertEqual(self.router.settlement, self.settlement)
        self.assertIsNotNone(self.router.created_at)
        self.assertIsNotNone(self.router.updated_at)

    def test_router_str(self):
        """Test the string representation of a router."""
        self.assertEqual(str(self.router), "Test Router")

    def test_router_verbose_names(self):
        """Test the verbose names of the Router model."""
        self.assertEqual(Router._meta.verbose_name, "Маршрут")
        self.assertEqual(Router._meta.verbose_name_plural, "Маршруты")

    def test_router_validation(self):
        """Test router validation."""
        # Test creating a router without district and settlement
        router = Router(
            title="Invalid Router",
            short_description="Short description",
            full_description="Full description",
            duration=timezone.timedelta(hours=2),
            difficulty=Router.Difficulty.MEDIUM,
        )
        with self.assertRaises(ValidationError):
            router.full_clean()

        # Test creating a router with only district
        router = Router(
            title="Valid Router",
            short_description="Short description",
            full_description="Full description",
            duration=timezone.timedelta(hours=2),
            difficulty=Router.Difficulty.MEDIUM,
            district=self.district,
        )
        router.full_clean()  # Should not raise an error

        # Test creating a router with only settlement
        router = Router(
            title="Valid Router",
            short_description="Short description",
            full_description="Full description",
            duration=timezone.timedelta(hours=2),
            difficulty=Router.Difficulty.MEDIUM,
            settlement=self.settlement,
        )
        router.full_clean()  # Should not raise an error

    def test_router_difficulty_choices(self):
        """Test router difficulty choices."""
        self.assertEqual(
            Router.Difficulty.choices,
            [
                ("easy", "Легкий"),
                ("medium", "Средний"),
                ("hard", "Сложный"),
            ],
        )
