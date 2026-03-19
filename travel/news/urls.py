from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NewsParserCreateView, NewsParserUpdateView, NewsViewSet

router = DefaultRouter()
router.register(r"", NewsViewSet)

urlpatterns = [
    path("parser/", NewsParserCreateView.as_view(), name="news-parser-create"),
    path("parser/<int:pk>/", NewsParserUpdateView.as_view(), name="news-parser-update"),
    path("", include(router.urls)),
]
