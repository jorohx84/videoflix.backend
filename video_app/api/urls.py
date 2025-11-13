from django.urls import path
from .views import VideoListView, VideoHLSView, VideoSegmentView

urlpatterns = [
    path('video/', VideoListView.as_view(), name='video_list'),
    path('video/<int:movie_id>/<str:resolution>/index.m3u8', VideoHLSView.as_view(), name='video_hls'),
    path('video/<int:movie_id>/<str:resolution>/<str:segment>/', VideoSegmentView.as_view(), name='video_segment'),

]
