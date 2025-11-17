from rest_framework import serializers
from django.conf import settings
from ..models import Video
import os

class VideoSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ('id', 'title', 'description', 'category', 'created_at', 'thumbnail_url')

    # def get_thumbnail_url(self, obj):
    #     thumbnail_path = os.path.join(settings.MEDIA_ROOT, "thumbnails", f"{obj.id}.jpg")
    #     if os.path.exists(thumbnail_path):
    #         return settings.MEDIA_URL + f"thumbnails/{obj.id}.jpg"
    #     return None

    def get_thumbnail_url(self, obj):
        thumbnail_path = os.path.join(settings.MEDIA_ROOT, "thumbnails", f"{obj.id}.jpg")
        if os.path.exists(thumbnail_path):
            request = self.context.get('request')
            if request:
                # absolute URL inkl. Backend-Host + Port
                return request.build_absolute_uri(settings.MEDIA_URL + f"thumbnails/{obj.id}.jpg")
            else:
                # Fallback: nur relative URL
                return settings.MEDIA_URL + f"thumbnails/{obj.id}.jpg"
        return None
