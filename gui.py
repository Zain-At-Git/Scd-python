import tkinter as tk
from tkinter import messagebox
from db import DatabaseHandler
from logic import Transaction, BudgetManager, SavingsManager


class FinanceGUI:
    def __init__(self, root):
        self.db = DatabaseHandler()
        self.budget_manager = BudgetManager(self.db)
        self.savings_manager = SavingsManager(self.db)

        root.title("Personal Finance Manager")
        root.geometry("640x750")
        root.configure(bg="#0b1c2d")
        root.resizable(False, False)

        self.type_var = tk.StringVar(value="Expense")
        self.category_var = tk.StringVar(value="Food")
        self.amount_var = tk.StringVar()
        self.budget_var = tk.StringVar()

        bg_card = "#12263f"
        accent = "#ff8c00"
        text = "#ecf0f1"

        tk.Label(
            root,
            text="Personal Finance Manager",
            font=("Segoe UI", 20, "bold"),
            bg="#0b1c2d",
            fg=accent
        ).pack(pady=20)

        self.categories = [
            "Food", "Rent", "Transport",
            "Shopping", "Utilities",
            "Entertainment", "Salary", "Other"
        ]

        card = tk.Frame(root, bg=bg_card)
        card.pack(padx=25, pady=10, fill="x")

        self.title(card, "Add Transaction", accent)

        self.label(card, "Type", text)
        tk.OptionMenu(card, self.type_var, "Income", "Expense").pack()

        self.label(card, "Category", text)
        tk.OptionMenu(card, self.category_var, *self.categories).pack()

        self.label(card, "Amount", text)
        tk.Entry(card, textvariable=self.amount_var).pack()

        tk.Button(
            card, text="Add Transaction",
            command=self.add_transaction,
            bg=accent, fg="black",
            font=("Segoe UI", 11, "bold"),
            relief="flat", padx=20, pady=8
        ).pack(pady=15)

        self.title(card, "Budget", accent)

        tk.Entry(card, textvariable=self.budget_var).pack()

        tk.Button(
            card, text="Save Budget",
            command=self.set_budget,
            bg=accent, fg="black",
            font=("Segoe UI", 11, "bold"),
            relief="flat", padx=20, pady=8
        ).pack(pady=15)

        tk.Button(
            root, text="View Summary",
            command=self.view_summary,
            bg="#1f3b64", fg="white",
            font=("Segoe UI", 12, "bold"),
            relief="flat", padx=30, pady=10
        ).pack(pady=10)

        tk.Button(
            root, text="View Savings",
            command=self.view_savings,
            bg=accent, fg="black",
            font=("Segoe UI", 12, "bold"),
            relief="flat", padx=30, pady=10
        ).pack(pady=10)

    # ---------- UI Helpers ----------
    def label(self, parent, text, color):
        tk.Label(parent, text=text, bg=parent["bg"], fg=color).pack()

    def title(self, parent, text, color):
        tk.Label(
            parent, text=text,
            font=("Segoe UI", 15, "bold"),
            bg=parent["bg"], fg=color
        ).pack(pady=10)

    def clear_inputs(self):
        self.amount_var.set("")
        self.budget_var.set("")

    # ---------- Actions with Exception Handling ----------
    def add_transaction(self):
        
        try:
            if not self.amount_var.get():
                raise ValueError("Amount field is required")

            amount = float(self.amount_var.get())

            transaction = Transaction(
                self.type_var.get(),
                self.category_var.get(),
                amount
            )

            self.db.add_transaction(
                transaction.t_type,
                transaction.category,
                transaction.amount,
                transaction.date
            )

            messagebox.showinfo("Success", "Transaction added successfully")
            self.clear_inputs()

        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception:
            messagebox.showerror(
                "System Error",
                "Something went wrong while adding transaction"
            )

    def set_budget(self):
        try:
            if not self.budget_var.get():
                raise ValueError("Budget field is required")

            amount = float(self.budget_var.get())

            self.budget_manager.set_budget(
                self.category_var.get(),
                amount
            )

            messagebox.showinfo("Success", "Budget saved successfully")
            self.clear_inputs()

        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception:
            messagebox.showerror(
                "System Error",
                "Failed to save budget"
            )

    def view_summary(self):
        try:
            data = self.db.fetch_transactions()
            if not data:
                messagebox.showinfo("Summary", "No records found")
                return

            summary = "\n".join(
                f"{row[1]} | {row[2]} | {row[3]}" for row in data
            )

            messagebox.showinfo("Transaction Summary", summary)

        except Exception:
            messagebox.showerror(
                "System Error",
                "Unable to fetch transaction summary"
            )

    def view_savings(self):
        try:
            savings = self.savings_manager.calculate_savings()
            messagebox.showinfo(
                "Savings",
                f"Total Savings: {savings:.2f}"
            )
        except Exception:
            messagebox.showerror(
                "System Error",
                "Unable to calculate savings"
            )
