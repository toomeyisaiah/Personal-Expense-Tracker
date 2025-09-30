import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class ExpenseTracker:
    def __init__(self, filename="expenses.json"):
        self.filename = filename
        self.expenses = []
        self.load_expenses()

    def load_expenses(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as file:
                    self.expenses = json.load(file)
            except Exception as e:
                print(f"Error loading expenses: {e}")
                self.expenses = []

    def save_expenses(self):
        try:
            with open(self.filename, "w") as file:
                json.dump(self.expenses, file, indent=2)
        except Exception as e:
            print(f"Error saving expenses: {e}")

    def add_expense(self, description, amount, category):
        expense = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "description": description,
            "amount": float(amount),
            "category": category
        }
        self.expenses.append(expense)
        self.save_expenses()
        return True

    def get_expenses(self):
        return self.expenses

    def get_summary_by_category(self):
        summary = {}
        for expense in self.expenses:
            category = expense['category']
            amount = expense['amount']
            summary[category] = summary.get(category, 0) + amount
        return summary

class ExpenseTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Expense Tracker")
        self.tracker = ExpenseTracker()
        self.setup_gui()

    def setup_gui(self):
        # Frame for adding expenses
        add_frame = ttk.LabelFrame(self.root, text="Add Expense", padding=10)
        add_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(add_frame, text="Description:").grid(row=0, column=0, padx=5, pady=5)
        self.desc_entry = ttk.Entry(add_frame)
        self.desc_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Amount:").grid(row=1, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(add_frame)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Category:").grid(row=2, column=0, padx=5, pady=5)
        self.category_entry = ttk.Entry(add_frame)
        self.category_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(add_frame, text="Add Expense", command=self.add_expense).grid(row=3, column=0, columnspan=2, pady=10)

        # Frame for viewing expenses
        view_frame = ttk.LabelFrame(self.root, text="Actions", padding=10)
        view_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ttk.Button(view_frame, text="View All Expenses", command=self.view_expenses).grid(row=0, column=0, pady=5)
        ttk.Button(view_frame, text="View Summary by Category", command=self.view_summary).grid(row=1, column=0, pady=5)

        # Text area for displaying expenses or summaries
        self.display_text = tk.Text(self.root, height=15, width=50)
        self.display_text.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    def add_expense(self):
        desc = self.desc_entry.get()
        amount = self.amount_entry.get()
        category = self.category_entry.get()

        if not desc or not amount or not category:
            messagebox.showerror("Input Error", "All fields are required!")
            return

        try:
            amount = float(amount)
            self.tracker.add_expense(desc, amount, category)
            messagebox.showinfo("Success", "Expense added successfully!")
            # Clear the input fields after successful addition
            self.desc_entry.delete(0, tk.END)
            self.amount_entry.delete(0, tk.END)
            self.category_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def view_expenses(self):
        self.display_text.delete(1.0, tk.END)  # Clear previous content
        expenses = self.tracker.get_expenses()
        if not expenses:
            self.display_text.insert(tk.END, "No expenses recorded.\n")
        else:
            self.display_text.insert(tk.END, "All Expenses:\n")
            self.display_text.insert(tk.END, "-" * 50 + "\n")
            for exp in expenses:
                self.display_text.insert(tk.END, f"Date: {exp['date']}\n")
                self.display_text.insert(tk.END, f"Description: {exp['description']}\n")
                self.display_text.insert(tk.END, f"Amount: ${exp['amount']:.2f}\n")
                self.display_text.insert(tk.END, f"Category: {exp['category']}\n")
                self.display_text.insert(tk.END, "-" * 50 + "\n")

    def view_summary(self):
        self.display_text.delete(1.0, tk.END)  # Clear previous content
        summary = self.tracker.get_summary_by_category()
        if not summary:
            self.display_text.insert(tk.END, "No expenses recorded.\n")
        else:
            self.display_text.insert(tk.END, "Summary by Category:\n")
            self.display_text.insert(tk.END, "-" * 50 + "\n")
            for category, total in summary.items():
                self.display_text.insert(tk.END, f"Category: {category}\n")
                self.display_text.insert(tk.END, f"Total Spent: ${total:.2f}\n")
                self.display_text.insert(tk.END, "-" * 50 + "\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerGUI(root)
    root.mainloop()