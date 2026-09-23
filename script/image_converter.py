"""
Konverter Gambar - GUI sederhana untuk mengonversi gambar antar format.

Fitur:
- Drag & drop file gambar (butuh library tkinterdnd2), atau tombol "Tambah File".
- Format sumber terdeteksi otomatis dari file yang dimasukkan.
- Format tujuan bisa dipilih: JPEG, JPG, PNG, WEBP, SVG.

Instalasi dependensi (jalankan di terminal / PowerShell):
    pip install -r requirements.txt

Menjalankan aplikasi:
    python image_converter.py
"""

import base64
import io
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

try:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
    SVG_INPUT_AVAILABLE = True
except ImportError:
    SVG_INPUT_AVAILABLE = False

from theme import COLORS, apply_icon, apply_ocean_theme

SUPPORTED_OUTPUT_FORMATS = ["JPEG", "JPG", "PNG", "WEBP", "SVG"]
SUPPORTED_INPUT_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".svg"}


def detect_format(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    mapping = {
        ".jpg": "JPEG",
        ".jpeg": "JPEG",
        ".png": "PNG",
        ".webp": "WEBP",
        ".svg": "SVG",
    }
    return mapping.get(ext, ext.lstrip(".").upper() or "?")


def load_as_pil_image(file_path):
    """Buka file gambar apapun (termasuk SVG) sebagai PIL.Image."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".svg":
        if not SVG_INPUT_AVAILABLE:
            raise RuntimeError(
                "Untuk membaca SVG, install dulu: pip install svglib reportlab"
            )
        drawing = svg2rlg(file_path)
        buf = io.BytesIO()
        renderPM.drawToFile(drawing, buf, fmt="PNG")
        buf.seek(0)
        return Image.open(buf).convert("RGBA")
    return Image.open(file_path)


def save_as_svg(pil_image, output_path):
    """Simpan gambar raster sebagai SVG dengan membungkusnya (base64 embed).

    Ini bukan vektorisasi asli (raster tetap raster), tapi menghasilkan
    file .svg yang valid dan bisa dibuka di browser / aplikasi vektor.
    """
    buf = io.BytesIO()
    rgb_image = pil_image.convert("RGBA")
    rgb_image.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    width, height = pil_image.size
    svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
     viewBox="0 0 {width} {height}">
  <image width="{width}" height="{height}"
         xlink:href="data:image/png;base64,{encoded}"
         xmlns:xlink="http://www.w3.org/1999/xlink"/>
</svg>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)


def convert_image(input_path, output_dir, target_format):
    """Konversi satu file gambar. Mengembalikan path file hasil."""
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    target_format_norm = "JPEG" if target_format in ("JPEG", "JPG") else target_format
    ext = ".jpg" if target_format == "JPG" else f".{target_format.lower()}"
    output_path = os.path.join(output_dir, f"{base_name}{ext}")

    # Hindari menimpa file dengan nama sama
    counter = 1
    while os.path.exists(output_path):
        output_path = os.path.join(output_dir, f"{base_name}_{counter}{ext}")
        counter += 1

    if target_format_norm == "SVG" and os.path.splitext(input_path)[1].lower() == ".svg":
        # Sudah SVG, salin apa adanya agar tetap vektor asli (tidak dirasterisasi)
        with open(input_path, "r", encoding="utf-8") as src, open(output_path, "w", encoding="utf-8") as dst:
            dst.write(src.read())
        return output_path

    image = load_as_pil_image(input_path)

    if target_format_norm == "SVG":
        save_as_svg(image, output_path)
        return output_path

    if target_format_norm == "JPEG":
        # JPEG tidak mendukung alpha channel, gabungkan ke background putih
        if image.mode in ("RGBA", "LA", "P"):
            image = image.convert("RGBA")
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
        else:
            image = image.convert("RGB")
        image.save(output_path, format="JPEG", quality=95)
    elif target_format_norm == "WEBP":
        image.save(output_path, format="WEBP")
    elif target_format_norm == "PNG":
        image.save(output_path, format="PNG")
    else:
        image.save(output_path, format=target_format_norm)

    return output_path


class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Konverter Gambar")
        self.root.geometry("640x740")
        self.root.minsize(600, 680)

        apply_ocean_theme(root)
        apply_icon(root)

        self.files = []  # list of file paths
        self.output_dir = tk.StringVar(value=os.path.join(os.getcwd(), "hasil_konversi"))
        self.target_format = tk.StringVar(value="PNG")

        self._build_ui()

    # ---------- UI ----------
    def _build_ui(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        title = ttk.Label(main, text="🌊 Konverter Gambar", style="Title.TLabel")
        title.pack(anchor="w")

        subtitle_text = "Seret & lepas gambar di kotak bawah, atau klik untuk memilih file."
        if not DND_AVAILABLE:
            subtitle_text += "\n(Drag & drop nonaktif, install 'tkinterdnd2' untuk mengaktifkan)"
        subtitle = ttk.Label(main, text=subtitle_text, style="Subtitle.TLabel")
        subtitle.pack(anchor="w", pady=(4, 10))

        # --- Drop zone (A) ---
        drop_border = tk.Frame(main, bg=COLORS["primary"], padx=2, pady=2)
        drop_border.pack(fill="x", pady=(0, 10))
        self.drop_zone = tk.Label(
            drop_border,
            text="🖼  Tarik & lepas file gambar di sini\n(JPEG, JPG, PNG, WEBP, SVG)\natau klik untuk memilih file",
            bg=COLORS["seafoam"],
            fg=COLORS["primary_dark"],
            font=("Segoe UI", 11),
            height=6,
            justify="center",
            cursor="hand2",
        )
        self.drop_zone.pack(fill="both", expand=True)
        self.drop_zone.bind("<Button-1>", lambda e: self.browse_files())
        self.drop_zone.bind("<Enter>", lambda e: self.drop_zone.configure(bg=COLORS["seafoam_dark"]))
        self.drop_zone.bind("<Leave>", lambda e: self.drop_zone.configure(bg=COLORS["seafoam"]))

        if DND_AVAILABLE:
            self.drop_zone.drop_target_register(DND_FILES)
            self.drop_zone.dnd_bind("<<Drop>>", self.on_drop)

        # --- File list ---
        list_frame = ttk.Frame(main)
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

        list_buttons = ttk.Frame(main)
        list_buttons.pack(fill="x", pady=(0, 10))
        ttk.Button(list_buttons, text="Tambah File...", command=self.browse_files).pack(side="left")
        ttk.Button(list_buttons, text="Hapus Terpilih", command=self.remove_selected).pack(side="left", padx=6)
        ttk.Button(list_buttons, text="Kosongkan", command=self.clear_files).pack(side="left")

        # --- Target format (B) ---
        target_frame = ttk.LabelFrame(main, text="Tujuan Konversi", padding=10)
        target_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(target_frame, text="Format tujuan:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        format_combo = ttk.Combobox(
            target_frame,
            textvariable=self.target_format,
            values=SUPPORTED_OUTPUT_FORMATS,
            state="readonly",
            width=10,
        )
        format_combo.grid(row=0, column=1, sticky="w")

        ttk.Label(target_frame, text="Folder tujuan:").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=(8, 0))
        output_entry = ttk.Entry(target_frame, textvariable=self.output_dir)
        output_entry.grid(row=1, column=1, sticky="ew", pady=(8, 0))
        ttk.Button(target_frame, text="Pilih...", command=self.browse_output_dir).grid(
            row=1, column=2, padx=(6, 0), pady=(8, 0)
        )
        target_frame.columnconfigure(1, weight=1)

        # --- Convert button + status ---
        action_frame = ttk.Frame(main)
        action_frame.pack(fill="x")
        self.convert_btn = ttk.Button(
            action_frame, text="🖼 Konversi Sekarang", style="Convert.TButton", command=self.start_conversion
        )
        self.convert_btn.pack(side="left")

        self.progress = ttk.Progressbar(action_frame, mode="determinate")
        self.progress.pack(side="left", fill="x", expand=True, padx=(10, 0))

        self.status_var = tk.StringVar(value="Siap.")
        status_label = ttk.Label(main, textvariable=self.status_var, style="Muted.TLabel")
        status_label.pack(anchor="w", pady=(8, 0))

    # ---------- Actions ----------
    def on_drop(self, event):
        paths = self.root.tk.splitlist(event.data)
        self.add_files(paths)

    def browse_files(self):
        filetypes = [
            ("Semua Gambar", "*.jpg *.jpeg *.png *.webp *.svg"),
            ("JPEG", "*.jpg *.jpeg"),
            ("PNG", "*.png"),
            ("WEBP", "*.webp"),
            ("SVG", "*.svg"),
        ]
        paths = filedialog.askopenfilenames(title="Pilih gambar", filetypes=filetypes)
        if paths:
            self.add_files(paths)

    def add_files(self, paths):
        added = 0
        for path in paths:
            path = path.strip("{}")
            ext = os.path.splitext(path)[1].lower()
            if ext not in SUPPORTED_INPUT_EXTENSIONS:
                continue
            if path in self.files:
                continue
            self.files.append(path)
            fmt = detect_format(path)
            self.tree.insert("", "end", values=(os.path.basename(path), fmt), tags=(path,))
            added += 1
        if added:
            self.status_var.set(f"{added} file ditambahkan.")
        else:
            self.status_var.set("Tidak ada file gambar yang valid ditambahkan.")

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
            messagebox.showwarning("Tidak ada file", "Tambahkan minimal satu file gambar terlebih dahulu.")
            return

        target_format = self.target_format.get()
        if target_format == "SVG" and not any(
            os.path.splitext(f)[1].lower() != ".svg" for f in self.files
        ):
            pass  # ok, SVG -> SVG just copies

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
                convert_image(path, output_dir, target_format)
                success += 1
            except Exception as exc:  # noqa: BLE001 - tampilkan error apapun ke user
                failed.append(f"{os.path.basename(path)}: {exc}")
            self.root.after(0, self._update_progress, i)

        self.root.after(0, self._conversion_done, success, failed, output_dir)

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


def main():
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    app = ImageConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
