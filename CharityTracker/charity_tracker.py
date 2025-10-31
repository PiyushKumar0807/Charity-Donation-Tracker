import json
import os
from datetime import datetime
import pytz
import tkinter as tk
from tkinter import ttk, messagebox

# ---------------- PATH SETUP ---------------- #
BASE_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"
DONORS_FILE = BASE_PATH + 'donors.json'
DONATIONS_FILE = BASE_PATH + 'donations.json'
RECEIPTS_FOLDER = BASE_PATH + 'receipts/'

if not os.path.exists(RECEIPTS_FOLDER):
    os.makedirs(RECEIPTS_FOLDER)

# ---------------- DATA HANDLING ---------------- #
def load_data(file):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_data(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# ---------------- LOGIC FUNCTIONS ---------------- #
def add_donor_logic(name, contact):
    donors = load_data(DONORS_FILE)
    if not name or not contact:
        messagebox.showwarning("Input Error", "Both name and contact are required!")
        return
    if any(d['name'].strip().lower() == name.lower() for d in donors):
        messagebox.showwarning("Duplicate", f"Donor '{name}' already exists!")
        return
    donors.append({"name": name.strip(), "contact": contact.strip()})
    save_data(DONORS_FILE, donors)
    messagebox.showinfo("Success", f"✅ Donor '{name}' added successfully!")

def record_donation_logic(name, amount):
    donors = load_data(DONORS_FILE)
    donations = load_data(DONATIONS_FILE)

    donor = next((d for d in donors if d['name'].strip().lower() == name.lower()), None)
    if not donor:
        messagebox.showwarning("Not Found", "⚠ Donor not found. Please add them first.")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showwarning("Invalid Input", "Enter a valid amount.")
        return

    india_tz = pytz.timezone('Asia/Kolkata')
    date = datetime.now(india_tz).strftime("%Y-%m-%d %H:%M:%S %Z")

    donation = {"name": name, "amount": amount, "date": date}
    donations.append(donation)
    save_data(DONATIONS_FILE, donations)

    receipt_file = RECEIPTS_FOLDER + f"receipt_{name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
    with open(receipt_file, 'w', encoding='utf-8') as f:
        f.write(f"""
=== Charity Donation Receipt ===
Donor Name : {name}
Amount     : ₹{amount}
Date       : {date}
-------------------------------
Thank you for your generous donation!
""")

    messagebox.showinfo("Donation Recorded", f"💰 ₹{amount} recorded for {name}\n🧾 Receipt saved:\n{receipt_file}")

def get_donor_summary():
    donors = load_data(DONORS_FILE)
    donations = load_data(DONATIONS_FILE)
    data = []
    for donor in donors:
        total = sum(d['amount'] for d in donations if d['name'].strip().lower() == donor['name'].strip().lower())
        data.append((donor['name'], donor['contact'], f"₹{total:.2f}"))
    return data

def generate_report_logic():
    donations = load_data(DONATIONS_FILE)
    if not donations:
        messagebox.showinfo("No Data", "⚠ No donations available.")
        return
    total = sum(d['amount'] for d in donations)
    avg = total / len(donations)
    top = max(donations, key=lambda d: d['amount'])
    messagebox.showinfo("Donation Report",
                        f"📊 Total Donations: ₹{total:.2f}\n"
                        f"Average Donation: ₹{avg:.2f}\n"
                        f"Top Donor: {top['name']} (₹{top['amount']})")

def delete_specific_donor_logic(name):
    donors = load_data(DONORS_FILE)
    donations = load_data(DONATIONS_FILE)

    if not name:
        messagebox.showwarning("Input Error", "Please enter a donor name!")
        return

    if not any(d['name'].strip().lower() == name.lower() for d in donors):
        messagebox.showwarning("Not Found", f"No donor found with name '{name}'.")
        return

    confirm = messagebox.askyesno("Confirm", f"Delete donor '{name}' and their donations?")
    if confirm:
        donors = [d for d in donors if d['name'].strip().lower() != name.lower()]
        donations = [d for d in donations if d['name'].strip().lower() != name.lower()]
        save_data(DONORS_FILE, donors)
        save_data(DONATIONS_FILE, donations)
        messagebox.showinfo("Deleted", f"🗑 Donor '{name}' and their donations deleted successfully!")

def delete_all_data_logic():
    confirm = messagebox.askyesno("Confirm", "⚠ Delete ALL donors and donations?")
    if confirm:
        if os.path.exists(DONORS_FILE):
            os.remove(DONORS_FILE)
        if os.path.exists(DONATIONS_FILE):
            os.remove(DONATIONS_FILE)
        messagebox.showinfo("Deleted", "🧹 All data deleted successfully!")

# ---------------- UI DESIGN ---------------- #
root = tk.Tk()
root.title("💖 Charity Donation Tracker")
root.geometry("700x550")
root.configure(bg="#f8f9fa")
root.resizable(False, False)

style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook.Tab", padding=[15, 8], font=("Arial", 10, "bold"))
style.configure("TButton", font=("Arial", 10, "bold"), foreground="#fff", background="#0078D7")
style.map("TButton", background=[("active", "#005A9E")])

title_label = tk.Label(root, text="💖 Charity Donation Tracker 💖",
                       font=("Helvetica", 16, "bold"), bg="#0078D7", fg="white", pady=10)
title_label.pack(fill='x')

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=15, pady=15)

