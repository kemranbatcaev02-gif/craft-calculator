"""Избранное и история последних расчётов."""
import customtkinter as ctk
from .theme import fonts
from .widgets import Card, page_title


class FavoritesFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, app):
        p = app.palette
        super().__init__(master, fg_color=p["bg"])
        self.app = app
        self.p = p
        self.f = fonts()
        self.a = app.config.accent

        page_title(self, p, "★ Избранное и история")

        # Избранное
        ctk.CTkLabel(self, text="Избранное", font=self.f["h2"],
                     text_color=p["text"]).pack(anchor="w", padx=28, pady=(20, 8))
        favs = app.config.favorites
        if not favs:
            self._empty("Пока пусто — добавляй звёздочкой на странице калькулятора")
        else:
            grid = ctk.CTkFrame(self, fg_color="transparent")
            grid.pack(fill="x", padx=24)
            for i in range(4):
                grid.grid_columnconfigure(i, weight=1)
            for i, iid in enumerate(favs):
                meta = app.calc.item_meta(iid)
                btn = ctk.CTkButton(
                    grid, text=f'{meta["icon"]}  {meta["name"]}', anchor="w",
                    height=42, font=self.f["body"], fg_color=p["card"],
                    hover_color=self.a["soft"], text_color=p["text"], corner_radius=10,
                    command=lambda x=iid: app.open_calculator(x),
                )
                btn.grid(row=i // 4, column=i % 4, padx=4, pady=4, sticky="ew")

        # История
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=28, pady=(24, 8))
        ctk.CTkLabel(top, text="История расчётов", font=self.f["h2"],
                     text_color=p["text"]).pack(side="left")
        if app.config.history:
            ctk.CTkButton(top, text="Очистить", width=100, height=28, font=self.f["small"],
                         fg_color="transparent", border_width=1, border_color=p["danger"],
                         text_color=p["danger"], hover_color=p["danger"],
                         command=self._clear_history).pack(side="right")

        if not app.config.history:
            self._empty("Здесь появятся твои последние расчёты")
        else:
            for h in app.config.history:
                card = Card(self, p)
                card.pack(fill="x", padx=24, pady=3)
                row = ctk.CTkFrame(card, fg_color="transparent")
                row.pack(fill="x", padx=16, pady=10)
                ctk.CTkLabel(row, text=f'{h["icon"]} {h["name"]} × {h["quantity"]}',
                             font=self.f["body"], text_color=p["text"]).pack(side="left")
                ctk.CTkButton(row, text="Открыть", width=90, height=28, font=self.f["small"],
                             fg_color=self.a["main"], hover_color=self.a["hover"],
                             command=lambda x=h["item_id"]: app.open_calculator(x)
                             ).pack(side="right")

    def _empty(self, text):
        card = Card(self, self.p)
        card.pack(fill="x", padx=24)
        ctk.CTkLabel(card, text=text, font=self.f["body"],
                     text_color=self.p["text_dim"]).pack(padx=20, pady=20)

    def _clear_history(self):
        self.app.config.clear_history()
        self.app.rebuild(show="favorites")
