import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
def is_valid_input(amount, currency, transaction_date, description):
    # Ensure no field is empty and amount is numeric
    if not all([amount, currency, transaction_date, description]):
        return False, "All fields are required."

    try:
        float(amount)
    except ValueError:
        return False, "Amount must be numeric."

    # Additional validation can be added here as necessary
    return True, ""

def open_add_cash_transaction_window():
    add_window = tk.Toplevel()
    add_window.geometry("600x400")
    add_window.resizable(False, False)
    add_window.configure(bg='#F0AFAF')

    frame = tk.Frame(add_window, bg="#D9D9D9")
    frame.pack(padx=20, pady=20, expand=True, fill="both")

    # Amount Entry
    tk.Label(frame, text="Amount:", bg="#D9D9D9").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    amount_entry = tk.Entry(frame, width=40)
    amount_entry.grid(row=0, column=1, padx=10, pady=10, sticky="e")

    # Currency Entry
    tk.Label(frame, text="Currency:", bg="#D9D9D9").grid(row=1, column=0, padx=10, pady=10, sticky="w")
    currency_entry = tk.Entry(frame, width=40)
    currency_entry.grid(row=1, column=1, padx=10, pady=10, sticky="e")

    # Transaction Date Entry
    tk.Label(frame, text="Transaction Date (YYYY-MM-DD):", bg="#D9D9D9").grid(row=2, column=0, padx=10, pady=10, sticky="w")
    date_entry = tk.Entry(frame, width=40)
    date_entry.grid(row=2, column=1, padx=10, pady=10, sticky="e")

    tk.Label(frame, text="Description:", bg="#D9D9D9").grid(row=3, column=0, padx=10, pady=10, sticky="w")
    description_entry = tk.Entry(frame, width=40)
    description_entry.grid(row=3, column=1, padx=10, pady=10, sticky="e")

    # Save Transaction Function
    def save_transaction():
        # Validate input
        amount = amount_entry.get()
        currency = currency_entry.get()
        transaction_date = date_entry.get()
        description = description_entry.get()


        is_valid, message = is_valid_input(amount, currency, transaction_date, description)
        if not is_valid:
            messagebox.showerror("Validation Error", message)
            return

        # This account_id should be dynamically obtained rather than hard-coded
        account_id = "NL65RABO0224663562EUR"  # Replace with the actual account ID logic

        # Connect to the database
        conn = None
        try:
            conn = psycopg2.connect(
                database="Quintor",
                user='postgres',
                password='12345',
                host='localhost',
                port='5432'
            )
            cursor = conn.cursor()

            # SQL to find the latest reference number for the account
            fetch_latest_reference_sql = """
                SELECT referenceNumber FROM File
                WHERE accountID = %s
                ORDER BY statementNumber DESC
                LIMIT 1;
            """
            cursor.execute(fetch_latest_reference_sql, (account_id,))
            fetch_result = cursor.fetchone()

            # Check if a reference number is found
            if fetch_result is None:
                messagebox.showerror("Error", "No reference number found for the account.")
                return

            latest_reference = fetch_result[0]

            # Insert SQL command for the Transactions table
            insert_transaction_sql = """
                           INSERT INTO transactions (amount, currency, transaction_date, description, referenceNumber)
                           VALUES (%s, %s, %s, %s, %s);
                       """
            cursor.execute(insert_transaction_sql, (amount, currency, transaction_date, description, latest_reference))

            # Update SQL command for the File table balance
            update_balance_sql = """
                UPDATE File
                SET forwardavbalance = forwardavbalance - %s
                WHERE referenceNumber = %s;
            """
            cursor.execute(update_balance_sql, (amount, latest_reference))

            # Commit the transaction
            conn.commit()
            messagebox.showinfo("Success", "Transaction saved and balance updated successfully!")
            add_window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save transaction and update balance: {e}")
            if conn is not None:
                conn.rollback()

        finally:
            if conn is not None:
                cursor.close()
                conn.close()

    # Submit Button
    submit_btn = tk.Button(frame, text="Save", bg="#D9D9D9", command=save_transaction)
    submit_btn.grid(row=4, column=0, columnspan=2, pady=20)

    # Adjust grid column configuration for alignment
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=3)