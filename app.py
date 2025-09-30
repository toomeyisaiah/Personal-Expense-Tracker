import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import hashlib
import getpass
from datetime import datetime
import webbrowser

# ---------- Styling for the whole app ----------
def setup_styles():
    style = ttk.Style()
    style.theme_use("clam")  # Looks modern on all major platforms
    style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground="#0052cc", background="#e7f0fa")
    style.configure("SubHeader.TLabel", font=("Segoe UI", 10, "italic"), foreground="#333", background="#e7f0fa")
    style.configure("TLabel", font=("Segoe UI", 11), background="#fafafa")
    style.configure("TButton", font=("Segoe UI", 11), padding=(8,4))
    style.configure("TLabelframe", background="#f7faff", font=("Segoe UI", 12, "bold"))
    style.configure("TLabelframe.Label", font=("Segoe UI", 12, "bold"), foreground="#3466af", background="#f7faff")
    style.map("TButton",
              background=[('active', '#3466af'), ('!active', '#0052cc')],
              foreground=[('disabled', '#cccccc'), ('active', '#ffffff')])
# -----------------------------------------------

class SecureStorage:
    def __init__(self, user_id):
        self.base_dir = os.path.join(os.path.expanduser("~"), ".expense_tracker_data")
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
            if os.name != 'nt':
                os.chmod(self.base_dir, 0o700)
        self.user_dir = os.path.join(self.base_dir, user_id)
        if not os.path.exists(self.user_dir):
            os.makedirs(self.user_dir)
        self.pin_file = os.path.join(self.user_dir, "pin.hash")
        self.data_file = os.path.join(self.user_dir, "expenses.json")

    def save_pin(self, pin):
        hashed_pin = hashlib.sha256(pin.encode()).hexdigest()
        with open(self.pin_file, 'w') as f:
            f.write(hashed_pin)

    def check_pin(self, pin):
        hashed_pin = hashlib.sha256(pin.encode()).hexdigest()
        if os.path.exists(self.pin_file):
            with open(self.pin_file, 'r') as f:
                stored_pin = f.read()
            return hashed_pin == stored_pin
        return False

    def pin_exists(self):
        return os.path.exists(self.pin_file)

class ExpenseTracker:
    def __init__(self, storage):
        self.storage = storage
        self.expenses = []
        self.load_expenses()

    def load_expenses(self):
        if os.path.exists(self.storage.data_file):
            try:
                with open(self.storage.data_file, "r") as file:
                    self.expenses = json.load(file)
            except Exception as e:
                print(f"Error loading expenses: {e}")
                self.expenses = []

    def save_expenses(self):
        try:
            with open(self.storage.data_file, "w") as file:
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

class LoginScreen:
    def __init__(self, root, on_login_success):
        self.root = root
        self.root.title("BudgetBase - Login")
        self.on_login_success = on_login_success
        self.user_id = getpass.getuser()
        self.storage = SecureStorage(self.user_id)

        self.root.geometry("400x300")
        self.root.minsize(300, 200)

        self.setup_gui()

    def setup_gui(self):
        self.login_frame = ttk.Frame(self.root, padding=20)
        self.login_frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # HEADER
        header_bar = tk.Frame(self.login_frame, bg="#e7f0fa", height=52)
        header_bar.place(relx=0, rely=0, relwidth=1.0, relheight=0.23)
        ttk.Label(self.login_frame, text="💲 BudgetBase v1.0.0", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=(0,22), sticky="ew")

        if self.storage.pin_exists():
            ttk.Label(self.login_frame, text="Enter PIN:").grid(row=1, column=0, padx=9, pady=11, sticky="w")
            self.pin_entry = ttk.Entry(self.login_frame, show="*")
            self.pin_entry.grid(row=1, column=1, padx=9, pady=11, sticky="ew")
            ttk.Button(self.login_frame, text="Login", command=self.check_pin).grid(row=2, column=0, columnspan=2, pady=14)
        else:
            ttk.Label(self.login_frame, text="Set Up New PIN:").grid(row=1, column=0, padx=9, pady=11, sticky="w")
            self.pin_entry = ttk.Entry(self.login_frame, show="*")
            self.pin_entry.grid(row=1, column=1, padx=9, pady=11, sticky="ew")
            ttk.Label(self.login_frame, text="Confirm PIN:").grid(row=2, column=0, padx=9, pady=11, sticky="w")
            self.confirm_pin_entry = ttk.Entry(self.login_frame, show="*")
            self.confirm_pin_entry.grid(row=2, column=1, padx=9, pady=11, sticky="ew")
            ttk.Button(self.login_frame, text="Set PIN", command=self.set_pin).grid(row=3, column=0, columnspan=2, pady=17)
        self.login_frame.grid_columnconfigure(1, weight=1)

    def set_pin(self):
        pin = self.pin_entry.get()
        confirm_pin = getattr(self, 'confirm_pin_entry', None)
        confirm_pin = confirm_pin.get() if confirm_pin else ""
        if not pin or not confirm_pin:
            messagebox.showerror("Error", "PIN fields cannot be empty!")
            return
        if pin != confirm_pin:
            messagebox.showerror("Error", "PINs do not match!")
            return
        if len(pin) < 4:
            messagebox.showerror("Error", "PIN must be at least 4 characters!")
            return
        self.storage.save_pin(pin)
        messagebox.showinfo("Success", "PIN set successfully! Please log in.")
        self.login_frame.destroy()
        self.setup_gui()

    def check_pin(self):
        pin = self.pin_entry.get()
        if self.storage.check_pin(pin):
            self.login_frame.destroy()
            self.on_login_success(self.storage)
        else:
            messagebox.showerror("Error", "Invalid PIN!")

