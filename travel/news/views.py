from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..core.pagination import StandardResultsSetPagination
from .authentication import ParserBearerAuthentication
from .models import News
from .serializers import NewsParserCreateSerializer, NewsSerializer


class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = []
    search_fields = ["title", "description"]
    ordering_fields = ["published_at", "created_at", "title"]
    ordering = ["-published_at"]


class NewsParserCreateView(APIView):
    authentication_classes = (ParserBearerAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = NewsParserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        news = serializer.save()
        return Response({"id": news.id}, status=status.HTTP_201_CREATED)
