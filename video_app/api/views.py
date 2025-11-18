import os
from django.conf import settings
from django.http import FileResponse, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import Video
from .serializers import VideoSerializer


class VideoListView(APIView):
    """
    API view to retrieve a list of all videos.

    This view returns all video objects ordered by creation date (newest first)
    and serializes them using `VideoSerializer`. The serializer receives the
    request context to generate absolute URLs for video thumbnails.

    Attributes:
        permission_classes (list): Restricts access to authenticated users only.

    Methods:
        get(request):
            Handles GET requests to fetch the list of videos. Returns serialized
            video data on success, or a 500 error response if an exception occurs.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            videos = Video.objects.all().order_by('-created_at')
            # serializer = VideoSerializer(videos, many=True)
            serializer = VideoSerializer(videos, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": "Internal Server Error", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VideoHLSView(APIView):
    """
    API view to serve HLS (HTTP Live Streaming) manifests for a specific video.

    This view retrieves the HLS manifest (`index.m3u8`) for the requested
    video and resolution. The user must be authenticated. If the video file
    or manifest does not exist, a 404 error is raised.

    Attributes:
        permission_classes (list): Restricts access to authenticated users only.

    Methods:
        get(request, movie_id, resolution):
            Handles GET requests to return the HLS manifest content for the
            specified video and resolution. Returns the manifest with the
            correct MIME type for HLS playback.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        video = get_object_or_404(Video, id=movie_id)
        input_video_path = video.file_path.path

        if not os.path.exists(input_video_path):
            raise Http404("Video-Datei nicht gefunden")

        manifest_path = os.path.join(settings.MEDIA_ROOT, 'hls', str(video.id), resolution, 'index.m3u8')
        if not os.path.exists(manifest_path):
            raise Http404("Manifest nicht gefunden")

        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_content = f.read()

        return HttpResponse(manifest_content, content_type='application/vnd.apple.mpegurl')



class VideoSegmentView(APIView):
    """
    API view to serve individual HLS video segments for streaming.

    This view retrieves a specific HLS segment file (`.ts`) for a given video
    and resolution. The user must be authenticated. If the segment file does
    not exist, a 404 error is raised.

    Attributes:
        permission_classes (list): Restricts access to authenticated users only.

    Methods:
        get(request, movie_id, resolution, segment):
            Handles GET requests to return the requested HLS segment file with
            the appropriate MIME type for HLS playback.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        video = get_object_or_404(Video, id=movie_id)
        segment_path = os.path.join(settings.MEDIA_ROOT, 'hls', str(video.id), resolution, segment)

        if not os.path.exists(segment_path):
            raise Http404("Segment not found")

        return FileResponse(open(segment_path, 'rb'), content_type='video/MP2T')
