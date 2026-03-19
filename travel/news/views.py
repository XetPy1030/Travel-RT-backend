from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..core.pagination import StandardResultsSetPagination
from .authentication import ParserBearerAuthentication
from .models import News
from .serializers import NewsParserCreateSerializer, NewsParserUpdateSerializer, NewsSerializer


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


class NewsParserUpdateView(APIView):
    authentication_classes = (ParserBearerAuthentication,)
    permission_classes = (IsAuthenticated,)

    def patch(self, request, pk: int):
        news = News.objects.filter(pk=pk).first()
        if news is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = NewsParserUpdateSerializer(instance=news, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return Response({"id": updated.id}, status=status.HTTP_200_OK)
