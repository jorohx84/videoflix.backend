import os
from django.conf import settings
from rest_framework import serializers
from ..models import Video

class VideoSerializer(serializers.ModelSerializer):
    """
    Serializer for the Video model, including a dynamically generated thumbnail URL.

    This serializer exposes basic video fields (`id`, `title`, `description`,
    `category`, `created_at`) and adds a `thumbnail_url` field. The `thumbnail_url`
    is computed based on the presence of a thumbnail file in the media directory
    and returns an absolute URL if a request context is available.

    Methods:
        get_thumbnail_url(obj):
            Returns the absolute URL of the video's thumbnail if it exists,
            or None if no thumbnail is found.
    """
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ('id', 'title', 'description', 'category', 'created_at', 'thumbnail_url')

    def get_thumbnail_url(self, obj):

        thumbnail_path = os.path.join(settings.MEDIA_ROOT, "thumbnails", f"{obj.id}.jpg")
        if os.path.exists(thumbnail_path):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(settings.MEDIA_URL + f"thumbnails/{obj.id}.jpg")
            else:
                return settings.MEDIA_URL + f"thumbnails/{obj.id}.jpg"
        return None



  