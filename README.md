# Project-6.1 Sports Accounting
### By NHL Stenden Student Team IT3K for Quintor

<h3> Description </h3>
A small desktop application that allows sports assocations to keep track and manage their finances. Sports Accounting is capable of reading MT-940 bank files (.sta) to save and manipulate bank trsanction data locally. The application features a NoSQL MongoDB database for archival storage of the files as well as a PostgreSQL database for manipulating the transactions. 
Sport assocation owners can link transactions to a Bar category or to one of the registered assocation Members.
The application was built with Python and TKinter utilizing Flask to create the API responsible for connecting the app to the two databases.


## Prerequisites

Before you begin, ensure that you have the following software installed on your system:

- **PgAdmin (Version 4.7 or higher):** Necessary for importing the database. [Download PgAdmin](https://www.pgadmin.org/download/)
- **PostgreSQL (Version 15.6 or higher):** Required for database management. [Download PostgreSQL](https://www.postgresql.org/download/)

## Database Setup

To import the application database using PgAdmin, follow these steps:

### Create a New Database:

1. Open PgAdmin and connect to your PostgreSQL server.
2. Right-click on the `Databases` node, select `Create`, and then `Database`.
3. Name the new database `Quintor` and click `Save`.

### Import Database:

1. Right-click on the `Quintor` database, select `Restore`.
2. In the dialog, choose the `Quintor.tar` file located in the project's resources folder.
3. Click `Restore` to import the database.

## Database Configuration

### MongoDB Connection Setup:

1. Navigate to `src > base application > api > database > databaseConnectionPyMongo`.
2. In the `get_database()` function, you will find an existing `CONNECTION_STRING`. 
3. If the default `CONNECTION_STRING` does not work, replace it with your own MongoDB connection string.

### PostgreSQL Connection Setup:

1. In the same directory, locate the `get_connection_postgre` function.
2. For the `password` field within this function, enter your own PgAdmin password to establish the connection.

## Application Setup in PyCharm

Ensure you have PyCharm 2023.3.4 or a compatible version installed to run the application. Follow the steps below to set up the application in PyCharm:

### Extract the Project Folder:

- Locate and extract the zip file containing the project to your desired location.

### Open Project in PyCharm:

1. Open PyCharm and select `Open`.
2. Navigate to and select the extracted project folder (e.g., `Project-6.1-Resit-Python-App`) and open it.

### Wait for Project Indexing:

- Allow PyCharm a moment to index the project files. This process ensures that the IDE properly recognizes project structure and dependencies.

### Configure Python Interpreter:

- Upon opening the project, a prompt may appear asking you to set up the Python interpreter. Choose a Python version of at least 3.6.
- If not prompted, you can manually configure the interpreter via `File > Settings > Project > Python Interpreter`.

### Install Dependencies:

- Open the terminal within PyCharm and execute the following command to install the project's dependencies: `pip install -r requirements.txt`.

### Running the Application:

1. To start the application, run `main.py` to initialize the API server.
2. Next, execute `parser.py`, followed by `launcher.py` to launch the GUI.

### Creating a New Account:

- On the GUI, create a new account by entering a Name, Password, and an IBAN Account.

### Admin Login:

- Log in as an admin by clicking "Login Admin" and entering the previously set password.

### Parsing MT940 Files:

- Copy and paste the MT940 files from the `resources` folder to the `MT940` folder within the project directory.
- After uploading a file, click the "Update" button in the GUI to display the new modifications.

This completes the setup guide for the application. Follow these instructions carefully to ensure a smooth setup and operation of the application. For further assistance or queries, please  contact the  team.

<h3> Authors </h3>
    
* Alin Costache
* Terry Ioannou
* Kaiser Aftab
* David Hlaváček
* Abu Hasib Shanewaz
* Nathan Pais D'Costa



