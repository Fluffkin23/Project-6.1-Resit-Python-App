# split_page.py

import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import messagebox


def create_split_entries(split_amounts_frame, number_of_splits):
    # Clear the frame for any existing widgets
    for widget in split_amounts_frame.winfo_children():
        widget.destroy()

    try:
        # Create a label and entry for each split
        for i in range(int(number_of_splits)):
            tk.Label(split_amounts_frame, text=f"Amount for split {i + 1}:").pack()
            entry = tk.Entry(split_amounts_frame)
            entry.pack()
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number for the splits.")


def confirm_splits(split_amounts_frame):
    split_amounts = []
    for entry_widget in split_amounts_frame.winfo_children():
        if isinstance(entry_widget, tk.Entry):
            split_amount = entry_widget.get()
            # Validate split_amount as needed
            split_amounts.append(split_amount)
    # Now you have a list of split amounts to process
    # Add your logic to process (save) the split amounts here
    print("Split amounts:", split_amounts)
    # Close the split window after processing
    split_amounts_frame.master.destroy()


def create_split_page(transaction_id, transaction_details):
    split_window = tk.Toplevel()
    split_window.title("Split Transaction")

    # ... other setup ...

    # Define the order of your columns based on the provided structure
    columns = ("id", "ref", "details", "description", "amount")
    tree = ttk.Treeview(split_window, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col.capitalize())
        # Adjust the width of the columns as needed
        tree.column(col, anchor='center', width=100, minwidth=100, stretch=False)

    # Clear any previous data in the Treeview
    tree.delete(*tree.get_children())

    # Insert the transaction details into the Treeview
    # Ensure transaction_details is a tuple with the data in the order of columns
    tree.insert('', 'end', values=transaction_details)
    tree.grid(row=1, column=0, columnspan=len(columns), sticky='ew', padx=5, pady=5)

    # Create and place the scrollbar
    scrollbar = ttk.Scrollbar(split_window, orient='horizontal', command=tree.xview)
    scrollbar.grid(row=2, column=0, columnspan=len(columns), sticky='ew')
    tree.configure(xscrollcommand=scrollbar.set)

    # Entry for number of ways to split
    tk.Label(split_window, text="How Many People to Split?").grid(row=3, column=0, sticky="e")
    num_splits_entry = tk.Entry(split_window)
    num_splits_entry.grid(row=3, column=1, sticky='w')

    # Button to confirm the splits and display the results
    confirm_button = tk.Button(split_window, text="Confirm Splits",
                               command=lambda: confirm_splits(num_splits_entry.get(), transaction_details))
    confirm_button.grid(row=3, column=2, sticky='w', padx=5)




def confirm_splits(num_splits, transaction_details):
    try:
        num_splits = int(num_splits)
        # Ensure you're referencing the correct index for the amount
        # Replace '4' with the correct index if amount is not the fifth item in your details
        amount = float(transaction_details[4])
        split_amounts = [round(amount / num_splits, 2) for _ in range(num_splits)]
        messagebox.showinfo("Split Amounts", f"Each part should be: {' , '.join(map(str, split_amounts))}")
    except ValueError as e:
        messagebox.showerror("Error", f"Invalid number or amount: {e}")
    except ZeroDivisionError:
        messagebox.showerror("Error", "Number of ways to split cannot be zero")





