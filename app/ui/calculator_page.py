"""Калькулятор: выбор предмета, количество, разбор на сырьё и дерево крафта."""
import customtkinter as ctk
from .theme import fonts
from .widgets import Card, page_title
from .tree_view import render_tree


class CalculatorFrame(ctk.CTkFrame):
    def __init__(self, master, app, preset_item=None):
        p = app.palette
        super().__init__(master, fg_color=p["bg"])
        self.app = app
        self.p = p
        self.f = fonts()
        self.a = app.config.accent
        self.calc = app.calc
        self.selected_item = preset_item

        page_title(self, p, "🧮 Калькулятор крафта",
                   "Впиши предмет и сколько штук нужно — покажу, сколько сырья собирать")

        # ---------- Поиск ----------
        search_card = Card(self, p)
        search_card.pack(fill="x", padx=24, pady=(18, 10))
        row = ctk.CTkFrame(search_card, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=16)

        self.search_entry = ctk.CTkEntry(row, placeholder_text="Например: алмазная кирка",
                                         height=42, font=self.f["body"], fg_color=p["card_2"])
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.search_entry.bind("<KeyRelease>", self._on_search)
        if preset_item:
            self.search_entry.insert(0, self.calc.item_meta(preset_item)["name"])

        self.qty_entry = ctk.CTkEntry(row, width=90, height=42, font=self.f["body"],
                                      fg_color=p["card_2"])
        self.qty_entry.insert(0, "1")
        self.qty_entry.pack(side="left", padx=(0, 8))

        self.calc_btn = ctk.CTkButton(row, text="Рассчитать", height=42, width=130,
                                      font=self.f["h3"], fg_color=self.a["main"],
                                      hover_color=self.a["hover"], command=self._calculate)
        self.calc_btn.pack(side="left")

        self.suggestions_holder = ctk.CTkFrame(search_card, fg_color="transparent")
        self.suggestions_holder.pack(fill="x", padx=18, pady=(0, 12))

        self.error_lbl = ctk.CTkLabel(self, text="", font=self.f["body"],
                                      text_color=p["danger"])
        self.error_lbl.pack(anchor="w", padx=28)

        self.result_area = ctk.CTkScrollableFrame(self, fg_color=p["bg"])
        self.result_area.pack(fill="both", expand=True, padx=16, pady=(4, 16))

        if preset_item:
            self._calculate()

    def _on_search(self, event=None):
        for w in self.suggestions_holder.winfo_children():
            w.destroy()
        query = self.search_entry.get()
        if len(query) < 2:
            return
        results = self.calc.search(query)[:6]
        if not results:
            return
        box = ctk.CTkFrame(self.suggestions_holder, fg_color=self.p["card_2"], corner_radius=8)
        box.pack(fill="x")
        for iid, meta in results:
            btn = ctk.CTkButton(
                box, text=f'{meta["icon"]}  {meta["name"]}', anchor="w", height=32,
                fg_color="transparent", hover_color=self.p["card"],
                text_color=self.p["text"], font=self.f["body"],
                command=lambda i=iid, n=meta["name"]: self._pick(i, n),
            )
            btn.pack(fill="x", padx=4, pady=1)

    def _pick(self, item_id, name):
        self.selected_item = item_id
        self.search_entry.delete(0, "end")
        self.search_entry.insert(0, name)
        for w in self.suggestions_holder.winfo_children():
            w.destroy()
        self._calculate()

    def _resolve_item(self):
        if self.selected_item:
            return self.selected_item
        query = self.search_entry.get().strip()
        matches = self.calc.search(query)
        if len(matches) == 1:
            return matches[0][0]
        exact = [iid for iid, meta in matches if meta["name"].lower() == query.lower()]
        return exact[0] if exact else None

    def _calculate(self):
        item_id = self._resolve_item()
        if not item_id:
            self.error_lbl.configure(text="Не нашла такой предмет — выбери из подсказок")
            return
        try:
            qty = int(self.qty_entry.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            self.error_lbl.configure(text="Количество — целое число больше нуля")
            return

        self.error_lbl.configure(text="")
        self.selected_item = item_id
        tree, raw_totals, steps = self.calc.calculate(item_id, qty)
        meta = self.calc.item_meta(item_id)
        self.app.config.add_history(item_id, meta["name"], meta["icon"], qty)
        self._render_result(tree, raw_totals, steps, meta, qty)

    def _render_result(self, tree, raw_totals, steps, meta, qty):
        for w in self.result_area.winfo_children():
            w.destroy()
        p, f, a = self.p, self.f, self.a

        # Заголовок результата + избранное
        header = ctk.CTkFrame(self.result_area, fg_color="transparent")
        header.pack(fill="x", padx=8, pady=(4, 10))
        ctk.CTkLabel(header, text=f'{meta["icon"]} {meta["name"]} × {qty}',
                     font=f["h2"], text_color=p["text"]).pack(side="left")
        is_fav = self.app.config.is_favorite(self.selected_item)
        ctk.CTkButton(
            header, text="★ В избранном" if is_fav else "☆ В избранное",
            width=160, height=32, font=f["small"],
            fg_color=a["main"] if is_fav else "transparent",
            border_width=1, border_color=a["main"],
            text_color=p["text"] if is_fav else a["main"],
            hover_color=a["hover"],
            command=self._toggle_fav,
        ).pack(side="right")

        # Сырьё
        ctk.CTkLabel(self.result_area, text="🪨 Нужно добыть / собрать", font=f["h3"],
                     text_color=p["text"]).pack(anchor="w", padx=8, pady=(6, 6))
        raw_card = Card(self.result_area, p)
        raw_card.pack(fill="x", padx=4, pady=(0, 14))
        grid = ctk.CTkFrame(raw_card, fg_color="transparent")
        grid.pack(fill="x", padx=16, pady=14)
        for i, (iid, amount) in enumerate(sorted(raw_totals.items(), key=lambda t: -t[1])):
            im = self.calc.item_meta(iid)
            cell = ctk.CTkFrame(grid, fg_color=p["card_2"], corner_radius=10)
            cell.grid(row=i // 3, column=i % 3, padx=5, pady=5, sticky="ew")
            grid.grid_columnconfigure(i % 3, weight=1)
            inner = ctk.CTkFrame(cell, fg_color="transparent")
            inner.pack(padx=12, pady=10)
            ctk.CTkLabel(inner, text=f'{im["icon"]} {im["name"]}', font=f["body"],
                         text_color=p["text"]).pack(anchor="w")
            ctk.CTkLabel(inner, text=str(amount), font=(f["h1"][0], 20, "bold"),
                         text_color=a["main"]).pack(anchor="w")

        # Шаги крафта
        if steps:
            ctk.CTkLabel(self.result_area, text="🔨 Шаги крафта", font=f["h3"],
                         text_color=p["text"]).pack(anchor="w", padx=8, pady=(4, 6))
            steps_card = Card(self.result_area, p)
            steps_card.pack(fill="x", padx=4, pady=(0, 14))
            inner = ctk.CTkFrame(steps_card, fg_color="transparent")
            inner.pack(fill="x", padx=16, pady=12)
            ordered = sorted(steps.items(), key=lambda kv: kv[1]["craft_count"])
            for iid, s in ordered:
                row = ctk.CTkFrame(inner, fg_color="transparent")
                row.pack(fill="x", pady=3)
                ctk.CTkLabel(row, text=f'{s["icon"]} {s["name"]}', font=f["body"],
                             text_color=p["text"]).pack(side="left")
                ctk.CTkLabel(row, text=f'скрафтить {s["craft_count"]}× → получишь {s["produced"]}',
                             font=f["small"], text_color=a["main"]).pack(side="right")

        # Дерево
        ctk.CTkLabel(self.result_area, text="🌳 Полное дерево крафта", font=f["h3"],
                     text_color=p["text"]).pack(anchor="w", padx=8, pady=(4, 6))
        tree_card = Card(self.result_area, p)
        tree_card.pack(fill="x", padx=4, pady=(0, 10))
        tree_inner = ctk.CTkFrame(tree_card, fg_color="transparent")
        tree_inner.pack(fill="x", padx=14, pady=14)
        render_tree(tree_inner, p, a, tree).pack(fill="x")

    def _toggle_fav(self):
        self.app.config.toggle_favorite(self.selected_item)
        item_id = self.selected_item
        qty = int(self.qty_entry.get())
        tree, raw_totals, steps = self.calc.calculate(item_id, qty)
        meta = self.calc.item_meta(item_id)
        self._render_result(tree, raw_totals, steps, meta, qty)
