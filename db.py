import sqlite3


class DatabaseHandler:
    def __init__(self, db_name="finance.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            category TEXT PRIMARY KEY,
            limit_amount REAL NOT NULL
        )
        """)
        self.conn.commit()

    def add_transaction(self, t_type, category, amount, date):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO transactions (type, category, amount, date) VALUES (?, ?, ?, ?)",
            (t_type, category, amount, date)
        )
        self.conn.commit()

    def fetch_transactions(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM transactions")
        return cursor.fetchall()

    def set_budget(self, category, limit_amount):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO budgets (category, limit_amount)
        VALUES (?, ?)
        ON CONFLICT(category)
        DO UPDATE SET limit_amount = excluded.limit_amount
        """, (category, limit_amount))
        self.conn.commit()

    def get_budget(self, category):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT limit_amount FROM budgets WHERE category=?",
            (category,)
        )
        return cursor.fetchone()

    # ---------- CORRECT CALCULATIONS ----------
    def get_total_by_type(self, t_type):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT SUM(amount) FROM transactions WHERE type=?",
            (t_type,)
        )
        result = cursor.fetchone()[0]
        return result if result else 0

    def get_category_expense(self, category):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT SUM(amount) FROM transactions WHERE type='Expense' AND category=?",
            (category,)
        )
        result = cursor.fetchone()[0]
        return result if result else 0

    def close(self):
        self.conn.close()
