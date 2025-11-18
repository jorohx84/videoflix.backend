from django.conf import settings
from rest_framework import serializers
from ..models import Video
import os

class VideoSerializer(serializers.ModelSerializer):
    """
    Serializer for the Video model, including a thumbnail URL.
    
    The `thumbnail_url` field is a read-only field computed via `get_thumbnail_url`.
    It handles both manually uploaded thumbnails and automatically generated ones:

        1. If a manual thumbnail is uploaded (`obj.thumbnail`), its URL is returned.
        2. If no manual thumbnail exists, the serializer checks for an automatically
           generated thumbnail in `MEDIA_ROOT/thumbnails/<video_id>.jpg`.
        3. If the file exists, it returns an absolute URL (using `request` if available),
           otherwise it returns None.

    Notes:
        - The automatic thumbnail must already exist in the filesystem; this serializer
          does not trigger thumbnail generation.
        - The absolute URL depends on the request context being provided to the serializer.

    Methods:
        get_thumbnail_url(obj): Computes the absolute URL for the video's thumbnail.
    """
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ('id', 'title', 'description', 'category', 'created_at', 'thumbnail_url')

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')

        # 1️⃣ Manuelles Thumbnail hat Priorität
        if obj.thumbnail and obj.thumbnail.name:
            url_path = obj.thumbnail.url
        else:
            # 2️⃣ Automatisch generiertes Thumbnail
            thumbnail_path = os.path.join(settings.MEDIA_ROOT, "thumbnails", f"{obj.id}.jpg")
            if not os.path.exists(thumbnail_path):
                return None
            url_path = settings.MEDIA_URL + f"thumbnails/{obj.id}.jpg"  # <-- MEDIA_URL davor

        # Absolute URL
        if request:
            return request.build_absolute_uri(url_path)
        return url_path
