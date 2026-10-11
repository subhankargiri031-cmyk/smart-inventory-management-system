import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_db
from style import *

class SupplierPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.selected_id = None
        tk.Label(self, text="Supplier Management", font=FONT_TITLE, bg=BG, fg=TEXT).pack(
            anchor="w", pady=(0, 15))
        form = tk.Frame(self, bg=WHITE, padx=14, pady=14,
                        highlightbackground=BORDER, highlightthickness=1)
        form.pack(fill="x")
        self.fields = {}
        for col, (label, key) in enumerate([
            ("Supplier name", "name"), ("Phone", "phone"),
            ("Email", "email"), ("Address", "address")
        ]):
            tk.Label(form, text=label, bg=WHITE, fg=TEXT, font=FONT).grid(
                row=0, column=col, sticky="w", padx=6)
            entry = tk.Entry(form, font=FONT, width=22)
            entry.grid(row=1, column=col, padx=6, pady=8, ipady=4, sticky="ew")
            self.fields[key] = entry
            form.grid_columnconfigure(col, weight=1)
        actions = tk.Frame(self, bg=BG); actions.pack(fill="x", pady=10)
        for text, cmd in [("Add supplier", self.add), ("Update", self.update),
                          ("Delete", self.delete), ("Clear", self.clear)]:
            tk.Button(actions, text=text, command=cmd, bg=DANGER if text=="Delete" else PRIMARY,
                      fg=WHITE, font=FONT_BOLD, relief="flat", padx=12, pady=7).pack(
                          side="left", padx=(0, 8))
        self.table = ttk.Treeview(self, columns=("id","name","phone","email","address"), show="headings")
        for col, title, width in [
            ("id","ID",55),("name","Supplier",180),("phone","Phone",130),
            ("email","Email",210),("address","Address",220)
        ]:
            self.table.heading(col, text=title); self.table.column(col, width=width, anchor="w")
        self.table.pack(fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.select)
        self.refresh()

    def values(self):
        name = self.fields["name"].get().strip()
        if not name: raise ValueError("Supplier name is required.")
        return (name, self.fields["phone"].get().strip(), self.fields["email"].get().strip(),
                self.fields["address"].get().strip())

    def add(self):
        try:
            con=connect_db(); cur=con.cursor()
            cur.execute("INSERT INTO suppliers (supplier_name,phone,email,address) VALUES (%s,%s,%s,%s)", self.values())
            con.commit(); cur.close(); con.close()
            self.clear(); self.refresh(); messagebox.showinfo("Success","Supplier added.")
        except Exception as exc: messagebox.showerror("Supplier error",str(exc))

    def update(self):
        if self.selected_id is None:
            messagebox.showwarning("Select supplier","Select a supplier first."); return
        try:
            con=connect_db(); cur=con.cursor()
            cur.execute("UPDATE suppliers SET supplier_name=%s,phone=%s,email=%s,address=%s WHERE supplier_id=%s",
                        self.values()+(self.selected_id,))
            con.commit(); cur.close(); con.close(); self.clear(); self.refresh()
        except Exception as exc: messagebox.showerror("Supplier error",str(exc))

    def delete(self):
        if self.selected_id is None:
            messagebox.showwarning("Select supplier","Select a supplier first."); return
        if not messagebox.askyesno("Confirm","Delete selected supplier?"): return
        try:
            con=connect_db(); cur=con.cursor()
            cur.execute("DELETE FROM suppliers WHERE supplier_id=%s",(self.selected_id,))
            con.commit(); cur.close(); con.close(); self.clear(); self.refresh()
        except Exception as exc: messagebox.showerror("Supplier error",str(exc))

    def select(self,event=None):
        sel=self.table.selection()
        if not sel: return
        row=self.table.item(sel[0],"values"); self.selected_id=int(row[0])
        for key,val in zip(("name","phone","email","address"),row[1:]):
            self.fields[key].delete(0,"end"); self.fields[key].insert(0,val)

    def clear(self):
        self.selected_id=None
        for entry in self.fields.values(): entry.delete(0,"end")
        for item in self.table.selection(): self.table.selection_remove(item)

    def refresh(self):
        try:
            con=connect_db(); cur=con.cursor()
            cur.execute("SELECT supplier_id,supplier_name,COALESCE(phone,''),COALESCE(email,''),COALESCE(address,'') FROM suppliers ORDER BY supplier_name")
            rows=cur.fetchall(); self.table.delete(*self.table.get_children())
            for row in rows: self.table.insert("","end",values=row)
            cur.close(); con.close()
        except Exception as exc: messagebox.showerror("Supplier list error",str(exc))
