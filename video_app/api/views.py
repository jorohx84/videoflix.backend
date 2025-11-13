from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..models import Video
from .serializers import VideoSerializer
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import os
import ffmpeg
from django.conf import settings
from django.http import FileResponse, Http404

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
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        video = get_object_or_404(Video, id=movie_id)
        
        input_video_path = getattr(video, 'file_path', None) 
        if not input_video_path or not os.path.exists(input_video_path):
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

        hls_dir = os.path.join(settings.MEDIA_ROOT, 'hls', str(video.id), resolution)
        os.makedirs(hls_dir, exist_ok=True)

        manifest_path = os.path.join(hls_dir, 'index.m3u8')

        if not os.path.exists(manifest_path):
            try:
                resolutions = {
                    '480p': {'width': 854, 'height': 480, 'bitrate': '800k'},
                    '720p': {'width': 1280, 'height': 720, 'bitrate': '2800k'},
                    '1080p': {'width': 1920, 'height': 1080, 'bitrate': '5000k'},
                }

                if resolution not in resolutions:
                    return HttpResponse(status=status.HTTP_404_NOT_FOUND)

                opts = resolutions[resolution]
                output_pattern = os.path.join(hls_dir, 'segment_%03d.ts')

                (
                    ffmpeg
                    .input(input_video_path)
                    .output(
                        manifest_path,
                        format='hls',
                        hls_time=10,
                        hls_playlist_type='vod',
                        hls_segment_filename=output_pattern,
                        video_bitrate=opts['bitrate'],
                        vf=f"scale={opts['width']}:{opts['height']}"
                    )
                    .run(overwrite_output=True)
                )
            except ffmpeg.Error as e:
                return HttpResponse(f"ffmpeg error: {e.stderr.decode()}", status=500)

        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                content = f.read()
            response = HttpResponse(content, content_type='application/vnd.apple.mpegurl')
            return response
        else:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

class VideoSegmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
   
        video = get_object_or_404(Video, id=movie_id)

        hls_dir = os.path.join('media', 'hls', str(video.id), resolution)
        segment_path = os.path.join(hls_dir, segment)

        if not os.path.exists(segment_path):
            raise Http404("Segment not found")

        return FileResponse(open(segment_path, 'rb'), content_type='video/MP2T')