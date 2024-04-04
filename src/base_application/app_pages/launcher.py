import tkinter as tk
from tkinter import messagebox

# Adjust these imports according to your project structure
from userPanel import create_window
from registerPage import register_page
from src.base_application.admin.adminLogin import login_admin_page

def launch_app():
    # Create the main window
    root = tk.Tk()
    root.title("Sports Accounting Launcher")

    # Function to center the window on the screen
    def center_window(width, height):
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        root.geometry(f"{width}x{height}+{x}+{y}")

    # Calculate the window size
    width = int(0.3 * root.winfo_screenwidth())
    height = int(0.3 * root.winfo_screenheight())
    center_window(width, height)

    # Function to create buttons with a consistent style
    def create_button(parent, text, command):
        button = tk.Button(parent, text=text, command=command, width=20, height=2, font=("Arial", 12), bd=2,
                           relief="raised", bg="#4CAF50", fg="white")
        button.pack(pady=(10, 5), padx=10, ipadx=10, ipady=5, fill=tk.BOTH, expand=True)
        return button

    # Button to create a new association
    def on_new_assoc():
        root.destroy()
        register_page()

    # Button to go to the user panel
    def on_user_panel():
        root.destroy()
        create_window()

    def on_admin_login():
        root.destroy()
        login_admin_page()

    # Decision Buttons
    btn_new_assoc = create_button(root, "Create New Association", on_new_assoc)
    btn_user_panel = create_button(root, "Enter User Panel", on_user_panel)
    btn_admin_login = create_button(root, "Admin Login", on_admin_login)

    root.lift()  # Lift the window to the top after mainloop()

    root.mainloop()

if __name__ == "__main__":
    launch_app()
