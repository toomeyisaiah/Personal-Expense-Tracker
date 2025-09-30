import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import hashlib
from datetime import datetime
import webbrowser
import csv
from PIL import Image, ImageTk
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt



# ---------- Styling ----------
def setup_styles():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground="#0052cc", background="#e7f0fa")
    style.configure("SubHeader.TLabel", font=("Segoe UI", 10, "italic"), foreground="#333", background="#e7f0fa")
    style.configure("TLabel", font=("Segoe UI", 11), background="#fafafa")
    style.configure("TButton", font=("Segoe UI", 11), padding=(8,4))
    style.configure("TLabelframe", background="#f7faff", font=("Segoe UI", 12, "bold"))
    style.configure("TLabelframe.Label", font=("Segoe UI", 12, "bold"), foreground="#3466af", background="#f7faff")
    style.map("TButton", background=[('active', '#3466af'), ('!active', '#0052cc')],
              foreground=[('disabled', '#cccccc'), ('active', '#ffffff')])

# ---------- Storage ----------
class SecureStorage:
    BASE_DIR = os.path.join(os.path.expanduser("~"), ".expense_tracker_data")

    @staticmethod
    def list_users():
        if not os.path.exists(SecureStorage.BASE_DIR):
            return []
        return [d for d in os.listdir(SecureStorage.BASE_DIR) if os.path.isdir(os.path.join(SecureStorage.BASE_DIR, d))]

    def __init__(self, user_id):
        os.makedirs(self.BASE_DIR, exist_ok=True)
        self.user_dir = os.path.join(self.BASE_DIR, user_id)
        os.makedirs(self.user_dir, exist_ok=True)
        self.pin_file = os.path.join(self.user_dir, "pin.hash")
        self.data_file = os.path.join(self.user_dir, "expenses.json")
        self.category_file = os.path.join(self.user_dir, "categories.json")

    def save_pin(self, pin):
        hashed_pin = hashlib.sha256(pin.encode()).hexdigest()
        with open(self.pin_file, 'w') as f:
            f.write(hashed_pin)

    def check_pin(self, pin):
        hashed_pin = hashlib.sha256(pin.encode()).hexdigest()
        if os.path.exists(self.pin_file):
            with open(self.pin_file, 'r') as f:
                return hashed_pin == f.read()
        return False

    def pin_exists(self):
        return os.path.exists(self.pin_file)

    def reset_pin(self):
        if os.path.exists(self.pin_file):
            os.remove(self.pin_file)

    def load_categories(self):
        try:
            if os.path.exists(self.category_file):
                with open(self.category_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print("Error loading categories:", e)
        return ["Food", "Transport", "Utilities", "Entertainment", "Health", "Other"]

    def save_categories(self, categories):
        try:
            with open(self.category_file, 'w') as f:
                json.dump(categories, f, indent=2)
        except Exception as e:
            print("Error saving categories:", e)

# ---------- Expense Tracker ----------
class ExpenseTracker:
    def __init__(self, storage):
        self.storage = storage
        self.expenses = []
        self.load_expenses()

    def load_expenses(self):
        try:
            if os.path.exists(self.storage.data_file):
                with open(self.storage.data_file, "r") as f:
                    self.expenses = json.load(f)
        except Exception as e:
            print("Error loading expenses:", e)
            self.expenses = []

    def save_expenses(self):
        try:
            with open(self.storage.data_file, "w") as f:
                json.dump(self.expenses, f, indent=2)
        except Exception as e:
            print("Error saving expenses:", e)

    def add_expense(self, description, amount, category):
        expense = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "description": description,
            "amount": float(amount),
            "category": category
        }
        self.expenses.append(expense)
        self.save_expenses()

    def delete_last_expense(self):
        if self.expenses:
            self.expenses.pop()
            self.save_expenses()
            return True
        return False

    def get_expenses(self):
        return self.expenses

    def get_summary_by_category(self):
        summary = {}
        for exp in self.expenses:
            summary[exp['category']] = summary.get(exp['category'], 0) + exp['amount']
        return summary

    def get_monthly_summary(self):
        summary = {}
        for exp in self.expenses:
            dt = datetime.strptime(exp['date'], "%Y-%m-%d %H:%M:%S")
            key = dt.strftime("%Y-%m")
            summary[key] = summary.get(key, 0) + exp['amount']
        return summary

