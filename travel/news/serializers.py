from rest_framework import serializers
from .models import News


class NewsSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = News
        fields = ['id', 'title', 'image', 'description', 'content', 'created_at', 'created_by']
