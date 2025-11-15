from django.db import models
from django.conf import settings
import os
from .api.utils import generate_thumbnail, generate_hls_streams

class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    file_path = models.FileField(upload_to='videos/')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Thumbnail erzeugen, falls fehlt
        if not self.thumbnail_url and self.file_path:
            self.thumbnail_url = generate_thumbnail(self.file_path.path, self.id)
            super().save(update_fields=['thumbnail_url'])

        # HLS-Streams erzeugen
        if self.file_path:
            generate_hls_streams(self.file_path.path, self.id)
