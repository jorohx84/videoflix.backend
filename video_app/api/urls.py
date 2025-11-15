from django.urls import path
from .views import VideoListView, VideoHLSView, VideoSegmentView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('video/', VideoListView.as_view(), name='video_list'),
    path('video/<int:movie_id>/<str:resolution>/index.m3u8', VideoHLSView.as_view(), name='video_hls'),
    path('video/<int:movie_id>/<str:resolution>/<str:segment>/', VideoSegmentView.as_view(), name='video_segment'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
