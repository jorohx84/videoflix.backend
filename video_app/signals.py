from django.db.models.signals import post_save
from django.dispatch import receiver
from django_rq import enqueue
from .models import Video
from .api.utils import generate_hls_streams, generate_thumbnail

@receiver(post_save, sender=Video)
def start_video_processing(sender, instance, created, **kwargs):
    if created and instance.file_path:
      
        enqueue(generate_hls_streams, instance.file_path.path, instance.id)
        enqueue(generate_thumbnail, instance.file_path.path, instance.id)
