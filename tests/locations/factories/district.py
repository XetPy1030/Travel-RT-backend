import factory

from travel.locations.models import District


class DistrictFactory(factory.django.DjangoModelFactory):
    """Factory for creating District instances."""

    class Meta:
        model = District

    name = factory.Faker("city")
