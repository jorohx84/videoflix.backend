import os
import subprocess
from django.conf import settings

# ----------------------------
# Thumbnail-Erzeugung
# ----------------------------
def generate_thumbnail(video_path, video_id):
    thumbnail_dir = os.path.join(settings.MEDIA_ROOT, "thumbnails")
    os.makedirs(thumbnail_dir, exist_ok=True)
    thumbnail_path = os.path.join(thumbnail_dir, f"{video_id}.jpg")

    if not os.path.exists(thumbnail_path):
        command = [
            "ffmpeg",
            "-i", video_path,
            "-ss", "00:00:01",
            "-vframes", "1",
            thumbnail_path
        ]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return settings.MEDIA_URL + f"thumbnails/{video_id}.jpg"

# ----------------------------
# HLS-Streams erzeugen
# ----------------------------
def generate_hls_streams(video_path, video_id):
    resolutions = {
        "480p": "854x480",
        "720p": "1280x720",
        "1080p": "1920x1080"
    }

    for res_label, res_dim in resolutions.items():
        output_dir = os.path.join(settings.MEDIA_ROOT, "hls", str(video_id), res_label)
        os.makedirs(output_dir, exist_ok=True)
        manifest_path = os.path.join(output_dir, "index.m3u8")

        if os.path.exists(manifest_path):
            continue  # Skip if already exists

        command = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"scale={res_dim}",
            "-c:a", "aac",
            "-ar", "48000",
            "-b:a", "128k",
            "-c:v", "h264",
            "-profile:v", "main",
            "-crf", "20",
            "-sc_threshold", "0",
            "-g", "48",
            "-keyint_min", "48",
            "-hls_time", "4",
            "-hls_playlist_type", "vod",
            "-hls_segment_filename", os.path.join(output_dir, "segment_%03d.ts"),
            manifest_path
        ]

        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
