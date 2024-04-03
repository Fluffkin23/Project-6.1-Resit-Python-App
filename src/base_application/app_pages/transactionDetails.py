import tkinter as tk
from tkinter import ttk
from tkinter import *
import requests
from src.base_application import api_server_ip


def transaction_details(trans_id):
    # -------------------- Functions ----------------------
    def get_transaction_json():
        response = requests.get(api_server_ip + "/api/transactions/join" + str(trans_id))
        if len(response.json()) == 0:
            return
        return response.json()[0]

    trans = get_transaction_json()
    tuple_trans = (trans[0], trans[6], trans[2], trans[3], trans[1], trans[4], trans[5], trans[7], trans[14], trans[8], trans[11], trans[9])
    # ------------------------------------------------------
    # ----------------- Window TKinter ---------------------
    # Create a standard size window of 1200x900 pixels, not resizable
    window = tk.Tk()
    window.geometry("1200x400")
    window.resizable(False, False)
    window.title("Sports Accounting - Transaction Details")


    # Create a frame to hold the left section
    left_frame = tk.Frame(window, width=1200, height=900, bg="#D9D9D9")  # Set the background color to grey
    left_frame.pack(side="left")

    # -------------------------------------------------------
    # ----------------- Table -------------------------------
    table = ttk.Treeview(left_frame, columns=("ID", "Date", "Details", "Description", "Ref", "Amount", "Currency",
                                         "CategoryID", "Category", "MemberID", "Member", "Type"),
                         show="headings", style="Custom.Treeview")
    table.place(x=40, y=9000, width=1100, height=300)  # move down the table by 50 pixels


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

    # # Clear existing rows in the table
    table.delete(*table.get_children())

    # Insert retrieved data into the table
    table.insert("", "end", values=tuple_trans)

    # Pack the table into the frame and center it horizontally
    table.pack(fill="both", expand=False)  # Fill the frame with the table
    table.place(x=20, y=20)

    # -------------------------------------------------------------------------
    window.mainloop()
