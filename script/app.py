"""
Konverter Serbaguna - GUI untuk mengonversi Gambar, Dokumen, Audio, dan Video.

Setiap jenis file punya modul fungsi konversinya sendiri:
    image_converter.py     -> convert_image()
    document_converter.py  -> convert_document()
    audio_converter.py     -> convert_audio()
    video_converter.py     -> convert_video()

app.py hanya berisi GUI yang menggabungkan semuanya lewat tab, dengan tema warna laut.

Instalasi dependensi (jalankan di terminal / PowerShell):
    pip install -r requirements.txt

Audio & Video butuh ffmpeg terpasang dan tersedia di PATH:
    https://ffmpeg.org/download.html

Menjalankan aplikasi:
    python app.py
"""

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

import audio_converter as audio_mod
import document_converter as document_mod
import image_converter as image_mod
import video_converter as video_mod
from common import app_dir
from theme import COLORS, apply_icon, apply_ocean_theme


class DropZone(tk.Frame):
    """Kotak seret & lepas dengan bingkai warna laut dan efek hover halus."""

    def __init__(self, master, text, on_click):
        super().__init__(master, bg=COLORS["primary"], padx=2, pady=2)
        self.label = tk.Label(
            self,
            text=text,
            bg=COLORS["seafoam"],
            fg=COLORS["primary_dark"],
            font=("Segoe UI", 11),
            height=6,
            justify="center",
            cursor="hand2",
        )
        self.label.pack(fill="both", expand=True)
        self.label.bind("<Button-1>", lambda e: on_click())
        self.label.bind("<Enter>", self._on_enter)
        self.label.bind("<Leave>", self._on_leave)

    def _on_enter(self, _event):
        self.label.configure(bg=COLORS["seafoam_dark"])

    def _on_leave(self, _event):
        self.label.configure(bg=COLORS["seafoam"])

    def register_drop_target(self, callback):
        self.label.drop_target_register(DND_FILES)
        self.label.dnd_bind("<<Drop>>", callback)


