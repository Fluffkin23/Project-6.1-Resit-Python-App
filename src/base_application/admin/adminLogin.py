import json
import tkinter as tk
import requests
from src.base_application.admin.adminPanel import adminPanel
from src.base_application import api_server_ip
from src.base_application.utils import hash_password
from tkinter import messagebox


def login_admin_page():
    window = tk.Tk()
    window.geometry("1200x900")
    window.title("Sports Accounting - Admin Login")
    window.resizable(False, False)

    def login_button_click(username, password):
        response = requests.get(api_server_ip + "/api/associations")
        if response.status_code != 200:
            messagebox.showerror("Error", "Could not fetch data from the server")
            return

        try:
            associations = response.json()
            hashed_password = hash_password(password)
            login_successful = False

            for assoc in associations:
                _, assoc_username, assoc_password_hash = assoc
                if assoc_username == username and hashed_password == assoc_password_hash:
                    login_successful = True
                    break

            if login_successful:
                window.destroy()
                adminPanel()
            else:
                messagebox.showerror("Error", "Incorrect username or password")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

        if pass_entry.winfo_exists():
            pass_entry.delete(0, tk.END)
    def back_button_click():
        window.destroy()
        from src.base_application.app_pages.userPanel import create_window
        create_window()

    frame1 = tk.Frame(window, width=600, height=900, bg="#D9D9D9")
    frame2 = tk.Frame(window, width=600, height=900, bg="#F0AFAF")
    frame1.pack(side="left")
    frame2.pack(side="right")

    label = tk.Label(frame1, text="Admin Panel", font=("Inter", 24, "normal"), bg="#D9D9D9", fg="black", justify="left")
    label.place(x=20, y=20, width=190, height=50)

    # Username Field
    user_label = tk.Label(frame1, text="Username", font=("Inter", 18, "normal"), bg="#D9D9D9", fg="black",
                          justify="left")
    user_label.place(x=20, y=300, width=123, height=24)
    user_entry = tk.Entry(frame1, font=("Inter", 18, "normal"), bg="white", fg="black", justify="left")
    user_entry.place(x=153, y=300, width=300, height=28)

    # Password Field
    pass_label = tk.Label(frame1, text="Password", font=("Inter", 18, "normal"), bg="#D9D9D9", fg="black",
                          justify="left")
    pass_label.place(x=20, y=350, width=123, height=24)
    pass_entry = tk.Entry(frame1, show="*", font=("Inter", 18, "normal"), bg="white", fg="black", justify="left")
    pass_entry.place(x=153, y=350, width=300, height=28)

    # Login Button
    login_button = tk.Button(frame1, text="Login", font=("Inter", 12), bg="white", fg="black", bd=0,
                             highlightthickness=0, activebackground="#B3B3B3",
                             command=lambda: login_button_click(user_entry.get(), pass_entry.get()))
    login_button.place(x=200, y=400, width=82, height=24)

    # Back Button
    back_button = tk.Button(frame1, text="Back", font=("Inter", 12), bg="white", fg="black", bd=0, highlightthickness=0,
                            activebackground="#B3B3B3", command=back_button_click)
    back_button.place(x=20, y=700, width=82, height=24)

    window.mainloop()
