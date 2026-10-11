import tkinter as tk
from tkinter import messagebox
from database import check_login
from style import *

class LoginWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        root.title("Smart Inventory | Login")
        root.geometry("420x430")
        root.resizable(False, False)
        root.configure(bg=BG)

        card = tk.Frame(root, bg=WHITE, padx=34, pady=30,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True, padx=24, pady=24)

        tk.Label(card, text="SMART INVENTORY", font=("Segoe UI", 19, "bold"),
                 bg=WHITE, fg=TEXT).pack(pady=(10, 5))
        tk.Label(card, text="Sign in to manage your stock", font=FONT,
                 bg=WHITE, fg=MUTED).pack(pady=(0, 25))

        tk.Label(card, text="Username", bg=WHITE, fg=TEXT, font=FONT_BOLD,
                 anchor="w").pack(fill="x")
        self.username = tk.Entry(card, font=FONT, relief="solid", bd=1)
        self.username.pack(fill="x", ipady=8, pady=(5, 15))
        self.username.insert(0, "admin")

        tk.Label(card, text="Password", bg=WHITE, fg=TEXT, font=FONT_BOLD,
                 anchor="w").pack(fill="x")
        self.password = tk.Entry(card, show="*", font=FONT, relief="solid", bd=1)
        self.password.pack(fill="x", ipady=8, pady=(5, 20))
        self.password.bind("<Return>", lambda event: self.login())

        tk.Button(card, text="LOGIN", command=self.login, bg=PRIMARY, fg=WHITE,
                  activebackground=PRIMARY_DARK, activeforeground=WHITE,
                  font=FONT_BOLD, relief="flat", cursor="hand2").pack(fill="x", ipady=8)
        tk.Label(card, text="First login: admin / admin123", bg=WHITE,
                 fg=MUTED, font=("Segoe UI", 9)).pack(pady=(16, 0))

    def login(self):
        username = self.username.get().strip()
        password = self.password.get()
        if not username or not password:
            messagebox.showwarning("Missing details", "Enter username and password.")
            return
        try:
            if check_login(username, password):
                self.on_success(username)
            else:
                messagebox.showerror("Login failed", "Incorrect username or password.")
        except Exception as exc:
            messagebox.showerror(
                "Database error",
                f"Could not connect to MySQL.\n\n{exc}\n\n"
                "Check the password in database.py and ensure MySQL is running."
            )
