from rest_framework import serializers

from .models import RouteGenerationJob, Router


class RouteGenerateRequestSerializer(serializers.Serializer):
    user_text = serializers.CharField(required=True, allow_blank=True)
    district_id = serializers.IntegerField(required=False, allow_null=True)
    settlement_id = serializers.IntegerField(required=False, allow_null=True)


class RouteGenerateStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[c[0] for c in RouteGenerationJob.Status.choices])
    router_id = serializers.IntegerField(allow_null=True)
    error_message = serializers.CharField(allow_null=True)


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
            "creation_method",
            "district_name",
            "settlement_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")


class RouterDetailSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source="district.name", read_only=True)
    settlement_name = serializers.CharField(source="settlement.name", read_only=True)

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
            "creation_method",
            "district_name",
            "settlement_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")
