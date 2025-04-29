from django.urls import path

from .views import DistrictViewSet, SettlementViewSet

urlpatterns = [
    path('districts/', DistrictViewSet.as_view({'get': 'list'}), name='districts'),
    path('districts/<int:pk>/', DistrictViewSet.as_view({'get': 'retrieve'}), name='district-detail'),
    path('settlements/', SettlementViewSet.as_view({'get': 'list'}), name='settlements'),
    path('settlements/<int:pk>/', SettlementViewSet.as_view({'get': 'retrieve'}), name='settlement-detail'),
]
