# ----------------------------------------------------- Imports ------------------------------------------------------ #
import json
import xml.dom.minidom
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from tkcalendar import DateEntry
import requests
import xml.etree.ElementTree as ET

from src.base_application.api import parser
from src.base_application.member.manageMembers import manage_members
from src.base_application.app_pages.fileUpload import main
from src.base_application import api_server_ip
import xml.etree.ElementTree as ET


def adminPanel():
    selected_row = None
    window = tk.Tk()
    window.title("Sports Accounting - Admin Panel")
    window.resizable(False, False)

    # Set window size to 80% of the screen resolution
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = 1200
    window_height = 900
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    window.resizable(False, False)

    frame1 = tk.Frame(window, width=window_width / 2, height=window_height, bg="#D9D9D9")
    frame2 = tk.Frame(window, width=window_width / 2, height=window_height, bg="#F0AFAF")

    frame1.pack(side="left", fill="both", expand=True)
    frame2.pack(side="right", fill="both", expand=True)

    # Center the window on the screen
    window.eval('tk::PlaceWindow . center')

    # Get balance from db
    balance = "No data"
    response = requests.get(api_server_ip + "/api/files")
    if len(response.json()) != 0:
        balance = response.json()[0][4]

    # --------------------------------------------------- Functions -------------------------------------------------- #
    def manage_members_button():
        window.destroy()
        manage_members()

    def upload_button_click():
        main()

    def logout_button():
        window.destroy()
        from src.base_application.app_pages.userPanel import create_window
        create_window()

    # Define a function to be called when a row of the table is clicked
    def on_click_table_row(event):
        global selected_row
        # Get the selected item if available
        selected_item = table.selection()
        if selected_item:
            item = selected_item[0]
            # Get the values of the selected item
            values = table.item(item, "values")
            selected_row = values[0]
        else:
            # Handle the case when no row is selected
            selected_row = None

    def edit_button_click():
        global selected_row
        if selected_row is None:
            return
        window.destroy()
        from src.base_application.app_pages.editTransaction import edit_transaction_page_admin
        edit_transaction_page_admin(selected_row)

    def retrieveDB():
        response = requests.get(api_server_ip + "/api/transactions/sql")
        if len(response.json()) == 0:
            return
        # Convert JSON object into an array of tuples
        rows_out = []
        for entry in response.json():
            temp_tuple = (entry[0], entry[6], entry[2], entry[3], entry[1], entry[4])
            rows_out.append(tuple(temp_tuple))
        return rows_out

    def details_button_click():
        global selected_row
        if selected_row is None:
            return
        from src.base_application.app_pages.transactionDetails import transaction_details
        transaction_details(selected_row)

    def retrieveDB_keyword_search(keyword):
        response = requests.get(api_server_ip + "/api/transactions/search/" + str(keyword))
        if response.status_code == 200 and response.json():
            rows_out = []
            for entry in response.json():
                temp_tuple = (entry[0], entry[6], entry[2], entry[3], entry[1], entry[4])
                rows_out.append(temp_tuple)
            return rows_out
        return []  # Ensure an empty list is returned if no data is found

    def get_json_button_click():
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes("-topmost", 1)

        start_date = start_date_picker.get_date()
        end_date = end_date_picker.get_date()

        url = f"{api_server_ip}/api/transactions/filter?start_date={start_date}&end_date={end_date}"

        try:
            response = requests.get(url)
            response.raise_for_status()

            documents = response.json()

            file_path = filedialog.asksaveasfilename(defaultextension='.json')
            if file_path:
                with open(file_path, 'w') as f:
                    json.dump(documents, f, indent=4)
                messagebox.showinfo("Success", "Filtered transactions saved to JSON file successfully.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch transactions: {e}")
        finally:
            root.destroy()

    def get_xml_button_click():
        start_date = start_date_picker.get_date()
        end_date = end_date_picker.get_date()
        url = f"{api_server_ip}/api/downloads?start_date={start_date}&end_date={end_date}"
        try:
            headers = {'Accept': 'application/xml'}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                # Use the root tkinter window for the file dialog
                file_path = filedialog.asksaveasfilename(defaultextension='.xml')

                # Write the XML data to the selected file path
                if file_path:
                    with open(file_path, 'w') as file:
                        file.write(response.text)
                    messagebox.showinfo("Success", "Transactions saved to XML file successfully.")
            else:
                messagebox.showerror("Error", f"Failed to fetch transactions: {response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch transactions: {e}")

    def insert_category():
        # Get the category name from the Entry widget
        category_name = entry_category_name.get()

        # Define the URL of the API endpoint
        url = f"{api_server_ip}/api/categories"

        # Prepare the data payload as a dictionary
        data = {'name': category_name}

        # Use the json parameter of the requests.post method, which automatically
        # encodes the dictionary to JSON, sets the correct Content-Type header,
        # and sends the request as JSON
        response = requests.post(url, json=data)

        # Process the response
        if response.status_code == 201:
            messagebox.showinfo("Success", "Category added successfully.")
            # Optionally, clear the entry widget after successful insertion
            entry_category_name.delete(0, tk.END)
        else:
            # Display an error message if something goes wrong
            messagebox.showerror("Error", f"Failed to add category: {response.text}")

    # ---------------------------------------------------- Frame 1 --------------------------------------------------- #
    label = tk.Label(frame1, text="Admin Panel", font=("Inter", 24, "normal"), bg="#D9D9D9", fg="black", justify="left")
    label.place(x=20, y=20, width=190, height=50)

    line = tk.Label(frame1, text="_______________________________________________________",
                    font=("Inter", 18, "normal"), bg="#D9D9D9", fg="black", justify="left")
    line.place(x=61, y=180, width=450, height=30)

    welcome = tk.Label(frame1, text="Welcome", font=("Inter", 18, "normal"), bg="#D9D9D9",
                       fg="black", justify="left")
    welcome.place(x=15, y=175, width=190, height=30)

    entry_category_name = tk.Entry(frame1, font=("Inter", 14, "normal"), bg="#D9D9D9", fg="black", justify="left")
    entry_category_name.place(x=75, y=330, width=180, height=30)

    button_insert_category = tk.Button(frame1, text="Insert Cost Center", font=("Inter", 12, "normal"), bg="#D9D9D9",
                                       fg="black", justify="left", command=insert_category)
    button_insert_category.place(x=300, y=330, width=180, height=30)

    button = tk.Button(frame1, text="Logout", font=("Inter", 12, "normal"), bg="#D9D9D9", fg="black", justify="left",
                       command=logout_button)
    button.place(x=450, y=175, height=30)

    searchBar = tk.Entry(frame1, font=("Inter", 14, "normal"), bg="#D9D9D9", fg="black", justify="left")
    searchBar.place(x=75, y=400, width=180, height=30)

    start_date_label = tk.Label(frame1, text="Start Date:", font=("Inter", 14), bg="#D9D9D9")
    start_date_label.place(x=75, y=450, width=100, height=25)
    start_date_picker = DateEntry(frame1, width=12, background='darkblue', foreground='white', borderwidth=2,
                                  date_pattern='yyyy-mm-dd')
    start_date_picker.place(x=180, y=450, width=150, height=25)

    end_date_label = tk.Label(frame1, text="End Date:", font=("Inter", 14), bg="#D9D9D9")
    end_date_label.place(x=75, y=480, width=100, height=25)
    end_date_picker = DateEntry(frame1, width=12, background='darkblue', foreground='white', borderwidth=2,
                                date_pattern='yyyy-mm-dd')
    end_date_picker.place(x=180, y=480, width=150, height=25)

    downloadJSONFile = tk.Button(frame1, text="Download Transactions in JSON", font=("Inter", 12, "normal"),
                                 bg="#D9D9D9", fg="black", justify="left", command=get_json_button_click)
    downloadJSONFile.place(x=35, y=550, width=250, height=30)

    downloadXMLFile = tk.Button(frame1, text="Download Transactions in XML", font=("Inter", 12, "normal"),
                                bg="#D9D9D9", fg="black", justify="left", command=get_xml_button_click)
    downloadXMLFile.place(x=300, y=550, width=250, height=30)

    balance_label = tk.Label(frame1, text="Available Balance:", font=("Inter", 15), bg="#D9D9D9", fg="#000000",
                             justify="left")
    balance_label.place(x=35, y=600, width=160, height=24)

    balance_number = tk.Label(frame1, text=balance, font=("Inter", 15), bg="#D9D9D9", fg="#000000", justify="left")
    balance_number.place(x=210, y=600, width=160, height=24)

    search_balance_label = tk.Label(frame1, text="Sum of found transactions:", font=("Inter", 15), bg="#D9D9D9",
                                    fg="#000000", justify="left")
    search_balance_label.place(x=35, y=700, width=240, height=24)

    search_summary_num = tk.Label(frame1, text="", font=("Inter", 15), bg="#D9D9D9", fg="#000000", justify="left")
    search_summary_num.pack_forget()

    # ---------------------------------------------------- Frame 2 --------------------------------------------------- #
    table = ttk.Treeview(frame2, columns=("ID", "Date", "Details", "Description", "Ref", "Amount"),
                         show="headings", style="Custom.Treeview")
    table.heading("ID", text="ID")
    table.heading("Date", text="Date")
    table.heading("Details", text="Company Name")
    table.heading("Description", text="Description")
    table.heading("Ref", text="Ref")
    table.heading("Amount", text="Amount")

    def enable_download_buttons():
        """Enable the download buttons if both start and end dates are selected."""
        start_date = start_date_picker.get_date()
        end_date = end_date_picker.get_date()
        if start_date and end_date:
            downloadJSONFile['state'] = 'normal'
            downloadXMLFile['state'] = 'normal'
        else:
            downloadJSONFile['state'] = 'disabled'
            downloadXMLFile['state'] = 'disabled'

    # Looping through the columns and get the heading
    for column in table["columns"]:
        # Assigning the heading as text of the column
        table.heading(column, text=column, command=lambda: None)

    # Apply the background color to the entire table
    style = ttk.Style()
    style.configure("Custom.Treeview", background="#F0AFAF", rowheight=30)

    table.column("ID", width=20)  # Set width of column zero
    table.column("Date", width=100)  # Set the width of the first column
    table.column("Details", width=200)  # Set the width of the second column
    table.column("Description", width=100)  # Set the width of the third column
    table.column("Ref", width=50)  # Set the width of the forth column
    table.column("Amount", width=100)  # Set the width of the fifth
    table.config(height=20)  # Set the height of the table to 10 rows

    rows = retrieveDB()

    # # Clear existing rows in the table
    table.delete(*table.get_children())

    # Insert retrieved data into the table
    if rows is not None:
        for row in rows:
            table.insert("", "end", values=row)

    # Pack the table into the frame and center it horizontally
    table.pack(fill="both", expand=False)  # Fill the frame with the table
    table.place(x=15, y=100)  # Place the table 15 pixels from the left and 100 pixels from the top
    table.bind("<ButtonRelease-1>", on_click_table_row, "+")  # Bind row selection
    frame2.pack_propagate(False)  # Prevent the frame from resizing to fit the table

    edit_button = ttk.Button(frame2, text="Edit", command=edit_button_click)
    edit_button.place(x=15, y=35, width=100, height=30)

    details_button = ttk.Button(frame2, text="Details", command=details_button_click)
    details_button.place(x=485, y=35, width=100, height=30)

    start_date_picker.bind("<<DateEntrySelected>>", lambda event: enable_download_buttons())
    end_date_picker.bind("<<DateEntrySelected>>", lambda event: enable_download_buttons())

    # Initially disable download buttons until dates are picked
    downloadJSONFile['state'] = 'disabled'
    downloadXMLFile['state'] = 'disabled'

    search = tk.Button(frame1, text="Search Keyword", font=("Inter", 12, "normal"),
                       bg="#D9D9D9", fg="black", justify="left", command=lambda: keyword_search_button(searchBar.get(), table, search_summary_num))
    search.place(x=300, y=400, width=180, height=30)

    update_button = ttk.Button(frame2, text="Update", command=lambda: update_button_click(table, search_summary_num))
    update_button.place(x=235, y=35, width=100, height=30)

    def on_closing():
        window.destroy()

    def keyword_search_button(keyword, table, widget):
        # Initialize keyword_table
        keyword_table = []

        # Clear existing rows in the table
        table.delete(*table.get_children())

        # Show all transactions if keyword entry field is empty
        if len(keyword) == 0:
            keyword_table = retrieveDB()
            # Remove the sum per search label if no keyword is input
            widget.config(text="")
        else:
            keyword_table = retrieveDB_keyword_search(keyword)
            sum_output = 0
            # Calculate total sum of money per keyword
            for tuple_entry in keyword_table:
                sum_output += float(tuple_entry[5])
            widget.config(text=str(sum_output))
            widget.place(x=275, y=700, width=350, height=24)

        # Insert retrieved data into the table
        for result in keyword_table:
            table.insert("", "end", values=result)

    def update_button_click(table_inp, widget):
        # Clear existing rows in the table
        table_inp.delete(*table_inp.get_children())
        searchBar.delete(first=0, last=255)
        # Show all transactions if keyword entry field is empty
        rows = retrieveDB()
        if len(rows) == 0:
            return
        # Insert retrieved data into the table
        for result in rows:
            table_inp.insert("", "end", values=result)
        # Remove the sum per search label if table is updated
        widget.config(text="")
        refresh_balance_label()

    def refresh_balance_label():
        # Create an instance of FileWatcher
        watcher = parser.FileWatcher("../../MT940files")
        # Call the update_balance method on the instance
        new_balance = watcher.update_balance()
        if new_balance is not None:
            balance_number.configure(text=str(new_balance))
        else:
            balance_number.config(text="Failed to update")

    # Bind the on_closing function to the window close event
    window.protocol("WM_DELETE_WINDOW", on_closing)
    window.lift()  # Lift the window to the top after mainloop()
    # Start the main event loop
    window.mainloop()
