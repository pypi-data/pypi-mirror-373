from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Theme:
    name: str
    font: str
    node_fill: str
    node_border: str
    node_font: str
    edge_color: str
    background: str | None = None
    node_fill2: str | None = None  # optional gradient second color
    gradientangle: int | None = None


THEMES: dict[str, Theme] = {
    "light": Theme(
        name="light",
        font="Segoe UI, Meiryo, Arial",
        node_fill="#E9F0FB",
        node_border="#4C78A8",
        node_font="#1f2937",
        edge_color="#9AA6B2",
        background="#FFFFFF",
    ),
    "pastel": Theme(
        name="pastel",
        font="Inter, Segoe UI, Meiryo, Arial",
        node_fill="#FCE7F3",
        node_border="#F472B6",
        node_font="#1F2937",
        edge_color="#F9A8D4",
        background="#FFFFFF",
        node_fill2="#E0E7FF",
        gradientangle=90,
    ),
    "dark": Theme(
        name="dark",
        font="Segoe UI, Meiryo, Arial",
        node_fill="#374151",
        node_border="#93C5FD",
        node_font="#E5E7EB",
        edge_color="#6B7280",
        background="#111827",
    ),
    # New: kawaii (cute), chic, modern, business
    "kawaii": Theme(
        name="kawaii",
        font="Poppins, Segoe UI, Meiryo, Arial",
        node_fill="#FFE4F1",
        node_border="#FF9AC1",
        node_font="#7C3A4A",
        edge_color="#FFB6D9",
        background="#FFF7FB",
        node_fill2="#E3F8FF",
        gradientangle=90,
    ),
    "chic": Theme(
        name="chic",
        font="Segoe UI, Meiryo, Arial",
        node_fill="#1F2937",
        node_border="#D1B06B",
        node_font="#F9FAFB",
        edge_color="#B08946",
        background="#0B1220",
    ),
    "modern": Theme(
        name="modern",
        font="Inter, Segoe UI, Meiryo, Arial",
        node_fill="#E0F2FE",
        node_border="#0EA5E9",
        node_font="#0F172A",
        edge_color="#38BDF8",
        background="#F8FAFC",
        node_fill2="#EEF2FF",
        gradientangle=0,
    ),
    "business": Theme(
        name="business",
        font="Segoe UI, Meiryo, Arial",
        node_fill="#EEF2F7",
        node_border="#2563EB",
        node_font="#111827",
        edge_color="#64748B",
        background="#FFFFFF",
    ),
    # Caution: yellow & red focused theme
    "caution": Theme(
        name="caution",
        font="Segoe UI, Meiryo, Arial",
        node_fill="#FFF59D",      # soft yellow
        node_border="#DC2626",    # strong red border
        node_font="#7A1E1E",      # dark red text
        edge_color="#F59E0B",     # amber edges
        background="#FFFBEB",     # warm light bg
        node_fill2="#FECACA",     # light red for gradient
        gradientangle=90,
    ),
}


def get_theme(name: str | None) -> Theme:
    if not name:
        # Make pastel the new default for a stylish out-of-the-box look
        return THEMES["pastel"]
    return THEMES.get(name.lower(), THEMES["light"])
