import json
import xml.etree.ElementTree as ET
import xml.dom.minidom
import psycopg2
from flask import jsonify, request, make_response, Flask, Response
from json2xml import json2xml
from bson import json_util, ObjectId
from bson.json_util import dumps as json_util_dumps
import requests
from datetime import datetime
from flask import request, jsonify
from bson.json_util import dumps

# Get instances of Flask App and MongoDB collection from dataBaseConnectionPyMongo file
from src.base_application.api import app, transactions_collection, postgre_connection, postgre_connection_user
from src.base_application.api.api_utils import validate_json, validate_member_json, validate_association_json, \
    validate_xml

# Ensure transactions_collection is properly initialized
try:
    transactions_cursor = transactions_collection.find().limit(5)
    transactions_list = list(transactions_cursor)
except Exception as e:
    print("Error initializing transactions_collection:", e)


@app.route("/")
def index():
    answer = {
        "message": "Welcome to Sports Accounting API",
        "api": {
            "test": "/api/test",
            "getTransactionsAmount": "/api/getTransactionsCount",
            "getTransactions": "/api/getTransactions",
            "uploadMT940File": "/api/uploadFile",
            "downloadJSON": "/api/downloadJSON",
            "downloadXML": "/api/downloadXML",
            "searchKeywordSQL": "/api/searchKeyword/<keyword>",
            "insertAssociationSQL": "/api/insertAssociation",
            "insertFileSQL": "/api/insertFile",
            "insertTransactionSQL": "/api/insertTransaction",
            "insertMemberSQL": "/api/insertMemberSQL/<name>/<email>",
            "updateTransactionSQL": "/api/updateTransactionSQL/<transaction_id>",
            "deleteMemberSQL": "/api/deleteMember",
            "getAssociationSQL": "/api/getAssociation",
            "insertCategorySQL": "/api/insertCategory",
            "getFilesSQL": "/api/getFile",
            "transactions": "/api/transactions",
            "downloadTransactionsByDate": "/api/downloadTransactionsByDate",
            "transactions/filter": "/api/transactions/filter",
            "associations": "/api/associations",
            "members": "/api/members",
            "getCategory": "/api/getCategory",
            "categories": "/api/categories",
            "transactions/<int:trans_id>": "/api/transactions/<int:trans_id>",
            "transactions/search/<keyword>": "/api/transactions/search/<keyword>",
            "members/<member_id>": "/api/members/<member_id>"
        }
    }
    return make_response(jsonify(answer), 200)


# ----------------------- No SQL MongoDB functions of the API ---------------------------------


@app.route("/api/test")
def test():
    return make_response(jsonify("API works fine!"))


@app.route("/api/getTransactionsCount", methods=["GET"])
def get_transactions_count():
    output = {"transactionsCount": transactions_collection.count_documents({})}
    return output




@app.route("/api/downloadJSON", methods=["GET"])
def downloadJSON():
    with app.app_context():
        # Get the data from the database
        try:
            data = get_all_transactions()
        except TypeError:
            data = []

        # Create a response object
        json_data = json_util.dumps(data, indent=4)

        response = make_response(json_data)
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = 'attachment; filename=data.json'
    return response


@app.route("/api/downloadXML", methods=["GET"])
def downloadXML():
    # Get the data from the database
    try:
        data = get_all_transactions()
    except TypeError:
        data = []

    # Convert the data to a JSON string
    # json_data = json.dumps(data)
    json_data = json_util.dumps(data, indent=4)
    # Convert the JSON data to an ElementTree
    xml_root = ET.fromstring(json2xml.Json2xml(json.loads(json_data)).to_xml())
    xml_str = ET.tostring(xml_root, encoding='utf-8', method='xml')

    # Validate XML
    if not validate_xml(xml_str):
        print('Validation failed')

    # Create the Flask response object with XML data
    response = make_response(xml_str)
    response.headers["Content-Type"] = "application/xml"
    response.headers["Content-Disposition"] = "attachment; filename=data.xml"
    return response


