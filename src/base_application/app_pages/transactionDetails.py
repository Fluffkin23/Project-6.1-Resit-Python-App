import tkinter as tk
from tkinter import ttk
from tkinter import *
import json
import requests
from src.base_application import api_server_ip


def transaction_details(trans_id):
    # -------------------- Functions ----------------------
    def get_transaction_json(trans_id):
        response = requests.get(api_server_ip + "/api/transactions/join/" + str(trans_id))

        # Check if the response status code indicates success (2xx)
        if response.status_code == 200:
            try:
                # Try to decode the JSON response
                json_data = response.json()
                if len(json_data) > 0:
                    return json_data[0]
                else:
                    # Handle case where response is empty
                    print("Error: Empty response from the API")
                    return None
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
                # Handle case where JSON decoding fails
                return None
        else:
            # Handle case where the request was not successful
            print("Error:", response.status_code)
            return None

    trans = get_transaction_json(trans_id)

    if trans:
        tuple_trans = (trans[0], trans[6], trans[2], trans[3], trans[1], trans[4], trans[5], trans[7], trans[14], trans[8], trans[11], trans[9])

        # Create the Tkinter window and table
        window = tk.Tk()
        window.geometry("1200x400")
        window.resizable(False, False)
        window.title("Sports Accounting - Transaction Details")

        left_frame = tk.Frame(window, width=1200, height=900, bg="#D9D9D9")
        left_frame.pack(side="left")

        table = ttk.Treeview(left_frame, columns=("ID", "Date", "Details", "Description", "Ref", "Amount", "Currency",
                                                  "CategoryID", "Category", "MemberID", "Member", "Type"),
                             show="headings", style="Custom.Treeview")
        table.place(x=40, y=9000, width=1100, height=300)

        # Add headings and columns...
        table.heading("ID", text="ID")
        table.heading("Date", text="Date")
        table.heading("Details", text="Company Name")
        table.heading("Description", text="Description")
        table.heading("Ref", text="Ref")
        table.heading("Amount", text="Amount")
        table.heading("CategoryID", text="CategoryID")
        table.heading("Category", text="Category")
        table.heading("MemberID", text="MemberID")
        table.heading("Member", text="Member")
        table.heading("Type", text="Type")
        table.heading("Currency", text="Currency")

        # Looping through the columns and get the heading
        for column in table["columns"]:
            # Assigning the heading as text of the column
            table.heading(column, text=column, command=lambda: None)

        table.column("ID", width=20)
        table.column("Date", width=70)
        table.column("Details", width=300)
        table.column("Description", width=240)
        table.column("Ref", width=120)
        table.column("Amount", width=50)
        table.column("CategoryID", width=50)
        table.column("Category", width=70)
        table.column("MemberID", width=50)
        table.column("Member", width=70)
        table.column("Type", width=55)
        table.column("Currency", width=55)

        table.config(height=2)

        # Apply the background color to the entire table
        style = ttk.Style()
        style.configure("Custom.Treeview", background="#F0AFAF", rowheight=180)

        # Clear existing rows in the table
        table.delete(*table.get_children())

        # Insert retrieved data into the table
        table.insert("", "end", values=tuple_trans)

        # Pack the table into the frame and center it horizontally
        table.pack(fill="both", expand=False)
        table.place(x=20, y=20)

        window.mainloop()
    else:
        print("Error: Failed to retrieve transaction data from the API")
