"""Переиспользуемые виджеты."""
import customtkinter as ctk
from .theme import fonts


class Card(ctk.CTkFrame):
    def __init__(self, master, palette, **kwargs):
        kwargs.setdefault("fg_color", palette["card"])
        kwargs.setdefault("corner_radius", 14)
        super().__init__(master, **kwargs)


def page_title(master, palette, text, subtitle=None):
    f = fonts()
    ctk.CTkLabel(master, text=text, font=f["h1"],
                 text_color=palette["text"]).pack(anchor="w", padx=28, pady=(24, 0))
    if subtitle:
        ctk.CTkLabel(master, text=subtitle, font=f["body"],
                     text_color=palette["text_dim"]).pack(anchor="w", padx=28, pady=(2, 0))
