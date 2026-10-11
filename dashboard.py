import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_db
from style import *

class DashboardPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        tk.Label(self, text="Dashboard", font=FONT_TITLE, bg=BG, fg=TEXT).pack(
            anchor="w", pady=(0, 18))
        self.cards = tk.Frame(self, bg=BG)
        self.cards.pack(fill="x")
        self.values = {}
        for title, key in [
            ("PRODUCT TYPES", "products"), ("UNITS IN STOCK", "units"),
            ("STOCK VALUE", "value"), ("TOTAL SALES", "sales")
        ]:
            card = tk.Frame(self.cards, bg=WHITE, padx=18, pady=16,
                            highlightbackground=BORDER, highlightthickness=1)
            card.pack(side="left", fill="both", expand=True, padx=(0, 12))
            tk.Label(card, text=title, bg=WHITE, fg=MUTED,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w")
            self.values[key] = tk.Label(card, text="—", bg=WHITE, fg=TEXT,
                                        font=("Segoe UI", 20, "bold"))
            self.values[key].pack(anchor="w", pady=(8, 0))

        tk.Label(self, text="Low-stock products", font=("Segoe UI", 14, "bold"),
                 bg=BG, fg=TEXT).pack(anchor="w", pady=(26, 10))
        columns = ("id", "name", "quantity", "threshold")
        self.table = ttk.Treeview(self, columns=columns, show="headings", height=9)
        for col, title, width in [
            ("id", "ID", 60), ("name", "Product", 280),
            ("quantity", "Quantity", 120), ("threshold", "Low-stock level", 150)
        ]:
            self.table.heading(col, text=title)
            self.table.column(col, width=width, anchor="w")
        self.table.pack(fill="both", expand=True)
        self.refresh()

    def refresh(self):
        try:
            con = connect_db()
            cur = con.cursor()
            cur.execute("SELECT COUNT(*), COALESCE(SUM(quantity),0), "
                        "COALESCE(SUM(quantity*purchase_price),0) FROM products")
            products, units, value = cur.fetchone()
            cur.execute("SELECT COALESCE(SUM(total_amount),0) FROM sales")
            sales = cur.fetchone()[0]
            self.values["products"].config(text=str(products))
            self.values["units"].config(text=str(units))
            self.values["value"].config(text=f"₹{float(value):,.2f}")
            self.values["sales"].config(text=f"₹{float(sales):,.2f}")
            cur.execute("""SELECT product_id, product_name, quantity, low_stock_level
                           FROM products WHERE quantity <= low_stock_level
                           ORDER BY quantity ASC""")
            rows = cur.fetchall()
            self.table.delete(*self.table.get_children())
            for row in rows:
                self.table.insert("", "end", values=row)
            cur.close()
            con.close()
        except Exception as exc:
            messagebox.showerror("Dashboard error", str(exc))
