import tkinter as tk
from tkinter import INSERT, messagebox
import requests
from src.base_application import api_server_ip


def center_window(window, width_percent=0.8, height_percent=0.8):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    window_width = int(screen_width * width_percent)
    window_height = int(screen_height * height_percent)

    x_coordinate = int((screen_width - window_width) / 2)
    y_coordinate = int((screen_height - window_height) / 2)

    window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")


def edit_transaction_page(transaction_id):
    def get_members():
        response = requests.get(api_server_ip + "/api/members")
        if len(response.json()) == 0:
            return

        # Convert JSON object into an array with values memberID-memberName
        members = [None]
        for entry in response.json():
            members.append(str(entry[0]) + "-" + str(entry[1]))

        return members

    def get_category():
        response = requests.get(api_server_ip + "/api/categories")
        if len(response.json()) == 0:
            return

        # Convert JSON object into an array with values categoryID-categoryName
        category = [None]
        for entry in response.json():
            category.append(str(entry[0]) + "-" + str(entry[1]))
        return category

    def get_transaction_json():
        response = requests.get(api_server_ip + "/api/transactions/" + str(transaction_id))
        if len(response.json()) == 0:
            return

        return response.json()[0]

    transaction_json = get_transaction_json()

    # Create a window
    window = tk.Tk()
    window.title("Sports Accounting - Edit Transaction")
    center_window(window)  # Center the window on the screen

    # Get list of options for drop down menu
    options_list_category = get_category()
    value_category = tk.StringVar(window)
    value_category.set("None")
    # TEMP
    options_list_members = get_members()
    value_member = tk.StringVar(window)
    value_member.set("None")

    # Two containers for other elements
    frame_left = tk.Frame(window, bg="#D9D9D9")
    frame_right = tk.Frame(window, bg="#F0AFAF")
    frame_left.pack(side="left", fill="both", expand=True)
    frame_right.pack(side="right", fill="both", expand=True)

    # Title of the window Admin Panel
    label_admin_panel = tk.Label(frame_left, text="Admin Panel", font=("Inter", 24, "normal"), fg="#575757", bg="#D9D9D9", justify="left")
    label_admin_panel.pack(pady=(20, 0))

    # Edit Transaction Title
    label_edit_trans = tk.Label(frame_left, text="Edit Transaction", font=("Inter", 35, "normal"), fg="black", bg="#D9D9D9", justify="center")
    label_edit_trans.pack(pady=(40, 0))

    # Description Text Box and Label
    label_desc = tk.Label(frame_left, text="Description", font=("Inter", 20, "normal"), fg="#575757", bg="#D9D9D9", justify="left")
    label_desc.pack()
    textbox_description = tk.Text(frame_left, bg="#D9D9D9", bd=1, fg="black", state="normal", relief="solid")
    textbox_description.pack(pady=(10, 0), padx=20, fill="both", expand=True)
    description_trans = ""
    if transaction_json is not None:
        description_trans = transaction_json[3]
    textbox_description.insert(INSERT, str(description_trans))

    # Category/Member Menu and Label
    label_category = tk.Label(frame_left, text="Category", font=("Inter", 20, "normal"), fg="#575757", bg="#D9D9D9", justify="left")
    label_category.pack(pady=(20, 0))
    optionmenu_category = tk.OptionMenu(frame_left, value_category, *options_list_category)
    optionmenu_category.pack(pady=(0, 20), padx=20, fill="x")

    label_member = tk.Label(frame_left, text="Member", font=("Inter", 20, "normal"), fg="#575757", bg="#D9D9D9", justify="left")
    label_member.pack()
    optionmenu_member = tk.OptionMenu(frame_left, value_member, *options_list_members)
    optionmenu_member.pack(pady=(0, 20), padx=20, fill="x")

    # Save Button
    button_save = tk.Button(frame_left, text="Save", font=("Inter", 20), bg="#F0AFAF", fg="black", bd=0, highlightthickness=0, activebackground="#B3B3B3", command=lambda: get_input_save(value_category.get(), value_member.get(), textbox_description.get(1.0, 'end-1c')))
    button_save.pack(pady=(0, 20), padx=20, fill="x")

    # Back Button
    button_back = tk.Button(frame_left, text="Back", font=("Inter", 20), bg="white", fg="black", bd=0, highlightthickness=0, activebackground="#B3B3B3", command=lambda : back_button_click())
    button_back.pack(pady=(0, 20), padx=20, fill="x")

    def back_button_click():
        window.destroy()
        from src.base_application.admin.adminPanel import adminPanel
        adminPanel()

    def get_input_save(category, member, desc):
        # Ensure you're handling empty string values properly
        member_out = None
        if member != "":
            member_out = member.split("-")[0]

        category_out = None
        if category != "":
            category_out = category.split("-")[0]

        # Save to DB
        payload = {'desc': desc, 'category': category_out, 'member': member_out}
        response = requests.put(api_server_ip + "/api/transactions/" + str(transaction_id), json=payload)

        if response.status_code == 200:
            # Transaction updated successfully
            print("Transaction updated successfully")
            messagebox.showinfo("Success", "Transaction updated successfully")
        else:
            # Failed to update transaction
            print("Failed to update transaction:", response.text)

    # Ensure the window pops up on top of other windows
    window.attributes('-topmost', True)
    window.lift()  # Lift the window to the top after mainloop()
    # Start the window
    window.mainloop()


