import tkinter as tk
from tkinter import messagebox

# Adjust these imports according to your project structure
from userPanel import create_window
from registerPage import register_page

def launch_app():
    # Create the main window
    root = tk.Tk()
    root.title("Launch Application")
    root.geometry("300x200")

    # Button to create a new association
    def on_new_assoc():
        root.destroy()
        register_page()

    # Button to go to the user panel
    def on_user_panel():
        root.destroy()
        create_window()

    # Decision Buttons
    btn_new_assoc = tk.Button(root, text="Create New Association", command=on_new_assoc)
    btn_new_assoc.pack(pady=10, expand=True)

    btn_user_panel = tk.Button(root, text="Enter User Panel", command=on_user_panel)
    btn_user_panel.pack(pady=10, expand=True)

    root.mainloop()

if __name__ == "__main__":
    launch_app()
