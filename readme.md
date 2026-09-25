# Konverter Serbaguna

GUI bertema laut untuk mengonversi **Gambar**, **Dokumen**, **Audio**, dan **Video** antar format, masing-masing punya tab sendiri.

## Struktur

- `script/theme.py` - palet warna laut dan ikon jendela, dipakai bersama semua GUI
- `script/common.py` - fungsi utilitas bersama (nama file output unik)
- `script/image_converter.py` - fungsi konversi gambar (JPEG, JPG, PNG, WEBP, SVG)
- `script/document_converter.py` - fungsi konversi dokumen (TXT, PDF, DOCX, HTML, MD)
- `script/audio_converter.py` - fungsi konversi audio (MP3, WAV, OGG, FLAC, AAC, M4A, WMA)
- `script/video_converter.py` - fungsi konversi video (MP4, AVI, MOV, MKV, WEBM, GIF, ekstrak MP3)
- `script/app.py` - GUI utama, menggabungkan keempat modul di atas dalam satu jendela bertab
- `favicon/favicon.ico` - favicon jendela

## Pakai tanpa Python (aplikasi .exe)

Jalankan `build.bat` sekali (di PC yang punya Python) untuk menghasilkan `dist\KonverterSerbaguna.exe`. File itu bisa disalin ke PC mana pun **tanpa Python**. Untuk Audio/Video, taruh `ffmpeg.exe` di folder yang sama dengan `KonverterSerbaguna.exe` (atau pasang ffmpeg di PATH). Hasil konversi disimpan di folder `hasil_konversi` di sebelah exe.

## Instalasi (mode developer)

```
pip install -r requirements.txt
```

Untuk konversi **Audio** dan **Video**, install juga [ffmpeg](https://ffmpeg.org/download.html): taruh `ffmpeg.exe` di folder proyek, atau pastikan bisa dipanggil dari PATH.

Untuk hasil terbaik DOCX ke PDF, Microsoft Word perlu terpasang (dipakai lewat `docx2pdf`). Jika tidak ada, aplikasi otomatis memakai jalur cadangan (ekstrak teks lalu susun ulang jadi PDF/DOCX sederhana).

## Menjalankan

```
python script/app.py
```

Setiap tab (Gambar/Dokumen/Audio/Video) punya alur yang sama: seret & lepas file (atau klik untuk memilih), pilih format tujuan, pilih folder tujuan, lalu klik "Konversi Sekarang".

`image_converter.py` juga masih bisa dijalankan sendiri (`python script/image_converter.py`) sebagai konverter gambar mandiri, memakai tema dan ikon yang sama.

## Note !!!
Python hanya dibutuhkan untuk mem-build atau menjalankan dari source; exe hasil build tidak butuh Python.