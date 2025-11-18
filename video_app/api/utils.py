import os
import subprocess
from django.conf import settings

def generate_thumbnail(video_path, video_id):
    """
    Generates a thumbnail image for a video file and returns its URL.

    This function checks if a thumbnail already exists for the given video ID.
    If not, it uses ffmpeg to capture a single frame at 1 second into the video
    and saves it as a JPEG file in the `MEDIA_ROOT/thumbnails` directory. The
    function returns the relative URL to access the thumbnail.

    Args:
        video_path (str): The file system path to the video file.
        video_id (int or str): The unique identifier for the video, used to
                               name the thumbnail file.

    Returns:
        str: The URL of the generated or existing thumbnail image.

    Notes:
        - Requires `ffmpeg` to be installed and accessible in the system path.
        - Prints an error message if thumbnail generation fails.
    """
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
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print(f"[Thumbnail Error] {result.stderr.decode()}")

    return settings.MEDIA_URL + f"thumbnails/{video_id}.jpg"



def generate_hls_streams(video_path, video_id):
    """
    Generates HLS (HTTP Live Streaming) video streams at multiple resolutions.

    This function creates adaptive bitrate HLS streams (480p, 720p, 1080p)
    from the input video using ffmpeg. Each resolution is stored in a
    separate directory under `MEDIA_ROOT/hls/<video_id>/<resolution>/`, with
    segment files and an `index.m3u8` playlist. Existing playlists are not
    regenerated.

    Args:
        video_path (str): The file system path to the source video file.
        video_id (int or str): The unique identifier for the video, used to
                               organize HLS output directories.

    Notes:
        - Requires `ffmpeg` to be installed and accessible in the system path.
        - Prints an error message if stream generation fails for any resolution.
        - Segments are encoded with H.264 for video and AAC for audio, with
          VOD-compatible HLS playlists.
    """
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
            continue

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
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print(f"[HLS Error] {result.stderr.decode()}")
