from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters

from .models import Place
from .serializers import PlaceListSerializer, PlaceDetailSerializer


class PlaceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Place.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['district', 'settlement']
    search_fields = ['title', 'short_description']
    ordering_fields = ['title', 'created_at']
    ordering = ['title']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PlaceDetailSerializer
        return PlaceListSerializer
