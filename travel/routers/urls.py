from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import RouterViewSet, generate_route, generate_route_status

router = DefaultRouter()
router.register(r"", RouterViewSet)

urlpatterns = [
    path("generate/", generate_route),
    path("generate/<str:task_id>/", generate_route_status),
    path("", include(router.urls)),
]
