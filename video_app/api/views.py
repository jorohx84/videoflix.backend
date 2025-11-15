import os
from django.conf import settings
from django.http import HttpResponse, FileResponse, Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Video
from .serializers import VideoSerializer
from django.shortcuts import get_object_or_404

class VideoListView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            videos = Video.objects.all().order_by('-created_at')
            serializer = VideoSerializer(videos, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": "Internal Server Error", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VideoHLSView(APIView):
    # permission_classes = [IsAuthenticated]

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
    # permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        video = get_object_or_404(Video, id=movie_id)
        segment_path = os.path.join(settings.MEDIA_ROOT, 'hls', str(video.id), resolution, segment)

        if not os.path.exists(segment_path):
            raise Http404("Segment not found")

        return FileResponse(open(segment_path, 'rb'), content_type='video/MP2T')
