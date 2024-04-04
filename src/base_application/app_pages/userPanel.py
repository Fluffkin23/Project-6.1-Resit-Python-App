import tkinter as tk
from tkinter import ttk
import requests
import json
from src.base_application.admin.adminLogin import login_admin_page
from src.base_application import api_server_ip


def create_window():
    selected_row = None

    def destroy_window():
        if 'root' in globals() and root is not None:
            root.destroy()

    # Create the main window
    root = tk.Tk()
    root.title("Sports Accounting - User Panel")

    # Calculate the window size
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    width = int(0.8 * screen_width)
    height = int(0.8 * screen_height)

    # Calculate the coordinates to place the window in the center of the screen
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    root.geometry(f"{width}x{height}+{x}+{y}")  # Set the geometry with the calculated coordinates

    # Get balance from db
    balance = "No data"
    response = requests.get(api_server_ip + "/api/files")
    try:
        data = response.json()
        if len(data) != 0:
            balance = data[0][4]
    except json.decoder.JSONDecodeError:
        balance = "No data"

    def admin_login_button_click():
        root.destroy()
        login_admin_page()

    def logout_button_click():
        if root:
            root.destroy()

    def on_click_table_row(event):
        global selected_row
        item = table.selection()[0]
        values = table.item(item, "values")
        selected_row = values[0]

    def edit_button_click():
        global selected_row
        if selected_row is None:
            return
        root.destroy()
        from editTransaction import edit_transaction_page
        edit_transaction_page(selected_row)

    def details_button_click():
        global selected_row
        if selected_row is None:
            return
        from src.base_application.app_pages.transactionDetails import transaction_details
        transaction_details(selected_row)

    root.resizable(False, False)

    left_frame = tk.Frame(root, width=width / 2, height=height, bg="#D9D9D9")
    left_frame.pack(side="left", fill="both", expand=True)

    right_frame = tk.Frame(root, width=width / 2, height=height, bg="#F0AFAF")
    right_frame.pack(side="right", fill="both", expand=True)

    def create_logout_button(frame):
        logout_button_style = ttk.Style()
        logout_button_style.configure('Logout.TButton',
                                      font=('Inter', 12, 'bold'),
                                      foreground='black',
                                      background='red',
                                      borderwidth=1,
                                      relief='raised')
        logout_button_style.map('Logout.TButton',
                                background=[('active', 'darkred')],
                                foreground=[('active', 'black')])

        logout_button = ttk.Button(frame,
                                   text="Logout",
                                   style='Logout.TButton',
                                   command=logout_button_click)

        logout_button.place(relx=0.9, rely=0.01, anchor='ne', width=100, height=40)

    create_logout_button(left_frame)

    label = tk.Label(left_frame, text="User Panel", font=("Inter", 24, "normal"), bg="#D9D9D9", fg="#000000",
                     justify="left")
    label.place(x=20, y=20, width=190, height=50)

    label = tk.Label(left_frame, text="Welcome", font=("Inter", 18, "bold"), bg="#D9D9D9", fg="#000000", justify="left",
                     underline=len("Welcome"))
    label.place(x=30, y=200, width=190, height=50)

    entry = tk.Entry(left_frame, font=("Inter", 14))
    entry.place(x=70, y=300, width=280, height=24)

    style = ttk.Style()
    style.configure("RoundedButton.TButton", padding=6, relief="flat",
                    background="#000000", foreground="#FFFFFF",
                    font=("Inter", 14), borderwidth=0, bordercolor="#000000")
    style.map("RoundedButton.TButton", background=[("active", "#333333")])

    style = ttk.Style()
    style.configure("RoundedButton.TButton", padding=6, relief="flat",
                    background="#000000", foreground="#FFFFFF",
                    font=("Inter", 14), borderwidth=0, bordercolor="#000000")
    style.map("RoundedButton.TButton", background=[("active", "#333333")])

    button2 = ttk.Button(left_frame, text="Admin Login", command=admin_login_button_click)
    button2.place(x=250, y=400, width=150, height=24)

    balance_label = tk.Label(left_frame, text="Available Balance:", font=("Inter", 15), bg="#D9D9D9", fg="#000000",
                             justify="left")
    balance_label.place(x=70, y=500, width=160, height=24)

    balance_number = tk.Label(left_frame, text=balance, font=("Inter", 15), bg="#D9D9D9", fg="#000000", justify="left")
    balance_number.place(x=250, y=500, width=160, height=24)

    search_balance_label = tk.Label(left_frame, text="Sum of found transactions:", font=("Inter", 15), bg="#D9D9D9",
                                    fg="#000000", justify="left")
    search_balance_label.place(x=70, y=600, width=240, height=24)

    search_summary_num = tk.Label(left_frame, text="", font=("Inter", 15), bg="#D9D9D9", fg="#000000", justify="left")
    search_summary_num.pack_forget()

    table = ttk.Treeview(right_frame, columns=("ID", "Date", "Details", "Description", "Ref", "Amount"),
                         show="headings", style="Custom.Treeview")
    table.heading("ID", text="ID")
    table.heading("Date", text="Date")
    table.heading("Details", text="Company Name")
    table.heading("Description", text="Description")
    table.heading("Ref", text="Ref")
    table.heading("Amount", text="Amount")

    for column in table["columns"]:
        table.heading(column, text=column, command=lambda: None)

    table.column("ID", width=20)
    table.column("Date", width=100)
    table.column("Details", width=200)
    table.column("Description", width=100)
    table.column("Ref", width=50)
    table.column("Amount", width=100)
    table.config(height=20)

    rows = retrieveDB()

    table.delete(*table.get_children())

    if rows is not None:
        for row in rows:
            table.insert("", "end", values=row)

    table.pack(fill="both", expand=False)
    table.place(x=15, y=100)
    table.bind("<ButtonRelease-1>", on_click_table_row, "+")
    right_frame.pack_propagate(False)

    edit_button = ttk.Button(right_frame, text="Edit", command=lambda: edit_button_click())
    edit_button.place(x=15, y=35, width=100, height=30)

    details_button = ttk.Button(right_frame, text="Details", command=lambda: details_button_click())
    details_button.place(x=485, y=35, width=100, height=30)

    button1 = ttk.Button(left_frame, text="Keyboard Search", command=lambda: keyword_search_button(entry.get(), table, search_summary_num))
    button1.place(x=70, y=400, width=150, height=24)

    def on_closing():
        root.destroy()

    def keyword_search_button(keyword, table, widget):
        table.delete(*table.get_children())
        if len(keyword) == 0:
            keyword_table = retrieveDB()
            widget.config(text="")
        else:
            keyword_table = retrieveDB_keyword_search(keyword)
            sum_output = 0
            for tuple_entry in keyword_table:
                sum_output = sum_output + float(tuple_entry[5])
            widget.config(text=str(sum_output))
            widget.place(x=310, y=600, width=350, height=24)

        for result in keyword_table:
            table.insert("", "end", values=result)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.lift()  # Lift the window to the top after mainloop()

    root.mainloop()

def retrieveDB():
    response = requests.get(api_server_ip + "/api/transactions/sql")
    if len(response.json()) == 0:
        return []

    rows_out = []
    for entry in response.json():
        if isinstance(entry, list) and len(entry) >= 7:
            temp_tuple = (entry[0], entry[6], entry[2], entry[3], entry[1], entry[4])
            rows_out.append(tuple(temp_tuple))

    return rows_out

def retrieveDB_keyword_search(keyword):
    response = requests.get(api_server_ip + "/api/transactions/search/" + str(keyword))
    if len(response.json()) == 0:
        return

    rows_out = []
    for entry in response.json():
        temp_tuple = (entry[0], entry[6], entry[2], entry[3], entry[1], entry[4])
        rows_out.append(tuple(temp_tuple))

    return rows_out
