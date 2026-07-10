"""Каталог: все предметы по категориям, клик -> открыть в калькуляторе."""
import customtkinter as ctk
from .theme import fonts
from .widgets import Card, page_title


class BrowserFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, app):
        p = app.palette
        super().__init__(master, fg_color=p["bg"])
        self.app = app
        f = fonts()
        a = app.config.accent

        page_title(self, p, "📖 Каталог предметов", "Жми на предмет — откроется расчёт")

        cats = app.calc.by_category()
        for cat_name, entries in cats.items():
            ctk.CTkLabel(self, text=cat_name, font=f["h2"],
                         text_color=p["text"]).pack(anchor="w", padx=28, pady=(20, 8))
            grid = ctk.CTkFrame(self, fg_color="transparent")
            grid.pack(fill="x", padx=24)
            for i in range(4):
                grid.grid_columnconfigure(i, weight=1)
            for i, (iid, meta) in enumerate(entries):
                btn = ctk.CTkButton(
                    grid, text=f'{meta["icon"]}  {meta["name"]}', anchor="w",
                    height=42, font=f["body"], fg_color=p["card"],
                    hover_color=a["soft"], text_color=p["text"], corner_radius=10,
                    command=lambda x=iid: app.open_calculator(x),
                )
                btn.grid(row=i // 4, column=i % 4, padx=4, pady=4, sticky="ew")
