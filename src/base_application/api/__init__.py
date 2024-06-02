from src.base_application.api.database.dataBaseConnectionPyMongo import get_database, get_collection, get_flask_app, get_connection_postgre, get_connection_postgre_user

# Create a Flask application instance
app = get_flask_app()
# Get the MongoDB 'Transactions' collection
transactions_collection = get_collection()
# Establish a connection to the PostgreSQL database for admin
postgre_connection = get_connection_postgre()
# Placeholder for establishing a connection to the PostgreSQL database for a user (currently returns None)
postgre_connection_user = get_connection_postgre_user()

from src.base_application.api import APIConnect