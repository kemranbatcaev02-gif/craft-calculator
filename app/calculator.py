"""Рекурсивный расчёт ресурсов для крафта."""
import json
import math
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_json(name):
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


class CraftNode:
    """Узел дерева крафта."""
    def __init__(self, item_id, name, icon, needed, is_raw):
        self.item_id = item_id
        self.name = name
        self.icon = icon
        self.needed = needed        # сколько штук нужно этого предмета
        self.is_raw = is_raw        # True = сырьё, добывается, не крафтится
        self.craft_count = 0        # сколько раз нужно скрафтить (для крафтовых)
        self.produced = 0           # сколько получится с учётом округления вверх
        self.children = []          # дочерние CraftNode


class Calculator:
    def __init__(self):
        self.items = load_json("items.json")
        self.recipes = load_json("recipes.json")

    def is_raw(self, item_id: str) -> bool:
        return item_id not in self.recipes

    def item_meta(self, item_id: str):
        return self.items.get(item_id, {"name": item_id, "category": "?", "icon": "❓"})

    def build_tree(self, item_id: str, quantity: int, raw_totals: dict = None) -> CraftNode:
        """Строит дерево крафта и параллельно копит raw_totals (сырьё -> суммарное кол-во)."""
        if raw_totals is None:
            raw_totals = {}
        meta = self.item_meta(item_id)
        node = CraftNode(item_id, meta["name"], meta["icon"], quantity, self.is_raw(item_id))

        if node.is_raw:
            raw_totals[item_id] = raw_totals.get(item_id, 0) + quantity
            node.produced = quantity
            return node

        recipe = self.recipes[item_id]
        yield_ = recipe["yield"]
        craft_count = math.ceil(quantity / yield_)
        node.craft_count = craft_count
        node.produced = craft_count * yield_

        for ing_id, ing_qty in recipe["ingredients"].items():
            child = self.build_tree(ing_id, ing_qty * craft_count, raw_totals)
            node.children.append(child)

        return node

    def calculate(self, item_id: str, quantity: int):
        """Возвращает (дерево, сырьё-словарь, список_шагов_крафта)."""
        raw_totals = {}
        tree = self.build_tree(item_id, quantity, raw_totals)
        steps = self._flatten_craft_steps(tree, {})
        return tree, raw_totals, steps

    def _flatten_craft_steps(self, node: CraftNode, acc: dict):
        """Сколько раз нужно скрафтить каждый промежуточный предмет (для итогового списка действий)."""
        if not node.is_raw and node.craft_count > 0:
            entry = acc.setdefault(node.item_id, {
                "name": node.name, "icon": node.icon, "craft_count": 0, "produced": 0,
            })
            entry["craft_count"] += node.craft_count
            entry["produced"] += node.produced
        for c in node.children:
            self._flatten_craft_steps(c, acc)
        return acc

    def search(self, query: str):
        query = query.strip().lower()
        if not query:
            return []
        return [
            (iid, meta) for iid, meta in self.items.items()
            if query in meta["name"].lower()
        ]

    def by_category(self):
        cats: dict = {}
        for iid, meta in self.items.items():
            cats.setdefault(meta["category"], []).append((iid, meta))
        order = ["Сырьё", "Материалы", "Инструменты", "Оружие", "Броня",
                 "Еда", "Мебель и декор", "Механизмы", "Транспорт"]
        return {k: sorted(cats[k], key=lambda t: t[1]["name"]) for k in order if k in cats}
