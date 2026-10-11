import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from database import connect_db
from style import *

class ReportPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        tk.Label(self, text="Reports & History", font=FONT_TITLE, bg=BG, fg=TEXT).pack(
            anchor="w", pady=(0, 12))
        actions = tk.Frame(self, bg=BG); actions.pack(fill="x", pady=(0, 10))
        tk.Button(actions, text="Refresh reports", command=self.refresh, bg=PRIMARY,
                  fg=WHITE, relief="flat", font=FONT_BOLD, padx=12, pady=7).pack(side="left")
        tk.Button(actions, text="Export CSV", command=self.export_csv, bg=SIDEBAR,
                  fg=WHITE, relief="flat", font=FONT_BOLD, padx=12, pady=7).pack(side="left", padx=8)
        self.summary = tk.Label(self, text="", bg=BG, fg=TEXT, font=("Segoe UI", 12, "bold"))
        self.summary.pack(anchor="w", pady=(0, 12))
        self.table = ttk.Treeview(self, columns=("id","product","qty","unit","total","date"), show="headings")
        for col, label, width in [
            ("id","Sale ID",70),("product","Product",240),("qty","Quantity",90),
            ("unit","Unit price",120),("total","Total",120),("date","Date",180)
        ]:
            self.table.heading(col,text=label); self.table.column(col,width=width,anchor="w")
        self.table.pack(fill="both", expand=True)
        self.rows=[]; self.refresh()

    def refresh(self):
        try:
            con=connect_db(); cur=con.cursor()
            cur.execute("SELECT COUNT(*), COALESCE(SUM(total_amount),0) FROM sales")
            count,total=cur.fetchone()
            cur.execute("SELECT COALESCE(SUM(quantity*purchase_price),0) FROM products")
            stock_value=cur.fetchone()[0]
            self.summary.config(text=f"Transactions: {count}     Sales revenue: ₹{float(total):,.2f}     Current stock value: ₹{float(stock_value):,.2f}")
            cur.execute("""SELECT s.sale_id,p.product_name,s.quantity,s.unit_price,s.total_amount,
                DATE_FORMAT(s.sale_date,'%Y-%m-%d %H:%i:%s')
                FROM sales s JOIN products p ON s.product_id=p.product_id ORDER BY s.sale_date DESC""")
            self.rows=cur.fetchall(); self.table.delete(*self.table.get_children())
            for row in self.rows: self.table.insert("","end",values=row)
            cur.close(); con.close()
        except Exception as exc: messagebox.showerror("Report error",str(exc))

    def export_csv(self):
        if not self.rows:
            messagebox.showinfo("No data","There are no sales records to export."); return
        path=filedialog.asksaveasfilename(defaultextension=".csv",
            filetypes=[("CSV files","*.csv")], initialfile="sales_report.csv")
        if not path: return
        try:
            with open(path,"w",newline="",encoding="utf-8-sig") as file:
                writer=csv.writer(file)
                writer.writerow(["Sale ID","Product","Quantity","Unit Price","Total","Sale Date"])
                writer.writerows(self.rows)
            messagebox.showinfo("Export complete",f"Report saved to:\n{path}")
        except Exception as exc: messagebox.showerror("Export error",str(exc))
