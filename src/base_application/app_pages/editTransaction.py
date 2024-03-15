import tkinter as tk
from tkinter import INSERT

import requests
from src.base_application import api_server_ip


def edit_transaction_page(transaction_id):
    def get_members():
        response = requests.get(api_server_ip + "/api/getMembers")
        if len(response.json()) == 0:
            return

        # Convert JSON object into an array with values memberID-memberName
        members = [None]
        for entry in response.json():
            members.append(str(entry[0]) + "-" + str(entry[1]))

        return members

    def get_category():
        response = requests.get(api_server_ip + "/api/getCategory")
        if len(response.json()) == 0:
            return

        # Convert JSON object into an array with values categoryID-categoryName
        category = [None]
        for entry in response.json():
            category.append(str(entry[0]) + "-" + str(entry[1]))
        return category

    def get_transaction_json():
        response = requests.get(api_server_ip + "/api/getTransactionOnId/" + transaction_id)
        if len(response.json()) == 0:
            return

        return response.json()[0]

    transaction_json = get_transaction_json()

    # Create a standard size window of 1200x900 pixels, not resizable
    window = tk.Tk()
    window.geometry("1200x900")
    window.resizable(False, False)
    window.title("Sports Accounting - Edit Transaction")

    # Two containers for other elements
    frame_left = tk.Frame(window, width=600, height=900, bg="#D9D9D9")
    frame_right = tk.Frame(window, width=600, height=900, bg="#F0AFAF")
    frame_left.pack(side="left")
    frame_right.pack(side="right")

    # Get list of options for drop down menu
    options_list_category = get_category()
    value_category = tk.StringVar(frame_left)
    value_category.set("None")
    # TEMP
    options_list_members = get_members()
    value_member = tk.StringVar(frame_left)
    value_member.set("None")

    # Title of the window Admin Panel
    label_admin_panel = tk.Label(frame_left, text="Admin Panel", font=("Inter", 24, "normal"), fg="#575757", bg="#D9D9D9", justify="left")
    label_admin_panel.place(x=20, y=20, width=190, height=50)

    # Edit Transaction Title
    label_edit_trans = tk.Label(frame_left, text="Edit Transaction", font=("Inter", 35, "normal"), fg="black", bg="#D9D9D9", justify="center")
    label_edit_trans.place(x=0, y=90, width=600, height=140)

    # Description Text Box and Label
    label_desc = tk.Label(frame_left, text="Description", font=("Inter", 20, "normal"), fg="#575757", bg="#D9D9D9", justify="left")
    label_desc.place(x=25, y=230, width=190, height=50)
    textbox_description = tk.Text(frame_left, bg="#D9D9D9", bd=1, fg="black", state="normal", relief="solid")
    textbox_description.place(x=50, y=290, height=200, width=500)
    description_trans = ""
    if transaction_json is not None:
        description_trans = transaction_json[3]
    textbox_description.insert(INSERT, str(description_trans))

    # Category/Member Menu and Label
    label_category = tk.Label(frame_left, text="Category", font=("Inter", 20, "normal"), fg="#575757", bg="#D9D9D9", justify="left")
    label_category.place(x=10, y=490, width=190, height=50)
    optionmenu_category = tk.OptionMenu(frame_left, value_category, *options_list_category)
    optionmenu_category.place(x=50, y=540, height=30, width=500)

    label_member = tk.Label(frame_left, text="Member", font=("Inter", 20, "normal"), fg="#575757", bg="#D9D9D9", justify="left")
    label_member.place(x=10, y=570, width=190, height=50)
    optionmenu_member = tk.OptionMenu(frame_left, value_member, *options_list_members)
    optionmenu_member.place(x=50, y=620, height=30, width=500)

    #Save Button
    button_save = tk.Button(frame_left, text="Save", font=("Inter", 20), bg="#F0AFAF", fg="black", bd=0, highlightthickness=0, activebackground="#B3B3B3", command=lambda: get_input_save(value_category.get(), value_member.get(), textbox_description.get(1.0, 'end-1c')))
    button_save.place(x=50, y=700, width=500, height=50)

    #Back Button
    button_back = tk.Button(frame_left, text="Back", font=("Inter", 20), bg="white", fg="black", bd=0, highlightthickness=0, activebackground="#B3B3B3", command=lambda : back_button_click())
    button_back.place(x=20, y=820, width=100, height=50)

    def back_button_click():
        window.destroy()
        from src.base_application.app_pages.userPanel import create_window
        create_window()

    def get_input_save(category, member, desc):
        member_out = None
        category_out = None
        if member is not None:
            member_out = member.split("-")[0]
        if category is not None:
            category_out = category.split("-")[0]

        # Save to DB
        payload = {'trans_id': transaction_id, 'desc': desc, 'category': category_out, 'member': member_out}
        response = requests.put(api_server_ip + "/api/updateTransaction", data=payload)
        back_button_click()

    # Start the window
    window.mainloop()


