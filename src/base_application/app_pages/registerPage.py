import json
import tkinter as tk
from tkinter import ttk
import requests
from src.base_application import api_server_ip
from userPanel import create_window
from src.base_application.utils import hash_password


def register_page():
    try:
        # Check if a user is already registered
        json_test = requests.get(api_server_ip + "/api/associations")
        json_data = json_test.json()
        if len(json_data) != 0:
            # Navigate to user panel
            create_window()
            return
    except json.decoder.JSONDecodeError:
        # Handle case where response couldn't be parsed as JSON
        print("Error: Server response couldn't be parsed as JSON.")
        # Add appropriate error handling here, such as displaying an error message to the user or logging the error

    # Create the main window
    root = tk.Tk()
    root.title("Register a user")
    root.geometry("1200x900")

    def button_click(name, password, iban):
        hashed_pass = hash_password(password)
        # Save to DB
        payload = {'accountID': iban,
                   'name': name,
                   'password': hashed_pass}
        json_data = json.dumps(payload, indent=4)
        url = api_server_ip + '/api/associations'
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(url, json=json_data, headers=headers)
            response.raise_for_status()  # Raise exception for 4xx or 5xx status codes
            # If the request is successful, navigate to the user panel
            root.destroy()
            create_window()
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Log the error
            # Handle the error gracefully, e.g., display an error message to the user
        except Exception as err:
            print(f'Other error occurred: {err}')  # Log the error
            # Handle the error gracefully, e.g., display an error message to the user

    # Create a frame to hold the left section
    left_frame = tk.Frame(root, width=600, height=900,  bg="#D9D9D9")  # Set the background color to grey
    left_frame.pack(side="left", fill="both", expand=True)

    # Create a frame to hold the right section
    right_frame = tk.Frame(root, width=600, height=900,  bg="#F0AFAF")  # Set the background color to pink
    right_frame.pack(side="right", fill="both", expand=True, padx=(0, 5))  # Add padding to prevent overlap

    # Headings
    heading1 = tk.Label(left_frame, text="New user registration", font=("Roboto", 28), bg="#D9D9D9", fg="#000000",
                        justify="center")
    heading1.place(x=85, y=100, width=350, height=50)

    heading2 = tk.Label(left_frame, text="Before we continue let's make an account", font=("Roboto", 14), bg="#D9D9D9",
                        fg="#000000",
                        justify="center")
    heading2.place(x=25, y=160, width=500, height=50)

    # Inputs for the registration
    # assoc name
    assoc_name_label = tk.Label(text="Association Name", font=("Inter", 14, "normal"), bg="#D9D9D9", fg="black")
    assoc_name_label.place(x=20, y=306, width=147, height=18)
    assoc_name_input = tk.Entry(left_frame)
    assoc_name_input.place(x=180, y=300, width=300, height=30)

    # password
    assoc_passwd_label = tk.Label(text="Password", font=("Inter", 14, "normal"), bg="#D9D9D9", fg="black")
    assoc_passwd_label.place(x=20, y=345, width=120, height=18)

    passwd = tk.Entry(left_frame)
    passwd.place(x=180, y=345, width=300, height=30)

    # IBAN
    assoc_iban_label = tk.Label(text="IBAN", font=("Inter", 14, "normal"), bg="#D9D9D9", fg="black")
    assoc_iban_label.place(x=20, y=390, width=120, height=18)

    iban = tk.Entry(left_frame)
    iban.place(x=180, y=390, width=300, height=30)

    button1 = ttk.Button(left_frame, text="Sign up", command=lambda: button_click(assoc_name_input.get(), passwd.get(), iban.get()))

    button1.place(x=160, y=600, width=300, height=60)
    # Start the main event loop
    root.mainloop()
    register_page()