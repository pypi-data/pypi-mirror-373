import subprocess
import shlex
from dataclasses import dataclass

def get_video_codec(input_file: str) -> str:
    """
    Returns the codec name of the first video stream in the file.
    If no video stream is found, returns 'UNKNOWN'.
    """
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=codec_name",
            "-of", "default=noprint_wrappers=1:nokey=1",
            input_file
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        codec = result.stdout.strip()
        return codec if codec else "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def get_audio_codec(input_file: str) -> str:
    """
    Returns the codec name of the first audio stream in the file.
    If no audio stream is found, returns 'NONE'.
    """
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=codec_name",
            "-of", "default=noprint_wrappers=1:nokey=1",
            input_file
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        codec = result.stdout.strip()
        return codec if codec else "NONE"
    except Exception:
        return "NONE"

def seconds_to_hms(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format for ffmpeg."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{secs:02}"

def get_video_duration(file_path: str) -> float:
    """
    Returns video duration in seconds as a float.
    """
    result = subprocess.run(
        [
            "ffprobe", 
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            file_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return float(result.stdout.strip())

@dataclass
class MediaInfo:
    video_codec: str
    audio_codec: str
    duration_seconds: float
    duration_hms: str

def get_media_info(file_path: str) -> MediaInfo:
    
    audio_codec = get_audio_codec(file_path)
    video_codec = get_video_codec(file_path)
    duration_sec = get_video_duration(file_path)

    return MediaInfo(
        audio_codec=audio_codec,
        video_codec=video_codec,
        duration_seconds=duration_sec,
        duration_hms=seconds_to_hms(duration_sec)
    )


    
def build_ffmpeg_command(input_file: str, output_file: str, video_codec: str, audio_codec:str =None, offsetInSeconds:int=0, durationInSeconds:int=0):
    """
    Build ffmpeg command for Hikvision .dav/.mp4 conversion with normalization.
    - Normalizes video: max 1080p, max 4 Mbps
    - Normalizes audio: AAC 128k
    """

    # ----- VIDEO CODEC MAPPING -----
    video_map = {
        "MPEG4-SP":  "-c:v libx264 -preset fast -crf 23",
        "MPEG4-ASP": "-c:v libx264 -preset fast -crf 23",
        "MPEG4-MP":  "-c:v libx264 -preset fast -crf 23",
        "H.264-BP":  "-c:v copy",   # already compatible
        "H.264-MP":  "-c:v copy",
        "H.264-HP":  "-c:v copy",
        "H.264SVC-BP": "-c:v libx264 -preset fast -crf 23",  # not widely supported
        "H.264SVC-MP": "-c:v libx264 -preset fast -crf 23",
        "MPEG2-MP": "-c:v libx264 -preset fast -crf 23",
        "MJPEG":    "-c:v libx264 -preset fast -crf 23",
        "JPEG":     "-c:v libx264 -preset fast -crf 23",
        "JPEG2000": "-c:v libx264 -preset fast -crf 23",
        "UNKNOWN":  "-c:v libx264 -preset fast -crf 23"
    }

    # Add scaling & bitrate normalization (applies to all encodes, not copies)
    normalize_flags = "-vf \"scale='min(1920,iw)':'min(1080,ih)'\" -maxrate 4M -bufsize 8M -pix_fmt yuv420p"

    video_cmd = video_map.get(video_codec, video_map["UNKNOWN"])
    if "copy" not in video_cmd:
        video_cmd = f"{video_cmd} {normalize_flags}"

    # ----- AUDIO CODEC MAPPING -----
    audio_map = {
        "pcm_mulaw": "-c:a aac -b:a 128k",
        "pcm_alaw":  "-c:a aac -b:a 128k",
        "aac":       "-c:a copy",
        "mp3":       "-c:a copy",
        "g711":      "-c:a aac -b:a 128k",
        "g711a":     "-c:a aac -b:a 128k",
        "g711u":     "-c:a aac -b:a 128k",
        "g726":      "-c:a aac -b:a 128k",
        "g723":      "-c:a aac -b:a 128k",
        "g729":      "-c:a aac -b:a 128k",
        "UNKNOWN":   "-c:a aac -b:a 128k"
    }

    if audio_codec is None:
        audio_cmd = "-an"  # no audio
    else:
        audio_cmd = audio_map.get(audio_codec.lower(), audio_map["UNKNOWN"])

    trimargs = ""
    
    if offsetInSeconds >= 0:
        trimargs += f"-ss {seconds_to_hms(offsetInSeconds)} "
    if durationInSeconds > 0:
        trimargs += f"-to {seconds_to_hms(durationInSeconds + offsetInSeconds)} "
    else:
        trimargs = ""

    cmd = (
        f"ffmpeg {trimargs} -i {shlex.quote(input_file)} "
        f"{video_cmd} {audio_cmd} "
        f"-movflags +faststart -fflags +genpts "
        f"{shlex.quote(output_file)}"
    )
    return cmd

def convertAndTrim(input_file: str, output_file: str, mediaInfo: MediaInfo, offsetInSeconds:int=0, durationInSeconds:int=0):
    cmd = build_ffmpeg_command(input_file=input_file, output_file=output_file, video_codec=mediaInfo.video_codec, audio_codec=mediaInfo.audio_codec, offsetInSeconds=offsetInSeconds, durationInSeconds=durationInSeconds)
    print("Running command:", cmd)
    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