class ExpenseTrackerGUI:
    def __init__(self, root, storage):
        self.root = root
        self.root.title("BudgetBase v1.0.0")
        self.tracker = ExpenseTracker(storage)
        self.categories = ["Food", "Transport", "Utilities", "Entertainment", "Health", "Other"]

        # Sizing
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        initial_width = int(screen_width * 0.6)
        initial_height = int(screen_height * 0.6)
        self.root.geometry(f"{initial_width}x{initial_height}")
        self.root.minsize(700, 500)

        self.setup_gui()

    def setup_gui(self):
        # Configure grid
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=3)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # HEADER BAR
        header_frame = ttk.Frame(self.root, style="TFrame")
        header_frame.grid(row=0, column=0, columnspan=2, padx=0, pady=0, sticky="ew")
        header_frame.grid_columnconfigure(2, weight=1)
        header_bar = tk.Frame(header_frame, bg="#e7f0fa", height=50)
        header_bar.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)

        ttk.Label(header_frame, text="💲 BudgetBase", style="Header.TLabel", background="#e7f0fa").grid(row=0, column=0, padx=12, pady=8, sticky="w")
        ttk.Label(header_frame, text="Developed by Isaiah Toomey", style="SubHeader.TLabel", background="#e7f0fa").grid(row=0, column=1, padx=7, pady=8)
        github_link = ttk.Label(header_frame, text="GitHub", foreground="#0052cc", cursor="hand2", background="#e7f0fa", font=("Segoe UI", 10, "bold"))
        github_link.grid(row=0, column=2, padx=10, pady=8, sticky="e")
        github_link.bind("<Button-1>", lambda e: self.open_link("https://github.com/toomeyisaiah"))

        # Separator
        separator = ttk.Separator(self.root, orient="horizontal")
        separator.grid(row=1, column=0, columnspan=2, sticky="ew")

        # --- Add Expense ---
        add_frame = ttk.LabelFrame(self.root, text="📝 Add Expense", padding=18, style="TLabelframe")
        add_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
        add_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(add_frame, text="Description:", font=("Segoe UI", 11)).grid(row=0, column=0, padx=7, pady=7, sticky="w")
        self.desc_entry = ttk.Entry(add_frame, font=("Segoe UI", 11))
        self.desc_entry.grid(row=0, column=1, padx=7, pady=7, sticky="ew")

        ttk.Label(add_frame, text="Amount:", font=("Segoe UI", 11)).grid(row=1, column=0, padx=7, pady=7, sticky="w")
        self.amount_entry = ttk.Entry(add_frame, font=("Segoe UI", 11))
        self.amount_entry.grid(row=1, column=1, padx=7, pady=7, sticky="ew")

        ttk.Label(add_frame, text="Category:", font=("Segoe UI", 11)).grid(row=2, column=0, padx=7, pady=7, sticky="w")

        self.category_entry = ttk.Combobox(add_frame, values=self.categories, state="readonly", font=("Segoe UI", 11))
        self.category_entry.set(self.categories[0])
        self.category_entry.grid(row=2, column=1, padx=7, pady=7, sticky="ew")

        ttk.Button(add_frame, text="Add Expense", command=self.add_expense).grid(row=3, column=0, columnspan=2, pady=12)
        
        # --- Actions ---
        view_frame = ttk.LabelFrame(self.root, text="📊 Actions", padding=18, style="TLabelframe")
        view_frame.grid(row=2, column=1, padx=20, pady=20, sticky="nsew")
        view_frame.grid_columnconfigure(0, weight=1)

        ttk.Button(view_frame, text="View All Expenses", command=self.view_expenses).grid(row=0, column=0, pady=7, sticky="ew")
        ttk.Button(view_frame, text="View Summary by Category", command=self.view_summary).grid(row=1, column=0, pady=7, sticky="ew")

        # --- Output Display ---
        text_frame = ttk.Frame(self.root)
        text_frame.grid(row=3, column=0, columnspan=2, padx=18, pady=10, sticky="nsew")
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(text_frame, orient="vertical")
        scrollbar.grid(row=0, column=1, sticky="ns")
        horizontal_scrollbar = ttk.Scrollbar(text_frame, orient="horizontal")
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

        self.display_text = tk.Text(
            text_frame, height=18, width=60,
            yscrollcommand=scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
            wrap="word",
            bg='#f0f6fb', fg='#222', font=('Consolas', 12), relief="flat", borderwidth=5
        )
        self.display_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.config(command=self.display_text.yview)
        horizontal_scrollbar.config(command=self.display_text.xview)

    def open_link(self, url):
        webbrowser.open_new(url)

    def add_expense(self):
        desc = self.desc_entry.get().strip()
        amount = self.amount_entry.get().strip()
        category = self.category_entry.get()
        if not desc or not amount or not category:
            messagebox.showerror("Input Error", "All fields are required!")
            return
        try:
            amount = float(amount)
            self.tracker.add_expense(desc, amount, category)
            messagebox.showinfo("Success", "Expense added successfully!")
            self.desc_entry.delete(0, tk.END)
            self.amount_entry.delete(0, tk.END)
            self.category_entry.set(self.categories[0])
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def view_expenses(self):
        self.display_text.config(state="normal")
        self.display_text.delete(1.0, tk.END)
        expenses = self.tracker.get_expenses()
        if not expenses:
            self.display_text.insert(tk.END, "No expenses recorded.\n")
        else:
            self.display_text.insert(tk.END, "All Expenses:\n")
            self.display_text.insert(tk.END, "-" * 50 + "\n")
            for exp in expenses:
                self.display_text.insert(tk.END, f"📅 Date: {exp['date']}\n")
                self.display_text.insert(tk.END, f"📝 Description: {exp['description']}\n")
                self.display_text.insert(tk.END, f"💲 Amount: ${exp['amount']:.2f}\n")
                self.display_text.insert(tk.END, f"🏷️ Category: {exp['category']}\n")
                self.display_text.insert(tk.END, "-" * 50 + "\n")
        self.display_text.config(state="normal")

    def view_summary(self):
        self.display_text.config(state="normal")
        self.display_text.delete(1.0, tk.END)
        summary = self.tracker.get_summary_by_category()
        if not summary:
            self.display_text.insert(tk.END, "No expenses recorded.\n")
        else:
            self.display_text.insert(tk.END, "Summary by Category:\n")
            self.display_text.insert(tk.END, "-" * 50 + "\n")
            for category, total in summary.items():
                self.display_text.insert(tk.END, f"🏷️ Category: {category}\n")
                self.display_text.insert(tk.END, f"💲 Total Spent: ${total:.2f}\n")
                self.display_text.insert(tk.END, "-" * 50 + "\n")
        self.display_text.config(state="normal")

if __name__ == "__main__":
    setup_styles()
    root = tk.Tk()
    def start_main_app(storage):
        root.geometry("")  # Allow window resize for main app
        app = ExpenseTrackerGUI(root, storage)
    login_screen = LoginScreen(root, start_main_app)
    root.mainloop()