class ConverterTab(ttk.Frame):
    """Tab konversi generik yang dipakai ulang untuk tiap jenis file."""

    def __init__(self, master, *, icon, label, extensions_label, input_extensions,
                 output_formats, convert_func, detect_func, default_format,
                 default_subdir):
        super().__init__(master, padding=16)
        self.input_extensions = input_extensions
        self.convert_func = convert_func
        self.detect_func = detect_func

        self.files = []
        self.output_dir = tk.StringVar(
            value=os.path.join(app_dir(), "hasil_konversi", default_subdir)
        )
        self.target_format = tk.StringVar(value=default_format)

        self._build_ui(icon, label, extensions_label, output_formats)

    # ---------- UI ----------
    def _build_ui(self, icon, label, extensions_label, output_formats):
        subtitle_text = f"Seret & lepas file {label.lower()} di kotak bawah, atau klik untuk memilih file."
        if not DND_AVAILABLE:
            subtitle_text += "\n(Drag & drop nonaktif, install 'tkinterdnd2' untuk mengaktifkan)"
        ttk.Label(self, text=subtitle_text, style="Subtitle.TLabel").pack(anchor="w", pady=(0, 10))

        drop_text = f"{icon}  Tarik & lepas file {label.lower()} di sini\n({extensions_label})\natau klik untuk memilih file"
        self.drop_zone = DropZone(self, drop_text, self.browse_files)
        self.drop_zone.pack(fill="x", pady=(0, 12))
        if DND_AVAILABLE:
            self.drop_zone.register_drop_target(self.on_drop)

        list_frame = ttk.Frame(self)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))

        columns = ("file", "format")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        self.tree.heading("file", text="File")
        self.tree.heading("format", text="Format Terdeteksi")
        self.tree.column("file", width=380)
        self.tree.column("format", width=140, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        list_buttons = ttk.Frame(self)
        list_buttons.pack(fill="x", pady=(0, 12))
        ttk.Button(list_buttons, text="Tambah File...", command=self.browse_files).pack(side="left")
        ttk.Button(list_buttons, text="Hapus Terpilih", command=self.remove_selected).pack(side="left", padx=6)
        ttk.Button(list_buttons, text="Kosongkan", command=self.clear_files).pack(side="left")

        target_frame = ttk.LabelFrame(self, text="Tujuan Konversi", padding=12)
        target_frame.pack(fill="x", pady=(0, 14))

        ttk.Label(target_frame, text="Format tujuan:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        format_combo = ttk.Combobox(
            target_frame,
            textvariable=self.target_format,
            values=output_formats,
            state="readonly",
            width=18,
        )
        format_combo.grid(row=0, column=1, sticky="w")

        ttk.Label(target_frame, text="Folder tujuan:").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=(10, 0))
        output_entry = ttk.Entry(target_frame, textvariable=self.output_dir)
        output_entry.grid(row=1, column=1, sticky="ew", pady=(10, 0))
        ttk.Button(target_frame, text="Pilih...", command=self.browse_output_dir).grid(
            row=1, column=2, padx=(6, 0), pady=(10, 0)
        )
        target_frame.columnconfigure(1, weight=1)

        action_frame = ttk.Frame(self)
        action_frame.pack(fill="x")
        self.convert_btn = ttk.Button(
            action_frame, text=f"{icon} Konversi Sekarang", style="Convert.TButton", command=self.start_conversion
        )
        self.convert_btn.pack(side="left")

        self.progress = ttk.Progressbar(action_frame, mode="determinate")
        self.progress.pack(side="left", fill="x", expand=True, padx=(14, 0))

        self.status_var = tk.StringVar(value="Siap.")
        ttk.Label(self, textvariable=self.status_var, style="Muted.TLabel").pack(anchor="w", pady=(10, 0))

    # ---------- Actions ----------
    def on_drop(self, event):
        paths = self.winfo_toplevel().tk.splitlist(event.data)
        self.add_files(paths)

    def browse_files(self):
        patterns = " ".join(f"*{ext}" for ext in sorted(self.input_extensions))
        filetypes = [("File Didukung", patterns), ("Semua File", "*.*")]
        paths = filedialog.askopenfilenames(title="Pilih file", filetypes=filetypes)
        if paths:
            self.add_files(paths)

    def add_files(self, paths):
        added = 0
        for path in paths:
            path = path.strip("{}")
            ext = os.path.splitext(path)[1].lower()
            if ext not in self.input_extensions:
                continue
            if path in self.files:
                continue
            self.files.append(path)
            fmt = self.detect_func(path)
            self.tree.insert("", "end", values=(os.path.basename(path), fmt), tags=(path,))
            added += 1
        if added:
            self.status_var.set(f"{added} file ditambahkan.")
        else:
            self.status_var.set("Tidak ada file yang valid ditambahkan.")

    def remove_selected(self):
        selected = self.tree.selection()
        for item in selected:
            values = self.tree.item(item, "values")
            filename = values[0]
            self.files = [f for f in self.files if os.path.basename(f) != filename]
            self.tree.delete(item)

    def clear_files(self):
        self.files.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.status_var.set("Daftar file dikosongkan.")

    def browse_output_dir(self):
        chosen = filedialog.askdirectory(title="Pilih folder tujuan")
        if chosen:
            self.output_dir.set(chosen)

    def start_conversion(self):
        if not self.files:
            messagebox.showwarning("Tidak ada file", "Tambahkan minimal satu file terlebih dahulu.")
            return

        target_format = self.target_format.get()
        output_dir = self.output_dir.get().strip()
        if not output_dir:
            messagebox.showwarning("Folder tujuan kosong", "Pilih folder tujuan terlebih dahulu.")
            return
        os.makedirs(output_dir, exist_ok=True)

        self.convert_btn.config(state="disabled")
        self.progress.config(maximum=len(self.files), value=0)
        self.status_var.set("Mengonversi...")

        thread = threading.Thread(
            target=self._convert_worker, args=(list(self.files), output_dir, target_format), daemon=True
        )
        thread.start()

    def _convert_worker(self, files, output_dir, target_format):
        success, failed = 0, []
        for i, path in enumerate(files, start=1):
            try:
                self.convert_func(path, output_dir, target_format)
                success += 1
            except Exception as exc:  # noqa: BLE001 - tampilkan error apapun ke user
                failed.append(f"{os.path.basename(path)}: {exc}")
            self.after(0, self._update_progress, i)

        self.after(0, self._conversion_done, success, failed, output_dir)

    def _update_progress(self, value):
        self.progress.config(value=value)

    def _conversion_done(self, success, failed, output_dir):
        self.convert_btn.config(state="normal")
        if failed:
            self.status_var.set(f"Selesai: {success} berhasil, {len(failed)} gagal.")
            messagebox.showerror("Beberapa file gagal dikonversi", "\n".join(failed))
        else:
            self.status_var.set(f"Selesai! {success} file berhasil dikonversi ke: {output_dir}")
            messagebox.showinfo("Selesai", f"{success} file berhasil dikonversi ke:\n{output_dir}")


