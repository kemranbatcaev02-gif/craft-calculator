"""Рендер дерева крафта с возможностью сворачивать ветки."""
import customtkinter as ctk
from .theme import fonts


class TreeNodeRow(ctk.CTkFrame):
    def __init__(self, master, palette, accent, node, depth=0):
        super().__init__(master, fg_color="transparent")
        self.palette = palette
        self.accent = accent
        self.node = node
        self.depth = depth
        self.expanded = depth < 2  # первые уровни раскрыты сразу
        f = fonts()

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=(depth * 26, 0), pady=1)

        has_children = bool(node.children)
        if has_children:
            self.toggle_btn = ctk.CTkButton(
                row, text="▾" if self.expanded else "▸", width=22, height=22,
                fg_color="transparent", hover_color=palette["card_2"],
                text_color=palette["text_dim"], font=f["small"],
                command=self._toggle,
            )
            self.toggle_btn.pack(side="left")
        else:
            ctk.CTkLabel(row, text="", width=22).pack(side="left")

        ctk.CTkLabel(row, text=node.icon, font=f["icon"], width=28).pack(side="left")
        ctk.CTkLabel(row, text=node.name, font=f["h3"] if depth == 0 else f["body"],
                     text_color=palette["text"]).pack(side="left", padx=(2, 8))

        if node.is_raw:
            tag = f"нужно: {node.needed}"
            color = accent["main"]
        else:
            tag = f"нужно: {node.needed} · крафтов: {node.craft_count} → получится {node.produced}"
            color = palette["text_dim"]
        ctk.CTkLabel(row, text=tag, font=f["small"], text_color=color).pack(side="left")

        self.children_holder = ctk.CTkFrame(self, fg_color="transparent")
        if has_children and self.expanded:
            self._render_children()
        if has_children:
            self.children_holder.pack(fill="x")

    def _render_children(self):
        for w in self.children_holder.winfo_children():
            w.destroy()
        for child in self.node.children:
            TreeNodeRow(self.children_holder, self.palette, self.accent,
                        child, self.depth + 1).pack(fill="x")

    def _toggle(self):
        self.expanded = not self.expanded
        self.toggle_btn.configure(text="▾" if self.expanded else "▸")
        if self.expanded:
            self._render_children()
            self.children_holder.pack(fill="x")
        else:
            self.children_holder.pack_forget()


def render_tree(master, palette, accent, root_node):
    return TreeNodeRow(master, palette, accent, root_node, depth=0)
