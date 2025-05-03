from django.urls import include, path
from rest_framework.routers import DefaultRouter

from travel.locations.views import DistrictViewSet, SettlementViewSet

router = DefaultRouter()
router.register(r"districts", DistrictViewSet, basename="district")
router.register(r"settlements", SettlementViewSet, basename="settlement")

urlpatterns = [
    path("", include(router.urls)),
]
