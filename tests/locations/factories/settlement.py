import factory

from travel.locations.models import Settlement

from .district import DistrictFactory


class SettlementFactory(factory.django.DjangoModelFactory):
    """Factory for creating Settlement instances."""

    class Meta:
        model = Settlement

    name = factory.Faker("city")
    type = factory.Iterator(Settlement.SettlementType.values)
    district = factory.SubFactory(DistrictFactory)