@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    # Here you should replace the following line with the actual call to your database or API
    response = requests.get("your_api_server_ip_here" + "/api/getTransactions")
    response.raise_for_status()
    return jsonify(response.json())

@app.route('/api/transactions/filter', methods=['POST'])
def filter_transactions():
    # Extract start and end dates from the request
    data = request.get_json()
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')

    if not (start_date_str and end_date_str):
        return jsonify({'error': 'start_date and end_date are required'}), 400

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

        # Here you should replace the following line with the actual call to your database or API
        response = requests.get("your_api_server_ip_here" + "/api/getTransactions")
        response.raise_for_status()
        documents = response.json()

        filtered_documents = []
        for document in documents:
            new_document = document.copy()
            new_document['transactions'] = []

            for transaction in document['transactions']:
                transaction_date = datetime.strptime(transaction['entry_date'], "%Y-%m-%d").date()
                if start_date <= transaction_date <= end_date:
                    new_document['transactions'].append(transaction)

            if new_document['transactions']:
                filtered_documents.append(new_document)

        return jsonify(filtered_documents)

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except requests.exceptions.HTTPError as e:
        return jsonify({'error': 'HTTP error from external API'}), 500
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred'}), 500



@app.route('/api/downloadTransactionsByDate', methods=['GET'])
def download_transactions_by_date():
    # Extract the specific date from query parameters
    date_str = request.args.get('date')

    if not date_str:
        return jsonify({'error': 'Date parameter is required'}), 400

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        filtered_transactions = filter_transactions(date)

        # Convert the filtered transactions to JSON format
        formatted_json = json.dumps(filtered_transactions, indent=4, default=str)  # Ensure datetime objects are serialized properly

        # Create a response with the JSON data
        response = Response(formatted_json, mimetype='application/json')
        response.headers['Content-Disposition'] = 'attachment; filename=filtered_transactions.json'
        return response

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred'}), 500











# GET all transactions
@app.route("/api/transactions", methods=["GET"])
def get_all_transactions():
    try:
        transactions_cursor = transactions_collection.find()
        transactions_list = list(transactions_cursor)
        return Response(
            response=json_util.dumps(transactions_list),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        print("Error retrieving or serializing transactions:", e)
        return Response(
            response=json_util.dumps({"error": "Internal Server Error"}),
            status=500,
            mimetype='application/json'
        )




# POST a new transaction
@app.route("/api/transactions", methods=["POST"])
def create_transaction():
    try:
        # Get the JSON data from the request
        json_data = request.get_json()

        # Insert into NoSQL DB
        transactions_collection.insert_one(json_data)

        return jsonify({'message': 'Transaction created successfully'})
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred'})


# Send a POST request with the file path to this function
@app.route("/api/uploadFile", methods=["POST"])
def file_upload():
    # Get the JSON file from the POST request
    json_data = request.get_json()

    # Validate JSON
    if not validate_json(json_data):
        jsonify({'Error': 'Error Occured'})

    # Insert into No SQL Db
    transactions_collection.insert_one(json_data)

    return make_response(jsonify(status="File uploaded!"), 200)


# -------------------------- SQL PostGreSQL DB functions of the API ---------------------------
# DELETE a member
@app.route("/api/members/<member_id>", methods=["DELETE"])
def delete_member(member_id):
    try:
        cursor = postgre_connection.cursor()
        cursor.execute('CALL delete_member(%s)', (member_id,))
        postgre_connection.commit()
        cursor.close()
        return jsonify({'message': 'Member removed'})
    except Exception as e:
        return jsonify({'error': str(e)})


# The function receives a hashed password


# POST a new association
@app.route("/api/associations", methods=["POST"])
def create_association():
    try:
        json_data = request.get_json()
        accountID = str(json_data['accountID'])
        name = str(json_data['name'])
        hashed_password = str(json_data['password'])
        cursor = postgre_connection.cursor()
        cursor.execute('CALL insert_into_association(%s,%s,%s)', (accountID, name, hashed_password))
        postgre_connection.commit()
        cursor.close()
        return jsonify({'message': 'Association created successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

# POST a new member
# POST a new member
@app.route("/api/members", methods=["POST"])
def create_member():
    try:
        json_data = request.get_json()
        name = json_data['name']
        email = json_data['email']
        cursor = postgre_connection.cursor()
        cursor.execute('CALL insert_into_member(%s,%s)', (name, email))
        postgre_connection.commit()
        cursor.close()
        return jsonify({'message': 'Member saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route("/api/associations", methods=["GET", "POST"])
def handle_associations():
    if request.method == "GET":
        try:
            cursor = postgre_connection.cursor()
            cursor.execute('SELECT * FROM select_all_association()')
            data = cursor.fetchall()
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)})
    elif request.method == "POST":
        try:
            json_data = request.get_json()
            # Validate JSON and insert into database
            return jsonify({'message': 'Association created successfully'})
        except Exception as e:
            return jsonify({'error': str(e)})



#handling transactions in NoSQL and SQL databases
@app.route("/api/transactions", methods=["GET"])
def handle_transactions():
    if request.method == "GET":
        try:
            cursor = postgre_connection.cursor()
            cursor.execute('SELECT * FROM select_all_transaction()')
            data = cursor.fetchall()
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)})
    elif request.method == "POST":
        try:
            json_data = request.get_json()
            # Validate JSON and insert into database
            return jsonify({'message': 'Transaction created successfully'})
        except Exception as e:
            return jsonify({'error': str(e)})


