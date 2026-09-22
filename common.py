"""Fungsi utilitas bersama yang dipakai oleh semua modul konverter."""

import os


def unique_output_path(output_dir, base_name, ext):
    """Bangun path output di output_dir dari base_name+ext, hindari menimpa file yang sudah ada."""
    output_path = os.path.join(output_dir, f"{base_name}{ext}")
    counter = 1
    while os.path.exists(output_path):
        output_path = os.path.join(output_dir, f"{base_name}_{counter}{ext}")
        counter += 1
    return output_path