# ---------- GUI Screens ----------
class UserSelectScreen(ttk.Frame):
    def __init__(self, parent, on_user_selected):
        super().__init__(parent, padding=20)
        self.parent = parent
        self.on_user_selected = on_user_selected
        self.pack(fill="both", expand=True)
        self.setup_gui()

    def setup_gui(self):
        for widget in self.winfo_children():
            widget.destroy()

        ttk.Label(self, text="Choose a User", style="Header.TLabel").grid(row=0, column=0, columnspan=3, pady=(0,12))

        # User combobox
        self.user_combo = ttk.Combobox(self, values=SecureStorage.list_users(), state="readonly", font=("Segoe UI", 12))
        if SecureStorage.list_users():
            self.user_combo.set(SecureStorage.list_users()[0])
        self.user_combo.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12)
        
        ttk.Button(self, text="Login", command=self.select_user).grid(row=1, column=2, padx=5)
        ttk.Button(self, text="Delete User", command=self.delete_user).grid(row=2, column=2, padx=5, pady=5)

        # New user creation
        ttk.Label(self, text="Or create a New User:").grid(row=3, column=0, columnspan=3, pady=(18,4))
        self.new_user_entry = ttk.Entry(self, font=("Segoe UI", 12))
        self.new_user_entry.grid(row=4, column=0, columnspan=2, sticky="ew", padx=12)
        ttk.Button(self, text="Create User", command=self.create_user).grid(row=4, column=2, padx=5)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def select_user(self):
        user = self.user_combo.get().strip()
        if user:
            self.destroy()
            self.on_user_selected(user)
        else:
            messagebox.showerror("User", "Please select a user.")

    def create_user(self):
        user = self.new_user_entry.get().strip()
        if not user:
            messagebox.showerror("User", "Enter a username.")
            return
        if user in SecureStorage.list_users():
            messagebox.showerror("User Exists", "Username already taken.")
            return
        self.destroy()
        self.on_user_selected(user)

    def delete_user(self):
        user = self.user_combo.get().strip()
        if not user:
            messagebox.showerror("Delete User", "Select a user to delete")
            return
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to permanently delete user '{user}'?")
        if confirm:
            user_dir = os.path.join(SecureStorage.BASE_DIR, user)
            try:
                import shutil
                shutil.rmtree(user_dir)
                messagebox.showinfo("Deleted", f"User '{user}' deleted successfully")
                # Refresh combobox
                users = SecureStorage.list_users()
                self.user_combo['values'] = users
                if users:
                    self.user_combo.set(users[0])
                else:
                    self.user_combo.set("")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete user: {e}")


class LoginScreen(ttk.Frame):
    def __init__(self, parent, user_id, on_login_success):
        super().__init__(parent, padding=20)
        self.parent = parent
        self.user_id = user_id
        self.storage = SecureStorage(user_id)
        self.on_login_success = on_login_success
        self.pack(fill="both", expand=True)
        self.setup_gui()

    def setup_gui(self):
        for widget in self.winfo_children():
            widget.destroy()
        ttk.Label(self, text=f"💲 BudgetBase v1.0.0\nUser: {self.user_id}", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=(0,22), sticky="ew")
        if self.storage.pin_exists():
            ttk.Label(self, text="Enter PIN:").grid(row=1, column=0, padx=9, pady=11, sticky="w")
            self.pin_entry = ttk.Entry(self, show="*")
            self.pin_entry.grid(row=1, column=1, padx=9, pady=11, sticky="ew")
            ttk.Button(self, text="Login", command=self.check_pin).grid(row=2, column=0, columnspan=2, pady=14)
            ttk.Button(self, text="Reset PIN", command=self.reset_pin).grid(row=3, column=0, columnspan=2, pady=3)
        else:
            ttk.Label(self, text="Set Up New PIN:").grid(row=1, column=0, padx=9, pady=11, sticky="w")
            self.pin_entry = ttk.Entry(self, show="*")
            self.pin_entry.grid(row=1, column=1, padx=9, pady=11, sticky="ew")
            ttk.Label(self, text="Confirm PIN:").grid(row=2, column=0, padx=9, pady=11, sticky="w")
            self.confirm_pin_entry = ttk.Entry(self, show="*")
            self.confirm_pin_entry.grid(row=2, column=1, padx=9, pady=11, sticky="ew")
            ttk.Button(self, text="Set PIN", command=self.set_pin).grid(row=3, column=0, columnspan=2, pady=17)
        self.grid_columnconfigure(1, weight=1)

    def set_pin(self):
        pin = self.pin_entry.get()
        confirm = self.confirm_pin_entry.get()
        if not pin or not confirm:
            messagebox.showerror("Error", "PIN fields cannot be empty")
            return
        if pin != confirm:
            messagebox.showerror("Error", "PINs do not match")
            return
        if len(pin) < 4:
            messagebox.showerror("Error", "PIN must be at least 4 digits")
            return
        self.storage.save_pin(pin)
        messagebox.showinfo("Success", "PIN set successfully! Please log in.")
        self.setup_gui()

    def check_pin(self):
        pin = self.pin_entry.get()
        if self.storage.check_pin(pin):
            self.destroy()
            self.on_login_success(self.storage, self.user_id)
        else:
            messagebox.showerror("Error", "Invalid PIN")

    def reset_pin(self):
        res = messagebox.askyesno("Reset PIN", f"Reset PIN for user '{self.user_id}'? This cannot be undone.")
        if res:
            self.storage.reset_pin()
            messagebox.showinfo("Reset", "PIN reset. Please set a new PIN.")
            self.setup_gui()

