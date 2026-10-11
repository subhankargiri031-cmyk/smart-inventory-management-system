import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_db
from style import *

class SalesPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        tk.Label(self, text="Sales & Stock Control", font=FONT_TITLE, bg=BG, fg=TEXT).pack(
            anchor="w", pady=(0, 15))
        form = tk.Frame(self, bg=WHITE, padx=16, pady=16,
                        highlightbackground=BORDER, highlightthickness=1)
        form.pack(fill="x")
        tk.Label(form, text="Product", bg=WHITE, fg=TEXT, font=FONT_BOLD).grid(
            row=0, column=0, sticky="w", padx=6)
        self.product = ttk.Combobox(form, state="readonly", width=35)
        self.product.grid(row=1, column=0, padx=6, pady=8, sticky="ew")
        tk.Label(form, text="Quantity to sell", bg=WHITE, fg=TEXT, font=FONT_BOLD).grid(
            row=0, column=1, sticky="w", padx=6)
        self.quantity = tk.Entry(form, font=FONT, width=18)
        self.quantity.grid(row=1, column=1, padx=6, pady=8, ipady=4)
        tk.Button(form, text="Record sale", command=self.record_sale, bg=PRIMARY,
                  fg=WHITE, relief="flat", font=FONT_BOLD, padx=18, pady=8).grid(
                      row=1, column=2, padx=10)
        self.load_products()
        tk.Label(self, text="Recent sales", font=("Segoe UI", 14, "bold"),
                 bg=BG, fg=TEXT).pack(anchor="w", pady=(24, 10))
        cols = ("sale", "product", "quantity", "price", "total", "date")
        self.table = ttk.Treeview(self, columns=cols, show="headings")
        for col, label, width in [
            ("sale","Sale ID",70),("product","Product",230),("quantity","Qty",70),
            ("price","Unit price",110),("total","Total",110),("date","Date",180)
        ]:
            self.table.heading(col, text=label); self.table.column(col, width=width, anchor="w")
        self.table.pack(fill="both", expand=True)
        self.refresh()

    def load_products(self):
        con = connect_db(); cur = con.cursor()
        cur.execute("SELECT product_id, product_name, quantity, selling_price FROM products ORDER BY product_name")
        self.products = cur.fetchall()
        self.product["values"] = [
            f"{p[0]} - {p[1]} (stock: {p[2]}, ₹{float(p[3]):.2f})" for p in self.products
        ]
        cur.close(); con.close()

    def record_sale(self):
        selected = self.product.current()
        if selected < 0:
            messagebox.showwarning("Select product", "Choose a product.")
            return
        try:
            qty = int(self.quantity.get())
            if qty <= 0: raise ValueError("Quantity must be greater than zero.")
            product_id, name, stock, price = self.products[selected]
            if qty > stock:
                raise ValueError(f"Not enough stock. Available quantity: {stock}")
            total = float(price) * qty
            con = connect_db(); cur = con.cursor()
            cur.execute("UPDATE products SET quantity=quantity-%s WHERE product_id=%s AND quantity >= %s",
                        (qty, product_id, qty))
            if cur.rowcount != 1:
                con.rollback()
                raise ValueError("Stock changed. Refresh and try again.")
            cur.execute("INSERT INTO sales (product_id, quantity, unit_price, total_amount) VALUES (%s,%s,%s,%s)",
                        (product_id, qty, price, total))
            con.commit(); cur.close(); con.close()
            messagebox.showinfo("Sale recorded", f"Sale saved.\nProduct: {name}\nTotal: ₹{total:.2f}")
            self.quantity.delete(0, "end")
            self.load_products(); self.refresh()
        except ValueError as exc:
            messagebox.showwarning("Invalid sale", str(exc))
        except Exception as exc:
            messagebox.showerror("Sales error", str(exc))

    def refresh(self):
        try:
            con = connect_db(); cur = con.cursor()
            cur.execute("""SELECT s.sale_id, p.product_name, s.quantity, s.unit_price,
                s.total_amount, DATE_FORMAT(s.sale_date,'%Y-%m-%d %H:%i')
                FROM sales s JOIN products p ON s.product_id=p.product_id
                ORDER BY s.sale_date DESC LIMIT 200""")
            rows = cur.fetchall()
            self.table.delete(*self.table.get_children())
            for row in rows: self.table.insert("", "end", values=row)
            cur.close(); con.close()
        except Exception as exc:
            messagebox.showerror("Sales history error", str(exc))
