"""
Konverter Audio - fungsi-fungsi untuk mengonversi audio antar format.

Format didukung: MP3, WAV, OGG, FLAC, AAC, M4A, WMA

Membutuhkan ffmpeg (di sebelah aplikasi atau di PATH sistem).
Download: https://ffmpeg.org/download.html
"""

import os
from common import find_ffmpeg, run_ffmpeg, unique_output_path

FFMPEG_AVAILABLE = find_ffmpeg() is not None

SUPPORTED_OUTPUT_FORMATS = ["MP3", "WAV", "OGG", "FLAC", "AAC", "M4A", "WMA"]
SUPPORTED_INPUT_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a", ".wma"}

EXT_TO_FORMAT = {ext: ext[1:].upper() for ext in SUPPORTED_INPUT_EXTENSIONS}

# Codec ffmpeg yang cocok untuk tiap format tujuan
_CODEC_ARGS = {
    "MP3": ["-codec:a", "libmp3lame", "-qscale:a", "2"],
    "AAC": ["-codec:a", "aac", "-b:a", "192k"],
    "M4A": ["-codec:a", "aac", "-b:a", "192k"],
    "WMA": ["-codec:a", "wmav2"],
    "OGG": ["-codec:a", "libvorbis", "-qscale:a", "5"],
    "FLAC": ["-codec:a", "flac"],
    "WAV": ["-codec:a", "pcm_s16le"],
}


def detect_format(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    return EXT_TO_FORMAT.get(ext, ext.lstrip(".").upper() or "?")


def convert_audio(input_path, output_dir, target_format):
    """Konversi satu file audio menggunakan ffmpeg. Mengembalikan path file hasil."""
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    target_format = target_format.upper()
    ext = f".{target_format.lower()}"
    output_path = unique_output_path(output_dir, base_name, ext)

    run_ffmpeg(["-y", "-i", input_path, *_CODEC_ARGS.get(target_format, []), output_path])
    return output_path
