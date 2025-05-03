from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import Place, PlaceImage


class PlaceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceImage
        fields = ("id", "image", "order")


class PlaceListSerializer(serializers.ModelSerializer):
    images = PlaceImageSerializer(many=True, read_only=True)
    district_name = serializers.CharField(source="district.name", read_only=True)
    settlement_name = serializers.CharField(source="settlement.name", read_only=True)

    class Meta:
        model = Place
        fields = (
            "id",
            "title",
            "short_description",
            "district",
            "district_name",
            "settlement",
            "settlement_name",
            "created_at",
            "updated_at",
            "images",
        )
        read_only_fields = ("created_at", "updated_at")


class PlaceDetailSerializer(serializers.ModelSerializer):
    images = PlaceImageSerializer(many=True, read_only=True)
    district_name = serializers.CharField(source="district.name", read_only=True)
    settlement_name = serializers.CharField(source="settlement.name", read_only=True)

    class Meta:
        model = Place
        fields = (
            "id",
            "title",
            "short_description",
            "full_description",
            "district",
            "district_name",
            "settlement",
            "settlement_name",
            "created_at",
            "updated_at",
            "images",
        )
        read_only_fields = ("created_at", "updated_at")

    def validate(self, data):
        if not data.get("district") and not data.get("settlement"):
            raise ValidationError(
                "Место должно иметь либо район, либо населенный пункт"
            )
        return data
