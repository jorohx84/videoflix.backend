from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..models import Video
from .serializers import VideoSerializer

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
