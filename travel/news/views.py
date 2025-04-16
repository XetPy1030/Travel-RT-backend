from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import News
from .serializers import NewsSerializer
from ..core.pagination import StandardResultsSetPagination


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = []
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
