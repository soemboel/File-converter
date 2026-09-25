"""Tema oseanik (warna laut) yang dipakai bersama oleh semua jendela aplikasi ini."""

import os
from tkinter import ttk

from common import resource_path

COLORS = {
    "bg": "#eaf6fb",
    "surface": "#ffffff",
    "deep": "#023047",
    "primary": "#0077b6",
    "primary_dark": "#023e73",
    "accent": "#00b4d8",
    "seafoam": "#caf0f8",
    "seafoam_dark": "#90e0ef",
    "success": "#06d6a0",
    "success_dark": "#04b489",
    "muted": "#4a6572",
    "border": "#90e0ef",
}

ICON_PATH = resource_path("favicon", "favicon.ico")


def apply_icon(root):
    """Pasang favicon/ikon jendela kalau filenya ada."""
    try:
        if os.path.exists(ICON_PATH):
            root.iconbitmap(ICON_PATH)
    except Exception:
        pass


def apply_ocean_theme(root):
    """Terapkan palet warna laut ke seluruh widget ttk di jendela ini."""
    root.configure(bg=COLORS["bg"])

    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TFrame", background=COLORS["bg"])
    style.configure("Surface.TFrame", background=COLORS["surface"])

    style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["deep"], font=("Segoe UI", 10))
    style.configure("Title.TLabel", background=COLORS["bg"], foreground=COLORS["deep"], font=("Segoe UI", 20, "bold"))
    style.configure("Subtitle.TLabel", background=COLORS["bg"], foreground=COLORS["muted"], font=("Segoe UI", 10))
    style.configure("Muted.TLabel", background=COLORS["bg"], foreground=COLORS["muted"], font=("Segoe UI", 9))

    style.configure("TLabelframe", background=COLORS["bg"], bordercolor=COLORS["border"], relief="solid")
    style.configure(
        "TLabelframe.Label", background=COLORS["bg"], foreground=COLORS["primary_dark"], font=("Segoe UI", 10, "bold")
    )

    style.configure("TNotebook", background=COLORS["bg"], borderwidth=0)
    style.configure(
        "TNotebook.Tab",
        background=COLORS["seafoam_dark"],
        foreground=COLORS["deep"],
        padding=(18, 10),
        font=("Segoe UI", 10, "bold"),
        borderwidth=0,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", COLORS["primary"])],
        foreground=[("selected", "#ffffff")],
    )

    style.configure(
        "Treeview",
        background=COLORS["surface"],
        fieldbackground=COLORS["surface"],
        foreground=COLORS["deep"],
        rowheight=27,
        font=("Segoe UI", 9),
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=COLORS["primary"],
        foreground="#ffffff",
        font=("Segoe UI", 9, "bold"),
        relief="flat",
    )
    style.map("Treeview", background=[("selected", COLORS["accent"])], foreground=[("selected", "#ffffff")])
    style.map("Treeview.Heading", background=[("active", COLORS["primary_dark"])])

    style.configure(
        "TButton",
        background=COLORS["primary"],
        foreground="#ffffff",
        font=("Segoe UI", 10),
        padding=(10, 6),
        borderwidth=0,
        focuscolor=COLORS["primary"],
    )
    style.map("TButton", background=[("active", COLORS["primary_dark"]), ("disabled", "#a9c6d6")])

    style.configure(
        "Convert.TButton",
        background=COLORS["success"],
        foreground="#ffffff",
        font=("Segoe UI", 11, "bold"),
        padding=(16, 10),
        borderwidth=0,
    )
    style.map("Convert.TButton", background=[("active", COLORS["success_dark"]), ("disabled", "#a6e4cf")])

    style.configure("TEntry", fieldbackground="#ffffff", foreground=COLORS["deep"], bordercolor=COLORS["border"], padding=6)
    style.configure("TCombobox", fieldbackground="#ffffff", foreground=COLORS["deep"], padding=6)
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", "#ffffff")],
        foreground=[("readonly", COLORS["deep"])],
    )

    style.configure(
        "Horizontal.TProgressbar",
        background=COLORS["accent"],
        troughcolor=COLORS["seafoam"],
        bordercolor=COLORS["bg"],
        lightcolor=COLORS["accent"],
        darkcolor=COLORS["accent"],
        thickness=14,
    )

    style.configure(
        "Vertical.TScrollbar",
        background=COLORS["seafoam_dark"],
        troughcolor=COLORS["bg"],
        bordercolor=COLORS["bg"],
        arrowcolor=COLORS["primary_dark"],
    )

    return style
