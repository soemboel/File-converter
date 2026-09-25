"""
Konverter Video - fungsi-fungsi untuk mengonversi video antar format.

Format didukung: MP4, AVI, MOV, MKV, WEBM, GIF
Bonus: ekstrak audio ke MP3.

Membutuhkan ffmpeg (di sebelah aplikasi atau di PATH sistem).
Download: https://ffmpeg.org/download.html
"""

import os
from common import find_ffmpeg, run_ffmpeg, unique_output_path

FFMPEG_AVAILABLE = find_ffmpeg() is not None

SUPPORTED_OUTPUT_FORMATS = ["MP4", "AVI", "MOV", "MKV", "WEBM", "GIF", "MP3 (Ekstrak Audio)"]
SUPPORTED_INPUT_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv"}

EXT_TO_FORMAT = {ext: ext[1:].upper() for ext in SUPPORTED_INPUT_EXTENSIONS}

# Codec ffmpeg yang cocok untuk tiap format video tujuan
_CODEC_ARGS = {
    "MP4": ["-codec:v", "libx264", "-codec:a", "aac"],
    "AVI": ["-codec:v", "mpeg4", "-codec:a", "mp3"],
    "MOV": ["-codec:v", "libx264", "-codec:a", "aac"],
    "MKV": ["-codec:v", "libx264", "-codec:a", "aac"],
    "WEBM": ["-codec:v", "libvpx-vp9", "-codec:a", "libopus"],
}


def detect_format(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    return EXT_TO_FORMAT.get(ext, ext.lstrip(".").upper() or "?")


def convert_video(input_path, output_dir, target_format):
    """Konversi satu file video menggunakan ffmpeg. Mengembalikan path file hasil."""
    base_name = os.path.splitext(os.path.basename(input_path))[0]

    if target_format.upper().startswith("MP3"):
        output_path = unique_output_path(output_dir, base_name, ".mp3")
        cmd = [
            "-y", "-i", input_path,
            "-vn", "-codec:a", "libmp3lame", "-qscale:a", "2",
            output_path,
        ]
    else:
        target_format = target_format.upper()
        ext = f".{target_format.lower()}"
        output_path = unique_output_path(output_dir, base_name, ext)
        cmd = ["-y", "-i", input_path]
        if target_format == "GIF":
            cmd += ["-vf", "fps=10,scale=480:-1:flags=lanczos"]
        else:
            cmd += _CODEC_ARGS.get(target_format, [])
        cmd.append(output_path)

    run_ffmpeg(cmd)
    return output_path
