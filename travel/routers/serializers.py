from rest_framework import serializers

from .models import Router


class RouterListSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source="district.name", read_only=True)
    settlement_name = serializers.CharField(source="settlement.name", read_only=True)

    class Meta:
        model = Router
        fields = (
            "id",
            "title",
            "short_description",
            "image",
            "duration",
            "difficulty",
            "district_name",
            "settlement_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")


class RouterDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Router
        fields = (
            "id",
            "title",
            "short_description",
            "full_description",
            "image",
            "duration",
            "difficulty",
            "district_name",
            "settlement_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")
