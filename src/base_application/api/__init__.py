from src.base_application.api.database.dataBaseConnectionPyMongo import get_database, get_collection, get_flask_app, get_connection_postgre, get_connection_postgre_user

app = get_flask_app()
transactions_collection = get_collection()
postgre_connection = get_connection_postgre()
postgre_connection_user = get_connection_postgre_user()

from src.base_application.api import APIConnect