# ----- TAB: Add Donor ----- #
tab_add = ttk.Frame(notebook, padding=20)
notebook.add(tab_add, text="➕ Add Donor")

tk.Label(tab_add, text="Donor Name:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
entry_name = tk.Entry(tab_add, width=35, font=("Arial", 10))
entry_name.grid(row=0, column=1, pady=5)

tk.Label(tab_add, text="Contact:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
entry_contact = tk.Entry(tab_add, width=35, font=("Arial", 10))
entry_contact.grid(row=1, column=1, pady=5)

tk.Button(tab_add, text="Add Donor", width=25,
          command=lambda: add_donor_logic(entry_name.get(), entry_contact.get())).grid(row=2, column=0, columnspan=2, pady=15)

# ----- TAB: Record Donation ----- #
tab_donate = ttk.Frame(notebook, padding=20)
notebook.add(tab_donate, text="💰 Record Donation")

tk.Label(tab_donate, text="Donor Name:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
entry_dname = tk.Entry(tab_donate, width=35, font=("Arial", 10))
entry_dname.grid(row=0, column=1, pady=5)

tk.Label(tab_donate, text="Amount (₹):", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
entry_amount = tk.Entry(tab_donate, width=35, font=("Arial", 10))
entry_amount.grid(row=1, column=1, pady=5)

tk.Button(tab_donate, text="Record Donation", width=25,
          command=lambda: record_donation_logic(entry_dname.get(), entry_amount.get())).grid(row=2, column=0, columnspan=2, pady=15)

# ----- TAB: View Donors ----- #
tab_view = ttk.Frame(notebook, padding=20)
notebook.add(tab_view, text="📋 View Donors")

tree = ttk.Treeview(tab_view, columns=("Name", "Contact", "Total Donated"), show="headings", height=12)
for col in ("Name", "Contact", "Total Donated"):
    tree.heading(col, text=col)
    tree.column(col, width=200)
tree.pack(pady=10, fill='x')

def refresh_donor_list():
    for i in tree.get_children():
        tree.delete(i)
    for row in get_donor_summary():
        tree.insert("", tk.END, values=row)

tk.Button(tab_view, text="🔄 Refresh List", width=20, command=refresh_donor_list).pack(pady=10)

# ----- TAB: Reports / Settings ----- #
tab_report = ttk.Frame(notebook, padding=20)
notebook.add(tab_report, text="📊 Reports / Settings")

tk.Button(tab_report, text="📈 Generate Report", width=30, command=generate_report_logic).pack(pady=10)
tk.Button(tab_report, text="🧹 Delete All Data", width=30, command=delete_all_data_logic).pack(pady=10)

tk.Label(tab_report, text="Delete Specific Donor:", font=("Arial", 10, "bold")).pack(pady=(20, 5))
entry_del_name = tk.Entry(tab_report, width=35, font=("Arial", 10))
entry_del_name.pack(pady=5)
tk.Button(tab_report, text="🗑 Delete Donor", width=30,
          command=lambda: delete_specific_donor_logic(entry_del_name.get())).pack(pady=10)

tk.Label(tab_report, text="⚠ Deleting data will reset the tracker.", fg="red", font=("Arial", 9, "italic")).pack(pady=5)

root.mainloop()
