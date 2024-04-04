import tkinter as tk
from tkinter import ttk
import requests
from src.base_application.member.member_registration_gui import member_registration
from src.base_application import api_server_ip


def manage_members():
    selected_row = None
    # Create the main window
    root = tk.Tk()
    root.title("Manage members")
    root.geometry("1200x900")

    # connect to the database
    def retrieveDB():
        response = requests.get(api_server_ip + "/api/members")
        if len(response.json()) == 0:
            return

        # Convert JSON object into an array of tuples
        rows_out = []
        for entry in response.json():
            rows_out.append(tuple(entry))

        return rows_out

    def back_button_click():
        root.destroy()
        from src.base_application.admin.adminPanel import adminPanel
        adminPanel()

    def add_member_button_click():
        root.destroy()
        member_registration()

    # Define a function to be called when a row of the table is clicked
    def on_click_table_row(event):
        global selected_row
        # Get the selected item
        item = table.selection()[0]
        # Get the values of the selected item
        values = table.item(item, "values")
        selected_row = values[0]

    # Create a frame to hold the left section
    left_frame = tk.Frame(root, bg="#D9D9D9")  # Set the background color to grey
    left_frame.pack(side="left", fill="both", expand=True)

    # Create a frame to hold the right section
    right_frame = tk.Frame(root, bg="#F0AFAF")  # Set the background color to pink
    right_frame.pack(side="right", fill="both", expand=True, padx=(0, 5))  # Add padding to prevent overlap

    # Headings

    heading3 = tk.Label(left_frame, text="Manage members", font=("Roboto", 24), bg="#D9D9D9", fg="#000000",
                        justify="center")
    heading3.place(x=25, y=180, width=500, height=50)

    # -----------------------------TABLE-----------------------------------------
    table = ttk.Treeview(left_frame, columns=("Member ID", "Name", "Email", "Delete"), show="headings",
                         style="Custom.Treeview")
    table.heading("Member ID", text="Member ID")
    table.heading("Name", text="Name")
    table.heading("Email", text="Email")
    table.heading("Delete", text="Delete")

    for column in table["columns"]:
        # Assigning the heading as text of the column
        table.heading(column, text=column, command=lambda: None)
        # table.bind("<Button-1>", lambda event: "break")

    rows = retrieveDB()
    # # Clear existing rows in the table
    table.delete(*table.get_children())

    # Insert retrieved data into the table
    for row in rows:
        table.insert("", "end", values=row)

    style = ttk.Style()
    style.configure("Custom.Treeview", background="#D9D9D9")

    table.column("Member ID", width=80)
    table.column("Name", width=160)
    table.column("Email", width=160)
    table.column("Delete", width=160)

    table.config(height=8)

    table.pack(fill="both", expand=False)
    table.place(x=16, y=280)

    table.column("Delete", width=100, anchor="w")
    table.heading("Delete", text="Delete", command=lambda: None)
    table.bind("<ButtonRelease-1>", on_click_table_row, "+")

    def delete_button_click(table, member_count):
        global selected_row
        if selected_row is None:
            return
        data_params = {'memberid': str(selected_row)}
        # Update DB
        response = requests.delete(api_server_ip + "/api/members", params=data_params)
        print(response.text)
        rows = retrieveDB()
        table.delete(*table.get_children())
        member_count.config(text=str(len(rows)))
        for row in rows:
            table.insert("", "end", values=row)
    # -------------------------------------------------------------
    left_frame.pack_propagate(False)

    num_of_members = len(rows)

    # Right side
    heading4 = tk.Label(right_frame, text="Overview", font=("Roboto", 24), bg="#F0AFAF", fg="#000000", justify="center")
    heading4.place(x=220, y=80, width=200, height=50)

    heading5 = tk.Label(right_frame, text="All members", font=("Roboto", 14), bg="#F0AFAF", fg="#000000",
                        justify="center")
    heading5.place(x=220, y=200, width=200, height=50)

    member_count = tk.Label(right_frame, text=num_of_members, font=("Roboto", 14), bg="#F0AFAF", fg="#000000",
                        justify="center")
    member_count.place(x=220, y=260, width=200, height=50)
    # Buttons

    back_button = ttk.Button(left_frame, text="Back", command=lambda: back_button_click())
    back_button.place(x=30, y=850, width=100, height=30)

    add_member_button = ttk.Button(left_frame, text="Add member", command=lambda: add_member_button_click())
    add_member_button.place(x=140, y=550, width=300, height=80)

    delete_button = ttk.Button(left_frame, text="Delete", command=lambda: delete_button_click(table, member_count))
    delete_button.place(x=450, y=850, width=100, height=30)

    # Start the main event loop
    root.lift()  # Lift the window to the top after mainloop()
    root.mainloop()
