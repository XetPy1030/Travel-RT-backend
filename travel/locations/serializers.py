from rest_framework import serializers

from travel.locations.models import District, Settlement


class SettlementSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Settlement
        fields = ['id', 'name', 'district', 'type', 'type_display', 'is_city_district']
        read_only_fields = ['is_city_district']


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name', 'administrative_center']