def edit_transaction_page_admin(transaction_id):
    def get_members():
        response = requests.get(api_server_ip + "/api/getMembers")
        if len(response.json()) == 0:
            return

        # Convert JSON object into an array with values memberID-memberName
        members = [None]
        for entry in response.json():
            members.append(str(entry[0]) + "-" + str(entry[1]))

        return members

    def get_category():
        response = requests.get(api_server_ip + "/api/getCategory")
        if len(response.json()) == 0:
            return

        # Convert JSON object into an array with values categoryID-categoryName
        category = [None]
        for entry in response.json():
            category.append(str(entry[0]) + "-" + str(entry[1]))
        return category

    def get_transaction_json():
        response = requests.get(api_server_ip + "/api/getTransactionOnId/" + transaction_id)
        if len(response.json()) == 0:
            return

        return response.json()[0]

    transaction_json = get_transaction_json()

    # Create a standard size window of 1200x900 pixels, not resizable
    window = tk.Tk()
    window.geometry("1200x900")
    window.resizable(False, False)
    window.title("Sports Accounting - Edit Transaction")

    # Two containers for other elements
    frame_left = tk.Frame(window, width=600, height=900, bg="#D9D9D9")
    frame_right = tk.Frame(window, width=600, height=900, bg="#F0AFAF")
    frame_left.pack(side="left")
    frame_right.pack(side="right")

    # Get list of options for drop down menu
    options_list_category = get_category()
    value_category = tk.StringVar(frame_left)
    value_category.set("None")
    # TEMP
    options_list_members = get_members()
    value_member = tk.StringVar(frame_left)
    value_member.set("None")

    # Title of the window Admin Panel
    label_admin_panel = tk.Label(frame_left, text="Admin Panel", font=("Inter", 24, "normal"), fg="#575757", bg="#D9D9D9", justify="left")
    label_admin_panel.place(x=20, y=20, width=190, height=50)

    # Edit Transaction Title
    label_edit_trans = tk.Label(frame_left, text="Edit Transaction", font=("Inter", 35, "normal"), fg="black", bg="#D9D9D9", justify="center")
    label_edit_trans.place(x=0, y=90, width=600, height=140)

    # Description Text Box and Label
    label_desc = tk.Label(frame_left, text="Description", font=("Inter", 20, "normal"), fg="#575757", bg="#D9D9D9", justify="left")
    label_desc.place(x=25, y=230, width=190, height=50)
    textbox_description = tk.Text(frame_left, bg="#D9D9D9", bd=1, fg="black", state="normal", relief="solid")
    textbox_description.place(x=50, y=290, height=200, width=500)
    description_trans = ""
    if transaction_json is not None:
        description_trans = transaction_json[3]
    textbox_description.insert(INSERT, str(description_trans))

    # Category/Member Menu and Label
    label_category = tk.Label(frame_left, text="Cost center", font=("Inter", 20, "normal"), fg="#575757", bg="#D9D9D9", justify="left")
    label_category.place(x=10, y=490, width=190, height=50)
    optionmenu_category = tk.OptionMenu(frame_left, value_category, *options_list_category)
    optionmenu_category.place(x=50, y=540, height=30, width=500)

    # label_member = tk.Label(frame_left, text="Member", font=("Inter", 20, "normal"), fg="#575757", bg="#D9D9D9", justify="left")
    # label_member.place(x=10, y=570, width=190, height=50)
    # optionmenu_member = tk.OptionMenu(frame_left, value_member, *options_list_members)
    # optionmenu_member.place(x=50, y=620, height=30, width=500)

    #Save Button
    button_save = tk.Button(frame_left, text="Save", font=("Inter", 20), bg="#F0AFAF", fg="black", bd=0, highlightthickness=0, activebackground="#B3B3B3", command=lambda: get_input_save(value_category.get(), value_member.get(), textbox_description.get(1.0, 'end-1c')))
    button_save.place(x=50, y=700, width=500, height=50)

    #Back Button
    button_back = tk.Button(frame_left, text="Back", font=("Inter", 20), bg="white", fg="black", bd=0, highlightthickness=0, activebackground="#B3B3B3", command=lambda : back_button_click())
    button_back.place(x=20, y=820, width=100, height=50)

    def back_button_click():
        window.destroy()
        from src.base_application.admin.adminPanel import adminPanel
        adminPanel()

    def get_input_save(category, member, desc):
        member_out = None
        category_out = None
        if member is not None:
            member_out = member.split("-")[0]
        if category is not None:
            category_out = category.split("-")[0]

        # Save to DB
        payload = {'trans_id': transaction_id, 'desc': desc, 'category': category_out, 'member': member_out}
        response = requests.put(api_server_ip + "/api/updateTransaction", data=payload)
        back_button_click()

    # Start the window
    window.mainloop()