@app.route("/api/insertTransaction", methods=["POST"])
def insert_transaction():
    try:
        # Get the JSON file from the POST request
        json_trans = request.get_json()

        # Validate JSON
        if not validate_json(json_trans):
            print("Validation failed")
            return jsonify({'Error': 'Error Occured'})

        bank_reference = str(json_trans["transaction_reference"])

        cursor = postgre_connection.cursor()

        for trans_set in json_trans["transactions"]:
            amount = trans_set["amount"]["amount"]
            currency = trans_set["amount"]["currency"]
            transaction_date = trans_set["date"]
            transaction_details = str(trans_set["transaction_details"])
            transaction_details = transaction_details.replace("/", "-")
            description = None
            typetransaction = trans_set["status"]

            cursor.execute('CALL insert_into_transaction(%s,%s,%s,%s,%s,%s,%s,%s,%s)', (
                bank_reference, transaction_details, description, amount, currency, transaction_date, None, None,
                typetransaction))
            # commit the transaction
            postgre_connection.commit()

        # close the cursor
        cursor.close()

        return jsonify({'message': 'File inserted successfully'})
    except (Exception, psycopg2.DatabaseError) as error:
        error_message = str(error)
        return jsonify({'error': error_message})


@app.route("/api/insertFile", methods=["POST"])
def insert_file():
    try:
        # Get the JSON file from the POST request
        json_transactions = request.get_json()

        # Validate JSON
        if not validate_json(json_transactions):
            print("Validation failed")
            return jsonify({'Error': 'Error Occured'})

        # Extract values from a JSON into variables for the File table
        reference_number = str(json_transactions["transaction_reference"])
        statement_number = str(json_transactions["statement_number"])
        sequence_detail = str(json_transactions["sequence_number"])
        available_balance = json_transactions["available_balance"]["amount"]["amount"]
        forward_available_balance = json_transactions["forward_available_balance"]["amount"]["amount"]
        account_identification = str(json_transactions["account_identification"])

        cursor = postgre_connection.cursor()

        # Call a stored procedure
        cursor.execute('CALL insert_into_file(%s,%s,%s,%s,%s,%s)', (
            reference_number, statement_number, sequence_detail, available_balance, forward_available_balance,
            account_identification))

        # commit the transaction
        postgre_connection.commit()

        # close the cursor
        cursor.close()

        return jsonify({'message': 'File inserted successfully'})
    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({'message': error})


@app.route("/api/getTransactionsSQL", methods=["GET"])
def get_transactions_sql():
    try:
        cursor = postgre_connection.cursor()

        # call a stored procedure
        cursor.execute('SELECT * FROM select_all_transaction()')

        # Get all data from the stored procedure
        data = cursor.fetchall()

        # Return data in JSON format
        return jsonify(data)
    except psycopg2.InterfaceError as error:
        error_message = str(error)
        return jsonify({'error': error_message})


