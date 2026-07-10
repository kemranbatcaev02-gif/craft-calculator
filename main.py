"""
Minecraft Craft Calculator — калькулятор ресурсов для крафта.
Python 3.10+ · CustomTkinter
Запуск: python main.py
"""
import customtkinter as ctk
from app.config import Config
from app.calculator import Calculator
from app.ui.theme import PALETTES, fonts
from app.ui.calculator_page import CalculatorFrame
from app.ui.browser_page import BrowserFrame
from app.ui.favorites_page import FavoritesFrame
from app.ui.settings_page import SettingsFrame

PAGES = {
    "calculator": ("🧮  Калькулятор", CalculatorFrame),
    "browser":    ("📖  Каталог", BrowserFrame),
    "favorites":  ("★  Избранное", FavoritesFrame),
    "settings":   ("⚙️  Настройки", SettingsFrame),
}


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.config_ = Config()
        self.calc = Calculator()

        self.title("Minecraft Craft Calculator")
        self.geometry("1080x720")
        self.minsize(900, 600)

        self._current_page = "calculator"
        self._pending_item = None
        self.rebuild()

    @property
    def config(self):  # noqa: A003
        return self.config_

    @property
    def palette(self):
        return PALETTES[self.config_.settings["theme"]]

    def rebuild(self, show=None):
        ctk.set_appearance_mode(self.config_.settings["theme"])
        for w in self.winfo_children():
            w.destroy()

        p = self.palette
        self.configure(fg_color=p["bg"])
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self.content = ctk.CTkFrame(self, fg_color=p["bg"], corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.show_page(show or self._current_page)

    def _build_sidebar(self):
        p = self.palette
        a = self.config_.accent
        f = fonts()

        sidebar = ctk.CTkFrame(self, fg_color=p["sidebar"], corner_radius=0, width=220)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text="⛏️ CraftCalc", font=(f["h1"][0], 22, "bold"),
                     text_color=a["main"]).pack(padx=22, pady=(28, 4), anchor="w")
        ctk.CTkLabel(sidebar, text="Калькулятор ресурсов", font=f["small"],
                     text_color=p["text_dim"]).pack(padx=24, anchor="w", pady=(0, 18))

        self._nav_buttons = {}
        for key, (label, _) in PAGES.items():
            active = key == self._current_page
            btn = ctk.CTkButton(
                sidebar, text=label, anchor="w", height=44, corner_radius=10,
                font=f["body"],
                fg_color=a["soft"] if active else "transparent",
                text_color=p["text"] if active else p["text_dim"],
                hover_color=p["card"],
                command=lambda k=key: self.show_page(k),
            )
            btn.pack(fill="x", padx=14, pady=2)
            self._nav_buttons[key] = btn

        ctk.CTkLabel(sidebar, text="v1.0 · made with 🐍", font=f["small"],
                     text_color=p["text_dim"]).pack(side="bottom", pady=16)

    def show_page(self, key):
        self._current_page = key
        p = self.palette
        a = self.config_.accent
        for k, btn in self._nav_buttons.items():
            btn.configure(
                fg_color=a["soft"] if k == key else "transparent",
                text_color=p["text"] if k == key else p["text_dim"],
            )
        for w in self.content.winfo_children():
            w.destroy()

        if key == "calculator":
            CalculatorFrame(self.content, self, preset_item=self._pending_item).pack(
                fill="both", expand=True)
            self._pending_item = None
        else:
            PAGES[key][1](self.content, self).pack(fill="both", expand=True)

    def open_calculator(self, item_id):
        """Открыть калькулятор сразу с выбранным предметом (из каталога/избранного/истории)."""
        self._pending_item = item_id
        self.show_page("calculator")


if __name__ == "__main__":
    App().mainloop()
