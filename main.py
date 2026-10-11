import tkinter as tk
from tkinter import ttk, messagebox
from database import initialize_database
from login import LoginWindow
from dashboard import DashboardPage
from product import ProductPage
from sales import SalesPage
from supplier import SupplierPage
from report import ReportPage
from style import *

class InventoryApp:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        root.title("Smart Inventory Management System")
        root.geometry("1250x760")
        root.minsize(1000, 650)
        root.configure(bg=BG)
        self.configure_styles()

        sidebar = tk.Frame(root, bg=SIDEBAR, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="SMART\\nINVENTORY", bg=SIDEBAR, fg=WHITE,
                 font=("Segoe UI", 19, "bold"), justify="left").pack(
                     anchor="w", padx=22, pady=(28, 8))
        tk.Label(sidebar, text=f"Signed in: {username}", bg=SIDEBAR, fg="#CBD5E1",
                 font=("Segoe UI", 9)).pack(anchor="w", padx=22, pady=(0, 24))

        self.content = tk.Frame(root, bg=BG)
        self.content.pack(side="left", fill="both", expand=True, padx=22, pady=20)
        self.pages = {}
        nav = [
            ("Dashboard", DashboardPage),
            ("Products", ProductPage),
            ("Sales", SalesPage),
            ("Suppliers", SupplierPage),
            ("Reports", ReportPage)
        ]
        for label, page_class in nav:
            tk.Button(sidebar, text="   " + label, anchor="w", command=lambda l=label, p=page_class: self.show_page(l,p),
                      bg=SIDEBAR, fg=WHITE, activebackground=PRIMARY,
                      activeforeground=WHITE, relief="flat", font=("Segoe UI", 11),
                      padx=18, pady=12, cursor="hand2").pack(fill="x", padx=8, pady=2)
        tk.Frame(sidebar, bg="#334155", height=1).pack(fill="x", padx=16, pady=20)
        tk.Button(sidebar, text="   Refresh current page", command=self.refresh_current,
                  anchor="w", bg=SIDEBAR, fg="#CBD5E1", relief="flat",
                  font=FONT, padx=18, pady=10).pack(fill="x", padx=8)
        tk.Button(sidebar, text="   Logout", command=self.logout, anchor="w",
                  bg=SIDEBAR, fg="#FCA5A5", relief="flat", font=FONT,
                  padx=18, pady=10).pack(side="bottom", fill="x", padx=8, pady=16)
        self.show_page("Dashboard", DashboardPage)

    def configure_styles(self):
        style=ttk.Style()
        try: style.theme_use("clam")
        except tk.TclError: pass
        style.configure("Treeview", background=WHITE, fieldbackground=WHITE,
                        foreground=TEXT, rowheight=29, font=FONT)
        style.configure("Treeview.Heading", background="#E8EEF7", foreground=TEXT,
                        font=FONT_BOLD, padding=7)
        style.map("Treeview", background=[("selected", "#DBEAFE")],
                  foreground=[("selected", TEXT)])

    def show_page(self, name, page_class):
        for child in self.content.winfo_children():
            child.destroy()
        try:
            page = page_class(self.content)
            page.pack(fill="both", expand=True)
            self.current_page = page
            self.current_name = name
        except Exception as exc:
            messagebox.showerror("Page error", f"Could not open {name}.\n\n{exc}")

    def refresh_current(self):
        if hasattr(self, "current_page"):
            if hasattr(self.current_page, "refresh"):
                self.current_page.refresh()
            if hasattr(self.current_page, "load_products"):
                self.current_page.load_products()
            if hasattr(self.current_page, "load_options"):
                self.current_page.load_options()

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            for widget in self.root.winfo_children():
                widget.destroy()
            LoginWindow(self.root, self.login_success)

    def login_success(self, username):
        for widget in self.root.winfo_children():
            widget.destroy()
        InventoryApp(self.root, username)

def main():
    root=tk.Tk()
    root.withdraw()
    try:
        initialize_database()
    except Exception as exc:
        root.deiconify()
        messagebox.showerror(
            "MySQL setup error",
            "Could not initialize the database.\n\n"
            f"{exc}\n\nOpen database.py and replace YOUR_MYSQL_PASSWORD "
            "with your MySQL root password."
        )
        root.destroy()
        return
    root.deiconify()
    LoginWindow(root, lambda username: start_app(root, username))
    root.mainloop()

def start_app(root, username):
    for widget in root.winfo_children():
        widget.destroy()
    InventoryApp(root, username)

if __name__ == "__main__":
    main()
