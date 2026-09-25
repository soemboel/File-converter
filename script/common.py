"""Fungsi utilitas bersama yang dipakai oleh semua modul konverter."""

import os
import shutil
import subprocess
import sys


def unique_output_path(output_dir, base_name, ext):
    """Bangun path output di output_dir dari base_name+ext, hindari menimpa file yang sudah ada."""
    output_path = os.path.join(output_dir, f"{base_name}{ext}")
    counter = 1
    while os.path.exists(output_path):
        output_path = os.path.join(output_dir, f"{base_name}_{counter}{ext}")
        counter += 1
    return output_path


def app_dir():
    """Folder aplikasi: folder .exe saat sudah di-build, folder proyek saat dijalankan dari source."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resource_path(*parts):
    """Path resource bawaan (favicon dll), baik dari source maupun dari bundle PyInstaller."""
    base = getattr(sys, "_MEIPASS", None) or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *parts)


def find_ffmpeg():
    """Cari ffmpeg: di sebelah aplikasi (ffmpeg.exe / ffmpeg/ffmpeg.exe) dulu, lalu PATH."""
    name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    for candidate in (os.path.join(app_dir(), name), os.path.join(app_dir(), "ffmpeg", name)):
        if os.path.isfile(candidate):
            return candidate
    return shutil.which("ffmpeg")


def run_ffmpeg(args):
    """Jalankan ffmpeg tanpa memunculkan jendela console. Melempar RuntimeError jika gagal."""
    exe = find_ffmpeg()
    if not exe:
        raise RuntimeError(
            "ffmpeg tidak ditemukan. Taruh ffmpeg.exe di folder yang sama dengan aplikasi "
            "atau install ke PATH: https://ffmpeg.org/download.html"
        )
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    result = subprocess.run(
        [exe, *args], capture_output=True, text=True, errors="replace", creationflags=flags
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg gagal: {result.stderr[-500:]}")
