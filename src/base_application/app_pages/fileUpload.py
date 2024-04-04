import json
from tkinter import Tk, filedialog, CENTER
from tkinter.ttk import Button, Label
import requests
from src.base_application import api_server_ip
from src.base_application.utils import check_mt940_file, parse_mt940_file


class MainWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Sports Accounting - MT940 Parser")
        self.master.attributes("-topmost", True)

        # Center the window
        self.master.eval('tk::PlaceWindow . center')

        # Adjust window size to 80% of the screen resolution
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        width = int(screen_width * 0.8)
        height = int(screen_height * 0.8)
        x_coordinate = (screen_width - width) // 2
        y_coordinate = (screen_height - height) // 2
        self.master.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")

        # Create the "Select Files" button
        self.select_files_button = Button(self.master, text="Select Files", command=self.select_files)
        self.select_files_button.pack()

        # Create the label to display the selected files
        self.selected_files_label = Label(self.master, text="")
        self.selected_files_label.pack()

        # Create the "Parse" button
        self.parse_button = Button(self.master, text="Parse", command=self.parse_files)
        self.parse_button.pack()

        # Initialize list of file paths
        self.file_paths = []

    def select_files(self):
        """Open a file dialog to select MT940 files."""
        file_paths = filedialog.askopenfilenames(defaultextension=".sta",
                                                 filetypes=[("MT940 Files", "*.sta"), ("All Files", "*.*")])
        self.selected_files_label.config(text="Selected Files: " + str(file_paths))
        self.file_paths = file_paths

    def parse_files(self):
        """Parse the selected MT940 files and save the results as JSON files."""
        for file_path in self.file_paths:
            # Check MT940 file
            if check_mt940_file(file_path):
                # Save to NoSQL DB
                url = api_server_ip + '/api/uploadFile'
                json_data = parse_mt940_file(file_path)
                headers = {'Content-Type': 'application/json'}
                response = requests.post(url, json=json_data, headers=headers)

                # Save to SQL DB FILE
                url = api_server_ip + '/api/insertFile'
                headers = {'Content-Type': 'application/json'}
                response = requests.post(url, json=json_data, headers=headers)

                # Save to SQL DB Transaction
                url = api_server_ip + '/api/insertTransaction'
                headers = {'Content-Type': 'application/json'}
                response = requests.post(url, json=json_data, headers=headers)

        # Close Window
        self.master.destroy()


def main():
    root = Tk()
    MainWindow(root)
    root.lift()
    root.mainloop()


if __name__ == "__main__":
    main()
