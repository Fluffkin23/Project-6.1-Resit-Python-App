import json
import tkinter as tk
import requests
from src.base_application.admin.adminPanel import adminPanel
from src.base_application import api_server_ip
from src.base_application.utils import hash_password
from tkinter import messagebox


def login_admin_page():
    # create the main window
    window = tk.Tk()
    window.geometry("1200x900")
    window.title("Sports Accounting - Admin Login")

    window.resizable(False, False)

    def login_button_click(password):
        ...
        try:
            json_resp = requests.post(api_server_ip + "/api/login/admin", data={"password": password})
            if json_resp.status_code == 200:
                try:
                    data = json_resp.json()
                    if len(data) == 0:
                        # Handle case where response is empty
                        messagebox.showerror("Error", "Invalid password")
                        return
                except json.decoder.JSONDecodeError:
                    # Handle case where response is not in JSON format
                    messagebox.showerror("Error", "Unexpected response from server")
                    return
            else:
                # Handle non-200 status codes
                messagebox.showerror("Error", "Unexpected response from server")
                return
        except requests.exceptions.RequestException as e:
            # Handle request exception
            messagebox.showerror("Error", f"Request error: {str(e)}")
            return



    def back_button_click():
        from src.base_application.app_pages.userPanel import create_window
        window.destroy()
        create_window()


    # create two frames side by side
    frame1 = tk.Frame(window, width=600, height=900, bg="#D9D9D9")
    frame2 = tk.Frame(window, width=600, height=900, bg="#F0AFAF")

    frame1.pack(side="left")
    frame2.pack(side="right")

    # add a label to frame1 with the specified properties
    label = tk.Label(frame1, text="Admin Panel", font=("Inter", 24, "normal"), bg="#D9D9D9", fg="black", justify="left")
    label.place(x=20, y=20, width=190, height=50)

    # set the line height to 29 pixels and vertical alignment to top
    label.config(anchor="nw", pady=0, padx=0, wraplength=0, height=0, width=0)

    # add a label and text area to frame1 for Password
    pass_label = tk.Label(frame1, text="Password", font=("Inter", 18, "normal"), bg="#D9D9D9", fg="black",
                          justify="left")
    pass_label.place(x=20, y=350, width=123, height=24)
    pass_entry = tk.Entry(frame1, show="*", font=("Inter", 18, "normal"), bg="white", fg="black", justify="left")
    pass_entry.place(x=153, y=350, width=300, height=28)

    # add a login button to frame1
    login_button = tk.Button(frame1, text="Login", font=("Inter", 12), bg="white", fg="black",
                             bd=0, highlightthickness=0, activebackground="#B3B3B3",
                             command=lambda: login_button_click(pass_entry.get()))
    login_button.place(x=200, y=450, width=82, height=24)

    # add a back button to frame1
    back_button = tk.Button(frame1, text="Back", font=("Inter", 12), bg="white", fg="black",
                            bd=0, highlightthickness=0, activebackground="#B3B3B3",
                            command=back_button_click)
    back_button.place(x=20, y=700, width=82, height=24)

    # run the main loop
    window.mainloop()

