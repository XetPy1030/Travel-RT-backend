from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from travel.locations.models import District, Settlement


class SettlementSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_city_district(self, obj):
        return obj.is_city_district

    class Meta:
        model = Settlement
        fields = ['id', 'name', 'district', 'type', 'type_display', 'is_city_district']
        read_only_fields = ['is_city_district']


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name', 'administrative_center']
