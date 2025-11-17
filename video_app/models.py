

from django.db import models
from django_rq import enqueue
from .api.utils import generate_thumbnail, generate_hls_streams

class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    file_path = models.FileField(upload_to='videos/')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

     
