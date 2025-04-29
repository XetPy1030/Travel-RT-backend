from rest_framework import viewsets

from travel.locations.models import District, Settlement
from travel.locations.serializers import DistrictSerializer, SettlementSerializer


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint для чтения данных о районах
    """
    queryset = District.objects.all()
    serializer_class = DistrictSerializer


class SettlementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint для чтения данных о населенных пунктах
    """
    queryset = Settlement.objects.all()
    serializer_class = SettlementSerializer
