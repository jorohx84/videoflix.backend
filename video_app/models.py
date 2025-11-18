from django.db import models


class Video(models.Model):
    """
    Represents a video in the Videoflix platform.

    This model stores metadata about a video, including title, description,
    category, upload date, and file path. It is used to manage video content,
    generate HLS streams, and create thumbnails for the frontend.

    Important fields:
        - title: The title of the video.
        - description: Brief description of the video content.
        - category: The category or genre of the video.
        - file_path: Path to the uploaded video file.
        - created_at: Timestamp when the video was uploaded.
    """
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    file_path = models.FileField(upload_to='videos/')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

     
