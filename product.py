import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import connect_db
from style import *

class ProductPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.selected_id = None
        tk.Label(self, text="Product Management", font=FONT_TITLE, bg=BG, fg=TEXT).pack(
            anchor="w", pady=(0, 12))

        form = tk.Frame(self, bg=WHITE, padx=14, pady=12,
                        highlightbackground=BORDER, highlightthickness=1)
        form.pack(fill="x")
        self.entries = {}
        fields = [
            ("Product name", "name"), ("Quantity", "quantity"),
            ("Purchase price", "purchase"), ("Selling price", "selling"),
            ("Low-stock level", "low"), ("Expiry date (YYYY-MM-DD)", "expiry")
        ]
        for index, (label, key) in enumerate(fields):
            r, c = divmod(index, 3)
            tk.Label(form, text=label, bg=WHITE, fg=TEXT, font=FONT).grid(
                row=r*2, column=c, sticky="w", padx=7, pady=(2, 3))
            entry = tk.Entry(form, font=FONT, relief="solid", bd=1, width=24)
            entry.grid(row=r*2+1, column=c, sticky="ew", padx=7, pady=(0, 8), ipady=4)
            self.entries[key] = entry
        self.category = ttk.Combobox(form, state="readonly", width=22)
        self.supplier = ttk.Combobox(form, state="readonly", width=22)
        tk.Label(form, text="Category", bg=WHITE, fg=TEXT, font=FONT).grid(
            row=4, column=0, sticky="w", padx=7)
        self.category.grid(row=5, column=0, sticky="ew", padx=7, pady=(0, 8))
        tk.Label(form, text="Supplier", bg=WHITE, fg=TEXT, font=FONT).grid(
            row=4, column=1, sticky="w", padx=7)
        self.supplier.grid(row=5, column=1, sticky="ew", padx=7, pady=(0, 8))
        for c in range(3):
            form.grid_columnconfigure(c, weight=1)

        buttons = tk.Frame(self, bg=BG)
        buttons.pack(fill="x", pady=10)
        for text, command in [
            ("Add product", self.add_product), ("Update", self.update_product),
            ("Delete", self.delete_product), ("Clear", self.clear_form)
        ]:
            tk.Button(buttons, text=text, command=command, bg=PRIMARY if text != "Delete" else DANGER,
                      fg=WHITE, relief="flat", font=FONT_BOLD, padx=12, pady=7).pack(
                          side="left", padx=(0, 8))

        searchrow = tk.Frame(self, bg=BG)
        searchrow.pack(fill="x", pady=(0, 8))
        tk.Label(searchrow, text="Search product:", bg=BG, fg=TEXT, font=FONT).pack(side="left")
        self.search = tk.Entry(searchrow, font=FONT, width=30)
        self.search.pack(side="left", padx=8, ipady=4)
        tk.Button(searchrow, text="Search", command=self.refresh, bg=SIDEBAR,
                  fg=WHITE, relief="flat", padx=12).pack(side="left")
        tk.Button(searchrow, text="Show all", command=lambda: (self.search.delete(0, "end"), self.refresh()),
                  bg=SIDEBAR, fg=WHITE, relief="flat", padx=12).pack(side="left", padx=8)

        cols = ("id", "name", "category", "supplier", "qty", "purchase", "selling", "low", "expiry")
        self.table = ttk.Treeview(self, columns=cols, show="headings")
        headings = ["ID", "Product", "Category", "Supplier", "Qty", "Purchase", "Selling", "Low level", "Expiry"]
        widths = [45, 155, 120, 120, 55, 80, 80, 75, 95]
        for col, heading, width in zip(cols, headings, widths):
            self.table.heading(col, text=heading)
            self.table.column(col, width=width, anchor="w")
        self.table.pack(fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.select_row)
        self.load_options()
        self.refresh()

    def load_options(self):
        con = connect_db()
        cur = con.cursor()
        cur.execute("SELECT category_id, category_name FROM categories ORDER BY category_name")
        self.categories = cur.fetchall()
        cur.execute("SELECT supplier_id, supplier_name FROM suppliers ORDER BY supplier_name")
        self.suppliers = cur.fetchall()
        self.category["values"] = [x[1] for x in self.categories]
        self.supplier["values"] = [x[1] for x in self.suppliers]
        cur.close(); con.close()

    def get_form_data(self):
        name = self.entries["name"].get().strip()
        if not name:
            raise ValueError("Product name is required.")
        try:
            quantity = int(self.entries["quantity"].get())
            low = int(self.entries["low"].get() or "5")
            purchase = float(self.entries["purchase"].get())
            selling = float(self.entries["selling"].get())
        except ValueError:
            raise ValueError("Quantity, low-stock level and prices must be valid numbers.")
        if quantity < 0 or low < 0 or purchase < 0 or selling < 0:
            raise ValueError("Quantity, low-stock level and prices cannot be negative.")
        expiry = self.entries["expiry"].get().strip() or None
        if expiry:
            try:
                datetime.strptime(expiry, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Expiry date must use YYYY-MM-DD format.")
        category_name = self.category.get()
        supplier_name = self.supplier.get()
        category_id = next((x[0] for x in self.categories if x[1] == category_name), None)
        supplier_id = next((x[0] for x in self.suppliers if x[1] == supplier_name), None)
        return (name, category_id, supplier_id, quantity, purchase, selling, low, expiry)

    def add_product(self):
        try:
            data = self.get_form_data()
            con = connect_db(); cur = con.cursor()
            cur.execute("""INSERT INTO products
                (product_name, category_id, supplier_id, quantity, purchase_price,
                 selling_price, low_stock_level, expiry_date)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""", data)
            con.commit(); cur.close(); con.close()
            messagebox.showinfo("Success", "Product added successfully.")
            self.clear_form(); self.refresh()
        except Exception as exc:
            messagebox.showerror("Could not add product", str(exc))

    def update_product(self):
        if self.selected_id is None:
            messagebox.showwarning("Select product", "Select a product from the table first.")
            return
        try:
            data = self.get_form_data()
            con = connect_db(); cur = con.cursor()
            cur.execute("""UPDATE products SET product_name=%s, category_id=%s, supplier_id=%s,
                quantity=%s, purchase_price=%s, selling_price=%s, low_stock_level=%s,
                expiry_date=%s WHERE product_id=%s""", data + (self.selected_id,))
            con.commit(); cur.close(); con.close()
            messagebox.showinfo("Success", "Product updated.")
            self.clear_form(); self.refresh()
        except Exception as exc:
            messagebox.showerror("Could not update product", str(exc))

    def delete_product(self):
        if self.selected_id is None:
            messagebox.showwarning("Select product", "Select a product from the table first.")
            return
        if not messagebox.askyesno("Confirm delete", "Delete the selected product? Products with sales history cannot be deleted."):
            return
        try:
            con = connect_db(); cur = con.cursor()
            cur.execute("DELETE FROM products WHERE product_id=%s", (self.selected_id,))
            con.commit(); cur.close(); con.close()
            self.clear_form(); self.refresh()
        except Exception as exc:
            messagebox.showerror("Could not delete product", str(exc))

    def refresh(self):
        try:
            con = connect_db(); cur = con.cursor()
            term = "%" + self.search.get().strip() + "%"
            cur.execute("""SELECT p.product_id, p.product_name, COALESCE(c.category_name,''),
                COALESCE(s.supplier_name,''), p.quantity, p.purchase_price, p.selling_price,
                p.low_stock_level, COALESCE(DATE_FORMAT(p.expiry_date,'%Y-%m-%d'),'')
                FROM products p LEFT JOIN categories c ON p.category_id=c.category_id
                LEFT JOIN suppliers s ON p.supplier_id=s.supplier_id
                WHERE p.product_name LIKE %s ORDER BY p.product_id DESC""", (term,))
            rows = cur.fetchall()
            self.table.delete(*self.table.get_children())
            for row in rows: self.table.insert("", "end", values=row)
            cur.close(); con.close()
        except Exception as exc:
            messagebox.showerror("Product list error", str(exc))

    def select_row(self, event=None):
        selection = self.table.selection()
        if not selection: return
        values = self.table.item(selection[0], "values")
        self.selected_id = int(values[0])
        keys = ["name", "quantity", "purchase", "selling", "low", "expiry"]
        vals = [values[1], values[4], values[5], values[6], values[7], values[8]]
        for key, value in zip(keys, vals):
            self.entries[key].delete(0, "end")
            self.entries[key].insert(0, value)
        self.category.set(values[2]); self.supplier.set(values[3])

    def clear_form(self):
        self.selected_id = None
        for entry in self.entries.values(): entry.delete(0, "end")
        self.category.set(""); self.supplier.set("")
        for item in self.table.selection(): self.table.selection_remove(item)
