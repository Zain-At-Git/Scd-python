from datetime import datetime


class Transaction:
    def __init__(self, t_type, category, amount):
        if t_type not in ["Income", "Expense"]:
            raise ValueError("Invalid transaction type")
        if amount <= 0:
            raise ValueError("Amount must be positive")

        self.t_type = t_type
        self.category = category
        self.amount = amount
        self.date = datetime.now().strftime("%Y-%m-%d")


class BudgetManager:
    def __init__(self, db):
        self.db = db

    def set_budget(self, category, amount):
        if amount <= 0:
            raise ValueError("Budget must be positive")
        self.db.set_budget(category, amount)

    def is_over_budget(self, category):
        budget = self.db.get_budget(category)
        if not budget:
            return False

        total_expense = self.db.get_category_expense(category)
        return total_expense > budget[0]


class SavingsManager:
    def __init__(self, db):
        self.db = db

    def calculate_savings(self):
        total_income = self.db.get_total_by_type("Income")
        total_expense = self.db.get_total_by_type("Expense")
        return total_income - total_expense