# ---------- Expense Tracker GUI ----------
class ExpenseTrackerGUI(ttk.Frame):
    def __init__(self, parent, storage, user_id):
        super().__init__(parent)
        self.parent = parent
        self.storage = storage
        self.tracker = ExpenseTracker(storage)
        self.user_id = user_id
        self.pack(fill="both", expand=True)
        self.categories = self.storage.load_categories()
        self.chart_img = None
        self.setup_gui()

    # ---------- GUI Components ----------
    def setup_gui(self):
        # Clear frame
        for widget in self.winfo_children():
            widget.destroy()

        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(header_frame, text=f"💲 BudgetBase", style="Header.TLabel").pack(side="left")
        ttk.Label(header_frame, text=f"User: {self.user_id} | Developed by Isaiah Toomey", style="SubHeader.TLabel").pack(side="left", padx=10)
        ttk.Button(header_frame, text="Logout", command=self.logout).pack(side="right", padx=5)
        ttk.Button(header_frame, text="Change PIN", command=self.change_pin).pack(side="right", padx=5)

        # Main Frames
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Add Expense
        add_frame = ttk.LabelFrame(main_frame, text="📝 Add Expense", padding=10)
        add_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        add_frame.columnconfigure(1, weight=1)
        ttk.Label(add_frame, text="Description:").grid(row=0, column=0, sticky="w")
        self.desc_entry = ttk.Entry(add_frame)
        self.desc_entry.grid(row=0, column=1, sticky="ew")
        ttk.Label(add_frame, text="Amount:").grid(row=1, column=0, sticky="w")
        self.amount_entry = ttk.Entry(add_frame)
        self.amount_entry.grid(row=1, column=1, sticky="ew")
        ttk.Label(add_frame, text="Category:").grid(row=2, column=0, sticky="w")
        self.category_entry = ttk.Combobox(add_frame, values=self.categories, state="readonly")
        self.category_entry.set(self.categories[0])
        self.category_entry.grid(row=2, column=1, sticky="ew")
        ttk.Label(add_frame, text="New Category:").grid(row=3, column=0, sticky="w")
        self.new_cat_entry = ttk.Entry(add_frame)
        self.new_cat_entry.grid(row=3, column=1, sticky="ew")
        ttk.Button(add_frame, text="Add Category", command=self.add_category).grid(row=4, column=0, columnspan=2, pady=5)
        ttk.Button(add_frame, text="Add Expense", command=self.add_expense).grid(row=5, column=0, columnspan=2, pady=5)

        # Actions
        action_frame = ttk.LabelFrame(main_frame, text="📊 Actions", padding=10)
        action_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        action_frame.columnconfigure(0, weight=1)
        ttk.Button(action_frame, text="View All Expenses", command=self.view_expenses).grid(row=0, column=0, sticky="ew", pady=2)
        ttk.Button(action_frame, text="Summary by Category", command=self.view_summary).grid(row=1, column=0, sticky="ew", pady=2)
        ttk.Button(action_frame, text="Monthly Summary", command=self.view_monthly_summary).grid(row=2, column=0, sticky="ew", pady=2)
        ttk.Button(action_frame, text="Delete Last Expense", command=self.delete_last_expense).grid(row=3, column=0, sticky="ew", pady=2)
        ttk.Button(action_frame, text="Export CSV", command=self.export_csv).grid(row=4, column=0, sticky="ew", pady=2)
        ttk.Button(action_frame, text="Category Pie Chart", command=self.chart_category_pie).grid(row=5, column=0, sticky="ew", pady=2)
        ttk.Button(action_frame, text="Monthly Bar Chart", command=self.chart_monthly_bar).grid(row=6, column=0, sticky="ew", pady=2)

        # Display Text
        self.display_text = tk.Text(self, height=18, bg='#f0f6fb', font=('Consolas', 12))
        self.display_text.pack(fill="both", expand=True, padx=10, pady=5)

        # Chart
        self.chart_label = ttk.Label(self)
        self.chart_label.pack(pady=5)

    # ---------- Functional Methods ----------
    def logout(self):
        self.destroy()
        main(self.parent)

    def change_pin(self):
        old = simpledialog.askstring("Change PIN", "Current PIN:", show="*")
        if not old or not self.storage.check_pin(old):
            messagebox.showerror("Error", "Incorrect current PIN")
            return
        new = simpledialog.askstring("New PIN", "Enter new PIN:", show="*")
        confirm = simpledialog.askstring("Confirm PIN", "Confirm new PIN:", show="*")
        if not new or not confirm or new != confirm:
            messagebox.showerror("Error", "PINs do not match or empty")
            return
        if len(new) < 4:
            messagebox.showerror("Error", "PIN must be 4+ digits")
            return
        self.storage.save_pin(new)
        messagebox.showinfo("PIN", "PIN changed successfully")

    def add_category(self):
        cat = self.new_cat_entry.get().strip()
        if cat and cat not in self.categories:
            self.categories.append(cat)
            self.category_entry['values'] = self.categories
            self.category_entry.set(cat)
            self.storage.save_categories(self.categories)
            messagebox.showinfo("Category", f"Added '{cat}'")
        else:
            messagebox.showwarning("Category", "Invalid or duplicate category")
        self.new_cat_entry.delete(0, tk.END)

    def add_expense(self):
        desc = self.desc_entry.get().strip()
        amt = self.amount_entry.get().strip()
        cat = self.category_entry.get()
        if not desc or not amt or not cat:
            messagebox.showerror("Error", "All fields required")
            return
        try:
            amt = float(amt)
        except:
            messagebox.showerror("Error", "Invalid amount")
            return
        self.tracker.add_expense(desc, amt, cat)
        messagebox.showinfo("Success", "Expense added")
        self.desc_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.category_entry.set(self.categories[0])
        self.view_expenses()

    def view_expenses(self):
        self.display_text.delete(1.0, tk.END)
        for exp in self.tracker.get_expenses():
            self.display_text.insert(tk.END, f"{exp['date']} | {exp['description']:20} | {exp['category']:12} | ${exp['amount']:.2f}\n")

    def view_summary(self):
        summary = self.tracker.get_summary_by_category()
        self.display_text.delete(1.0, tk.END)
        self.display_text.insert(tk.END, "Category Summary:\n")
        for cat, amt in summary.items():
            self.display_text.insert(tk.END, f"{cat:12} | ${amt:.2f}\n")

    def view_monthly_summary(self):
        summary = self.tracker.get_monthly_summary()
        self.display_text.delete(1.0, tk.END)
        self.display_text.insert(tk.END, "Monthly Summary:\n")
        for month, amt in summary.items():
            self.display_text.insert(tk.END, f"{month} | ${amt:.2f}\n")

    def delete_last_expense(self):
        if self.tracker.delete_last_expense():
            messagebox.showinfo("Deleted", "Last expense removed")
            self.view_expenses()
        else:
            messagebox.showwarning("None", "No expense to delete")

    def export_csv(self):
        filename = os.path.join(self.storage.user_dir, f"expenses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "description", "amount", "category"])
            writer.writeheader()
            writer.writerows(self.tracker.get_expenses())
        messagebox.showinfo("CSV Exported", f"Saved to {filename}")

    def chart_category_pie(self):
        summary = self.tracker.get_summary_by_category()
        if not summary:
            messagebox.showwarning("No Data", "No expenses to chart")
            return
        fig, ax = plt.subplots()
        ax.pie(summary.values(), labels=summary.keys(), autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        self.show_chart(fig)

    def chart_monthly_bar(self):
        summary = self.tracker.get_monthly_summary()
        if not summary:
            messagebox.showwarning("No Data", "No expenses to chart")
            return
        months = list(summary.keys())
        amounts = list(summary.values())
        fig, ax = plt.subplots()
        ax.bar(months, amounts)
        ax.set_ylabel("Amount ($)")
        ax.set_title("Monthly Expenses")
        plt.xticks(rotation=45)
        self.show_chart(fig)

    def show_chart(self, fig):
        plt.tight_layout()
        chart_path = os.path.join(self.storage.user_dir, "temp_chart.png")
        fig.savefig(chart_path)
        plt.close(fig)
        img = Image.open(chart_path)
        img.thumbnail((500,300))
        self.chart_img = ImageTk.PhotoImage(img)
        self.chart_label.config(image=self.chart_img)

# ---------- Main ----------
def main(root=None):
    if root is None:
        root = tk.Tk()
        root.title("BudgetBase v1.0.0")
        root.geometry("900x700")
        setup_styles()
    # Show user selection screen
    def on_user_selected(user_id):
        login_frame = LoginScreen(root, user_id, on_login_success)
        login_frame.pack(fill="both", expand=True)
    def on_login_success(storage, user_id):
        ExpenseTrackerGUI(root, storage, user_id)
    UserSelectScreen(root, on_user_selected)
    root.mainloop()

if __name__ == "__main__":
    main()
