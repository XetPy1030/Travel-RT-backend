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
