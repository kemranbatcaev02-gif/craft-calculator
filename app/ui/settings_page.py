"""Настройки: тема и акцентный цвет."""
import customtkinter as ctk
from ..config import ACCENTS
from .theme import fonts
from .widgets import Card, page_title


class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        p = app.palette
        super().__init__(master, fg_color=p["bg"])
        self.app = app
        f = fonts()
        a = app.config.accent

        page_title(self, p, "⚙️ Настройки")

        card = Card(self, p)
        card.pack(fill="x", padx=24, pady=20)

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=10)
        ctk.CTkLabel(row, text="Тема", font=f["body"],
                     text_color=p["text"]).pack(side="left")
        seg = ctk.CTkSegmentedButton(row, values=["Тёмная", "Светлая"], height=34,
                                     selected_color=a["main"], selected_hover_color=a["hover"],
                                     command=self._set_theme)
        seg.set("Тёмная" if app.config.settings["theme"] == "dark" else "Светлая")
        seg.pack(side="right")

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=10)
        ctk.CTkLabel(row, text="Акцентный цвет", font=f["body"],
                     text_color=p["text"]).pack(side="left")
        colors = ctk.CTkFrame(row, fg_color="transparent")
        colors.pack(side="right")
        for name, col in ACCENTS.items():
            border = 2 if name == app.config.settings["accent"] else 0
            ctk.CTkButton(colors, text="", width=30, height=30, corner_radius=15,
                          fg_color=col["main"], hover_color=col["hover"],
                          border_width=border, border_color=p["text"],
                          command=lambda n=name: self._set_accent(n)).pack(side="left", padx=4)

    def _set_theme(self, value):
        self.app.config.settings["theme"] = "dark" if value == "Тёмная" else "light"
        self.app.config.save_settings()
        self.app.rebuild(show="settings")

    def _set_accent(self, name):
        self.app.config.settings["accent"] = name
        self.app.config.save_settings()
        self.app.rebuild(show="settings")
