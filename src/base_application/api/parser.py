import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests

from src.base_application import api_server_ip
from src.base_application.utils import check_mt940_file, parse_mt940_file


class FileWatcher:
    def __init__(self, watch_directory):
        self.watch_directory = watch_directory

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            print(f"File {file_path} has been created.")
            # Store raw data in NoSQL database
            self.store_in_nosql_database(file_path)
            # Make API call for further processing
            self.process_file_via_api(file_path)
            self.store_in_nosql_database(file_path)

    def store_in_nosql_database(self, file_path):
        # Placeholder: Add your logic to store the file in NoSQL database
        print(f"Storing {file_path} in NoSQL database as raw data.")

    def store_in_sql_database(self, file_path):
        # Placeholder: Add your logic to store the file in NoSQL database
        print(f"Storing {file_path} in SQL database as raw data.")

    def update_balance(self):
        try:
            # API call to get the new balance after file upload
            balance_response = requests.get(api_server_ip + "/api/getFile")
            balance_data = balance_response.json()
            new_total_balance = sum(float(file_data[4]) for file_data in balance_data if len(file_data) > 4)
            return new_total_balance
        except Exception as e:
            print(f"Error updating balance: {e}")
            return None

    def process_file_via_api(self, file_path):

        # Placeholder: Adjust payload and headers as needed for your specific API
        with open(file_path, 'rb') as file:
            if check_mt940_file(file_path):
                url = url = api_server_ip + '/api/uploadFile'
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

            if response.status_code == 200:
                print(f"File {file_path} processed successfully via API.")
            else:
                print(f"Error processing file {file_path} via API. Status Code: {response.status_code}")
        new_balance = self.update_balance()
        if new_balance is not None:
            print(f"New total balance is: {new_balance}")
        else:
            print("Failed to update balance.")

    def start(self):
        event_handler = FileSystemEventHandler()
        event_handler.on_created = self.on_created

        observer = Observer()
        observer.schedule(event_handler, self.watch_directory, recursive=False)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()

        observer.join()

if __name__ == "__main__":
    watch_directory = "../../MT940Files"

    file_watcher = FileWatcher(watch_directory)
    file_watcher.start()
