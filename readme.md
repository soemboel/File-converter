# Konverter Serbaguna

GUI bertema laut untuk mengonversi **Gambar**, **Dokumen**, **Audio**, dan **Video** antar format, masing-masing punya tab sendiri.

## Struktur

- `theme.py` - palet warna laut dan ikon jendela, dipakai bersama semua GUI
- `common.py` - fungsi utilitas bersama (nama file output unik)
- `image_converter.py` - fungsi konversi gambar (JPEG, JPG, PNG, WEBP, SVG)
- `document_converter.py` - fungsi konversi dokumen (TXT, PDF, DOCX, HTML, MD)
- `audio_converter.py` - fungsi konversi audio (MP3, WAV, OGG, FLAC, AAC, M4A, WMA)
- `video_converter.py` - fungsi konversi video (MP4, AVI, MOV, MKV, WEBM, GIF, ekstrak MP3)
- `app.py` - GUI utama, menggabungkan keempat modul di atas dalam satu jendela bertab
- `favicon/favicon.ico` - favicon jendela

## Instalasi

```
pip install -r requirements.txt
```

Untuk konversi **Audio** dan **Video**, install juga [ffmpeg](https://ffmpeg.org/download.html) dan pastikan `ffmpeg` bisa dipanggil dari PATH (cek dengan `ffmpeg -version` di terminal).

Untuk hasil terbaik DOCX ke PDF, Microsoft Word perlu terpasang (dipakai lewat `docx2pdf`). Jika tidak ada, aplikasi otomatis memakai jalur cadangan (ekstrak teks lalu susun ulang jadi PDF/DOCX sederhana).

## Menjalankan

```
python app.py
```

Setiap tab (Gambar/Dokumen/Audio/Video) punya alur yang sama: seret & lepas file (atau klik untuk memilih), pilih format tujuan, pilih folder tujuan, lalu klik "Konversi Sekarang".

`image_converter.py` juga masih bisa dijalankan sendiri (`python image_converter.py`) sebagai konverter gambar mandiri, memakai tema dan ikon yang sama.