def edit_transaction_page_admin(transaction_id):
    def get_members():
        response = requests.get(api_server_ip + "/api/members")
        if len(response.json()) == 0:
            return

        # Convert JSON object into an array with values memberID-memberName
        members = [None]
        for entry in response.json():
            members.append(str(entry[0]) + "-" + str(entry[1]))

        return members

    def get_category():
        response = requests.get(api_server_ip + "/api/categories")
        if len(response.json()) == 0:
            return

        # Convert JSON object into an array with values categoryID-categoryName
        category = [None]
        for entry in response.json():
            category.append(str(entry[0]) + "-" + str(entry[1]))
        return category

    def get_transaction_json():
        response = requests.get(api_server_ip + "/api/transactions/" + str(transaction_id))
        if len(response.json()) == 0:
            return

        return response.json()[0]

    transaction_json = get_transaction_json()

    # Create a window
    window = tk.Tk()
    window.title("Sports Accounting - Edit Transaction")
    center_window(window)  # Center the window on the screen

    # Get list of options for drop down menu
    options_list_category = get_category()
    value_category = tk.StringVar(window)
    value_category.set("None")
    # TEMP
    options_list_members = get_members()
    value_member = tk.StringVar(window)
    value_member.set("None")

    # Two containers for other elements
    frame_left = tk.Frame(window, bg="#D9D9D9")
    frame_right = tk.Frame(window, bg="#F0AFAF")
    frame_left.pack(side="left", fill="both", expand=True)
    frame_right.pack(side="right", fill="both", expand=True)

    # Title of the window Admin Panel
    label_admin_panel = tk.Label(frame_left, text="Admin Panel", font=("Inter", 24, "normal"), fg="#575757", bg="#D9D9D9", justify="left")
    label_admin_panel.pack(pady=(20, 0))

    # Edit Transaction Title
    label_edit_trans = tk.Label(frame_left, text="Edit Transaction", font=("Inter", 35, "normal"), fg="black", bg="#D9D9D9", justify="center")
    label_edit_trans.pack(pady=(40, 0))

    # Description Text Box and Label
    label_desc = tk.Label(frame_left, text="Description", font=("Inter", 20, "normal"), fg="#575757", bg="#D9D9D9", justify="left")
    label_desc.pack()
    textbox_description = tk.Text(frame_left, bg="#D9D9D9", bd=1, fg="black", state="normal", relief="solid")
    textbox_description.pack(pady=(10, 0), padx=20, fill="both", expand=True)
    description_trans = ""
    if transaction_json is not None:
        description_trans = transaction_json[3]
    textbox_description.insert(INSERT, str(description_trans))

    # Category/Member Menu and Label
    label_category = tk.Label(frame_left, text="Cost center", font=("Inter", 20, "normal"), fg="#575757", bg="#D9D9D9", justify="left")
    label_category.pack(pady=(20, 0))
    optionmenu_category = tk.OptionMenu(frame_left, value_category, *options_list_category)
    optionmenu_category.pack(pady=(0, 20), padx=20, fill="x")

    # label_member = tk.Label(frame_left, text="Member", font=("Inter", 20, "normal"), fg="#575757", bg="#D9D9D9", justify="left")
    # label_member.pack()
    # optionmenu_member = tk.OptionMenu(frame_left, value_member, *options_list_members)
    # optionmenu_member.pack(pady=(0, 20), padx=20, fill="x")

    # Save Button
    button_save = tk.Button(frame_left, text="Save", font=("Inter", 20), bg="#F0AFAF", fg="black", bd=0, highlightthickness=0, activebackground="#B3B3B3", command=lambda: get_input_save(value_category.get(), value_member.get(), textbox_description.get(1.0, 'end-1c')))
    button_save.pack(pady=(0, 20), padx=20, fill="x")

    # Back Button
    button_back = tk.Button(frame_left, text="Back", font=("Inter", 20), bg="white", fg="black", bd=0, highlightthickness=0, activebackground="#B3B3B3", command=lambda : back_button_click())
    button_back.pack(pady=(0, 20), padx=20, fill="x")

    def back_button_click():
        window.destroy()
        from src.base_application.admin.adminPanel import adminPanel
        adminPanel()

    def get_input_save(category, member, desc):
        # Ensure you're handling empty string values properly
        member_out = None
        if member != "":
            member_out = member.split("-")[0]

        category_out = None
        if category != "":
            category_out = category.split("-")[0]

        # Save to DB
        payload = {'desc': desc, 'category': category_out, 'member': member_out}
        response = requests.put(api_server_ip + "/api/transactions/" + str(transaction_id), json=payload)

        if response.status_code == 200:
            # Transaction updated successfully
            print("Transaction updated successfully")
            messagebox.showinfo("Success", "Transaction updated successfully")
        else:
            # Failed to update transaction
            print("Failed to update transaction:", response.text)
            messagebox.showerror("Failed to update transaction", response.text)

    # Ensure the window pops up on top of other windows
    window.attributes('-topmost', True)

    # Start the window
    window.mainloop()
