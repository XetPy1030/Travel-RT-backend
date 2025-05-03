from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters

from .models import Router
from .serializers import RouterListSerializer, RouterDetailSerializer
from ..core.pagination import StandardResultsSetPagination


class RouterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Router.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['district', 'settlement']
    search_fields = ['title', 'short_description']
    ordering_fields = ['title', 'created_at']
    ordering = ['title']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RouterDetailSerializer
        return RouterListSerializer
