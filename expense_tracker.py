import json
import os
from datetime import datetime

class ExpenseTracker:
    def __init__(self, filename="expenses.json"):
        self.filename = filename
        self.expenses = []
        self.load_expenses()

    def load_expenses(self):
        """Load expenses from a JSON file if it exists."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as file:
                    self.expenses = json.load(file)
            except Exception as e:
                print(f"Error loading expenses: {e}")
                self.expenses = []

    def save_expenses(self):
        """Save expenses to a JSON file."""
        try:
            with open(self.filename, "w") as file:
                json.dump(self.expenses, file, indent=2)
        except Exception as e:
            print(f"Error saving expenses: {e}")

    def add_expense(self, description, amount, category):
        """Add a new expense to the list."""
        expense = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "description": description,
            "amount": float(amount),
            "category": category
        }
        self.expenses.append(expense)
        self.save_expenses()
        print("Expense added successfully!")

    def view_expenses(self):
        """Display all expenses."""
        if not self.expenses:
            print("No expenses recorded.")
            return
        print("\nYour Expenses:")
        for i, expense in enumerate(self.expenses, 1):
            print(f"{i}. {expense['date']} - {expense['description']} "
                  f"({expense['category']}): ${expense['amount']:.2f}")

    def view_summary_by_category(self):
        """Display total expenses by category."""
        if not self.expenses:
            print("No expenses recorded.")
            return
        summary = {}
        for expense in self.expenses:
            category = expense['category']
            amount = expense['amount']
            summary[category] = summary.get(category, 0) + amount
        
        print("\nExpense Summary by Category:")
        for category, total in summary.items():
            print(f"{category}: ${total:.2f}")

def main():
    tracker = ExpenseTracker()
    while True:
        print("\n=== Personal Expense Tracker ===")
        print("1. Add Expense")
        print("2. View All Expenses")
        print("3. View Summary by Category")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            description = input("Enter description: ")
            try:
                amount = float(input("Enter amount: "))
                category = input("Enter category (e.g., Food, Transport): ")
                tracker.add_expense(description, amount, category)
            except ValueError:
                print("Invalid amount. Please enter a number.")
        elif choice == "2":
            tracker.view_expenses()
        elif choice == "3":
            tracker.view_summary_by_category()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()