class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Konverter Serbaguna")
        self.root.geometry("760x900")
        self.root.minsize(680, 760)

        apply_ocean_theme(root)
        apply_icon(root)

        self._build_header()

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        notebook.add(
            ConverterTab(
                notebook,
                icon="🖼",
                label="Gambar",
                extensions_label="JPEG, JPG, PNG, WEBP, SVG",
                input_extensions=image_mod.SUPPORTED_INPUT_EXTENSIONS,
                output_formats=image_mod.SUPPORTED_OUTPUT_FORMATS,
                convert_func=image_mod.convert_image,
                detect_func=image_mod.detect_format,
                default_format="PNG",
                default_subdir="gambar",
            ),
            text=" 🖼  Gambar ",
        )
        notebook.add(
            ConverterTab(
                notebook,
                icon="📄",
                label="Dokumen",
                extensions_label="TXT, PDF, DOCX, HTML, MD",
                input_extensions=document_mod.SUPPORTED_INPUT_EXTENSIONS,
                output_formats=document_mod.SUPPORTED_OUTPUT_FORMATS,
                convert_func=document_mod.convert_document,
                detect_func=document_mod.detect_format,
                default_format="PDF",
                default_subdir="dokumen",
            ),
            text=" 📄  Dokumen ",
        )
        notebook.add(
            ConverterTab(
                notebook,
                icon="🎵",
                label="Audio",
                extensions_label="MP3, WAV, OGG, FLAC, AAC, M4A, WMA",
                input_extensions=audio_mod.SUPPORTED_INPUT_EXTENSIONS,
                output_formats=audio_mod.SUPPORTED_OUTPUT_FORMATS,
                convert_func=audio_mod.convert_audio,
                detect_func=audio_mod.detect_format,
                default_format="MP3",
                default_subdir="audio",
            ),
            text=" 🎵  Audio ",
        )
        notebook.add(
            ConverterTab(
                notebook,
                icon="🎬",
                label="Video",
                extensions_label="MP4, AVI, MOV, MKV, WEBM",
                input_extensions=video_mod.SUPPORTED_INPUT_EXTENSIONS,
                output_formats=video_mod.SUPPORTED_OUTPUT_FORMATS,
                convert_func=video_mod.convert_video,
                detect_func=video_mod.detect_format,
                default_format="MP4",
                default_subdir="video",
            ),
            text=" 🎬  Video ",
        )

        if not audio_mod.FFMPEG_AVAILABLE or not video_mod.FFMPEG_AVAILABLE:
            self.root.after(300, self._warn_ffmpeg)

    def _build_header(self):
        header = ttk.Frame(self.root, padding=(20, 18, 20, 10))
        header.pack(fill="x")

        title_row = ttk.Frame(header)
        title_row.pack(fill="x")
        ttk.Label(title_row, text="🌊 Konverter Serbaguna", style="Title.TLabel").pack(side="left")

        ttk.Label(
            header,
            text="Ubah gambar, dokumen, audio, dan video ke format lain dalam beberapa klik.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        wave = tk.Frame(self.root, height=4, bg=COLORS["accent"])
        wave.pack(fill="x")

    def _warn_ffmpeg(self):
        messagebox.showwarning(
            "ffmpeg tidak ditemukan",
            "Konversi Audio dan Video membutuhkan ffmpeg.\n\n"
            "Install ffmpeg dan pastikan ada di PATH sistem:\n"
            "https://ffmpeg.org/download.html",
        )


def main():
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    ConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
