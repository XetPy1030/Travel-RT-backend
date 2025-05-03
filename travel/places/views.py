from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from ..core.pagination import StandardResultsSetPagination
from .models import Place
from .serializers import PlaceDetailSerializer, PlaceListSerializer


class PlaceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Place.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["district", "settlement"]
    search_fields = ["title", "short_description"]
    ordering_fields = ["title", "created_at"]
    ordering = ["title"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PlaceDetailSerializer
        return PlaceListSerializer
