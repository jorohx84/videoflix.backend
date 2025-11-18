from django.db.models.signals import post_save
from django.dispatch import receiver
from django_rq import enqueue
from .models import Video
from .api.utils import generate_hls_streams, generate_thumbnail

@receiver(post_save, sender=Video)
def start_video_processing(sender, instance, created, **kwargs):
    """
    Trigger background processing tasks after a Video instance is created.

    This signal handler listens for the `post_save` event of the Video model.
    When a new Video is created with an uploaded file, it enqueues the following
    asynchronous tasks using Django RQ:

        1. `generate_hls_streams`: Converts the uploaded video into HLS format.
        2. `generate_thumbnail`: Generates a thumbnail image for the video,
           but only if no manual thumbnail has been uploaded.

    Args:
        sender (type): The model class that sent the signal (Video).
        instance (Video): The actual instance of the Video that was saved.
        created (bool): True if a new record was created; False if updated.
        **kwargs: Additional keyword arguments passed by the signal.
    """
    if created and instance.file_path:
        enqueue(generate_hls_streams, instance.file_path.path, instance.id)

        if not instance.thumbnail or not bool(instance.thumbnail.name):
            enqueue(generate_thumbnail, instance.file_path.path, instance.id)