# Balance is [4]
@app.route("/api/getFile", methods=["GET"])
def get_file():
    try:
        cursor = postgre_connection.cursor()

        # call a stored procedure
        cursor.execute('SELECT * FROM select_all_file()')

        # Get all data from the stored procedure
        data = cursor.fetchall()

        # Return data in JSON format
        return jsonify(data)
    except psycopg2.InterfaceError as error:
        error_message = str(error)
        return jsonify({'error': error_message})


@app.route("/api/members", methods=["GET"])
def get_members():
    try:
        cursor = postgre_connection.cursor()
        cursor.execute('SELECT * FROM select_all_member()')
        data = cursor.fetchall()
        return jsonify(data)
    except psycopg2.InterfaceError as error:
        return jsonify({'error': str(error)}), 500


@app.route("/api/getCategory", methods=["GET"])
def get_categories():
    try:
        cursor = postgre_connection.cursor()
        cursor.execute('SELECT * FROM category')
        data = cursor.fetchall()
        return jsonify(data)
    except psycopg2.InterfaceError as error:
        return jsonify({'error': str(error)}), 500



@app.route("/api/categories", methods=["POST"])
def create_category():
    try:
        category_name = request.json.get('name')
        if not category_name:
            return jsonify({'error': 'Category name is required'}), 400

        cursor = postgre_connection.cursor()
        cursor.execute('INSERT INTO Category (name) VALUES (%s)', (category_name,))
        postgre_connection.commit()
        return jsonify({'message': 'Category added successfully'}), 201
    except psycopg2.Error as error:
        return jsonify({'error': str(error)}), 500

@app.route("/api/insertCategory", methods=["POST"])
def insert_category():
    try:
        # Get the category name from the POST request
        category_name = request.json.get('name')

        # Perform any necessary validation on the category_name

        # Insert the category into the database
        if create_category(category_name):
            # Return a success message
            return jsonify({'message': 'Category added successfully'}), 201
        else:
            return jsonify({'error': 'Failed to add category to the database'}), 500
    except Exception as e:
        # Return an error message if something goes wrong
        return jsonify({'error': str(e)}), 500



@app.route("/api/getTransactionOnId/<trans_id>", methods=["GET"])
def get_transaction_on_id(trans_id):
    try:
        cursor = postgre_connection.cursor()

        cursor.execute('SELECT * FROM select_transaction_on_id(%s)', (int(trans_id),))

        data = cursor.fetchall()

        return jsonify(data)
    except psycopg2.InterfaceError as error:
        error_message = str(error)
        return jsonify({'error': error_message})


@app.route("/api/transactions/<int:trans_id>", methods=["GET"])
def get_transaction_by_id(trans_id):
    try:
        cursor = postgre_connection.cursor()
        cursor.execute('SELECT * FROM select_transaction_on_id(%s)', (trans_id,))
        data = cursor.fetchall()
        return jsonify(data)
    except psycopg2.InterfaceError as error:
        return jsonify({'error': str(error)}), 500


@app.route("/api/transactions/<int:trans_id>", methods=["PUT"])
def update_transaction(trans_id):
    try:
        description = request.json.get('description')
        category_id = request.json.get('category_id')
        member_id = request.json.get('member_id')

        cursor = postgre_connection.cursor()
        cursor.execute('CALL update_transaction(%s,%s,%s,%s)', (trans_id, description, category_id, member_id))
        return jsonify({'message': 'Transaction Updated'})
    except psycopg2.InterfaceError as error:
        return jsonify({'error': str(error)}), 500


@app.route("/api/transactions/search/<keyword>", methods=["GET"])
def search_transactions(keyword):
    try:
        cursor = postgre_connection.cursor()
        cursor.execute("SELECT * FROM search_table2(%s)", (keyword,))
        results = cursor.fetchall()
        return jsonify(results)
    except psycopg2.DatabaseError as error:
        return jsonify({'error': str(error)}), 500
