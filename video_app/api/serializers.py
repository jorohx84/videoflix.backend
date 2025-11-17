
from rest_framework import serializers
from django.conf import settings
from ..models import Video
import os

class VideoSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ('id', 'title', 'description', 'category', 'created_at', 'thumbnail_url')

    def get_thumbnail_url(self, obj):
        thumbnail_path = os.path.join(settings.MEDIA_ROOT, "thumbnails", f"{obj.id}.jpg")
        if os.path.exists(thumbnail_path):
            return settings.MEDIA_URL + f"thumbnails/{obj.id}.jpg"
        return None
