import unittest
from logic import Transaction
from db import DatabaseHandler


class TestFinanceApp(unittest.TestCase):

    def test_valid_transaction(self):
        t = Transaction("Income", "Salary", 5000)
        self.assertEqual(t.amount, 5000)

    def test_invalid_amount(self):
        with self.assertRaises(ValueError):
            Transaction("Expense", "Food", -100)

    def test_database_insert(self):
        db = DatabaseHandler(":memory:")
        db.add_transaction("Expense", "Food", 200, "2025-01-01")
        records = db.fetch_transactions()
        self.assertEqual(len(records), 1)


if __name__ == "__main__":
    unittest.main()
