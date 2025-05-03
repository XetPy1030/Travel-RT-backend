from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from travel.core.pagination import StandardResultsSetPagination
from travel.locations.models import District, Settlement
from travel.locations.serializers import DistrictSerializer, SettlementSerializer


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint для чтения данных о районах
    """

    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["name"]
    search_fields = ["name"]
    ordering_fields = ["name", "settlements_count"]
    ordering = ["name"]


class SettlementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint для чтения данных о населенных пунктах
    """

    queryset = Settlement.objects.all()
    serializer_class = SettlementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["name", "type", "district"]
    search_fields = ["name"]
    ordering_fields = ["name", "type"]
    ordering = ["name"]
