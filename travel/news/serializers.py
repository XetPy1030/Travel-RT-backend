from rest_framework import serializers

from .models import News


class NewsSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)

    class Meta:
        model = News
        fields = [
            "id",
            "title",
            "image",
            "description",
            "content",
            "published_at",
            "created_at",
            "created_by",
        ]


class NewsParserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ["title", "image", "description", "content", "published_at"]

    def create(self, validated_data):
        validated_data["creation_method"] = News.CreationMethod.PARSING
        validated_data["created_by"] = None
        return super().create(validated_data)


class NewsParserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ["title", "image", "description", "content", "published_at"]
