"""Настройки приложения, избранное и история расчётов (JSON)."""
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CONFIG_PATH = DATA_DIR / "config.json"
FAVORITES_PATH = DATA_DIR / "favorites.json"
HISTORY_PATH = DATA_DIR / "history.json"

DEFAULT_SETTINGS = {"theme": "dark", "accent": "emerald"}

ACCENTS = {
    "emerald": {"main": "#10b981", "hover": "#059669", "soft": "#064e3b"},
    "blue":    {"main": "#3b82f6", "hover": "#2563eb", "soft": "#1e3a5f"},
    "amber":   {"main": "#f59e0b", "hover": "#d97706", "soft": "#573f10"},
    "violet":  {"main": "#8b5cf6", "hover": "#7c3aed", "soft": "#3b2a63"},
    "rose":    {"main": "#f43f5e", "hover": "#e11d48", "soft": "#551a26"},
}


def _load(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return default
    return default


def _save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


class Config:
    def __init__(self):
        self.settings = {**DEFAULT_SETTINGS, **_load(CONFIG_PATH, {})}
        self.favorites: list = _load(FAVORITES_PATH, [])
        self.history: list = _load(HISTORY_PATH, [])

    @property
    def accent(self):
        return ACCENTS.get(self.settings["accent"], ACCENTS["emerald"])

    def save_settings(self):
        _save(CONFIG_PATH, self.settings)

    # ---------- Избранное ----------

    def toggle_favorite(self, item_id: str):
        if item_id in self.favorites:
            self.favorites.remove(item_id)
        else:
            self.favorites.append(item_id)
        _save(FAVORITES_PATH, self.favorites)

    def is_favorite(self, item_id: str) -> bool:
        return item_id in self.favorites

    # ---------- История ----------

    def add_history(self, item_id: str, name: str, icon: str, quantity: int):
        self.history.insert(0, {"item_id": item_id, "name": name, "icon": icon, "quantity": quantity})
        self.history = self.history[:30]
        _save(HISTORY_PATH, self.history)

    def clear_history(self):
        self.history = []
        _save(HISTORY_PATH, self.history)
