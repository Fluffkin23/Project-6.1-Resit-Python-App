import json
import xml.etree.ElementTree as ET
import xml.dom.minidom
import psycopg2
from flask import jsonify, request, make_response, Flask, Response
from json2xml import json2xml
from bson import json_util, ObjectId
from bson.json_util import dumps as json_util_dumps

from datetime import datetime
from flask import request, jsonify
from bson.json_util import dumps

# Get instances of Flask App and MongoDB collection from dataBaseConnectionPyMongo file
from src.base_application.api import app, transactions_collection, postgre_connection, postgre_connection_user
from src.base_application.api.api_utils import validate_json, validate_member_json, validate_association_json, \
    validate_xml


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
            "insertCategorySQL": "/api/insertCategory"
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


@app.route('/api/filterTransactions', methods=['POST'])
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











@app.route("/api/getTransactions", methods=["GET"])
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
@app.route("/api/deleteMember", methods=["DELETE"])
def delete_member():
    try:
        member_id = request.args.get('memberid')
        cursor = postgre_connection.cursor()

        # call a stored procedure
        cursor.execute('CALL delete_member(%s)', (member_id,))

        # commit the procedure
        postgre_connection.commit()

        # close the cursor
        cursor.close()

        return jsonify({'message': 'Member removed'})
    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({'message': str(error)})


# The function receives a hashed password
@app.route("/api/insertAssociation", methods=["POST"])
def insert_association():
    try:
        # Get the JSON file from the POST request
        json_data = json.loads(request.get_json())
        # Validate with schema
        # if not validate_association_json(json_data):
        #     print("Schema failed")
        # jsonify({'Error': 'Error Occured'})

        accountID = str(json_data['accountID'])
        name = str(json_data['name'])
        hashed_password = str(json_data['password'])

        cursor = postgre_connection.cursor()

        # call a stored procedure
        cursor.execute('CALL insert_into_association(%s,%s,%s)', (accountID, name, hashed_password))

        # commit the transaction
        postgre_connection.commit()

        # close the cursor
        cursor.close()

        return jsonify({'message': 'File inserted successfully'})
    except (Exception, psycopg2.DatabaseError) as error:
        error_message = str(error)
        return jsonify({'error': error_message})


@app.route("/api/insertMemberSQL", methods=["POST"])
def insert_member():
    try:
        # Get the JSON file from the POST request
        json_temp = request.get_json()
        json_data = json.loads(json_temp)
        # Validate with schema
        if not validate_member_json(json_data):
            jsonify({'Error': 'Error Occured'})

        name = json_data['name']
        email = json_data['email']

        cursor = postgre_connection.cursor()

        # call a stored procedure
        cursor.execute('CALL insert_into_member(%s,%s)', (name, email))

        # commit the transaction
        postgre_connection.commit()

        # close the cursor
        cursor.close()

        return jsonify({'message': 'Member saved successfully'})
    except (Exception, psycopg2.DatabaseError) as error:
        error_message = str(error)
        return jsonify({'error': error_message})


@app.route("/api/getAssociation", methods=["GET"])
def get_association():
    try:
        cursor = postgre_connection.cursor()

        # call a stored procedure
        cursor.execute('SELECT * FROM select_all_association()')

        # Get all data from the stored procedure
        data = cursor.fetchall()

        # Return data in JSON format
        return jsonify(data)
    except psycopg2.InterfaceError as error:
        error_message = str(error)
        return jsonify({'error': error_message})


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


@app.route("/api/getMembers", methods=["GET"])
def get_members():
    try:
        cursor = postgre_connection.cursor()

        # call a stored procedure
        cursor.execute('SELECT * FROM select_all_member()')

        # Get all data from the stored procedure
        data = cursor.fetchall()

        # Return data in JSON format
        return jsonify(data)
    except psycopg2.InterfaceError as error:
        error_message = str(error)
        return jsonify({'error': error_message})


@app.route("/api/getCategory", methods=["GET"])
def get_category():
    try:
        cursor = postgre_connection.cursor()

        # call a stored procedure
        cursor.execute('SELECT * FROM category')

        # Get all data from the stored procedure
        data = cursor.fetchall()

        # Return data in JSON format
        return jsonify(data)
    except psycopg2.InterfaceError as error:
        error_message = str(error)
        return jsonify({'error': error_message})



@app.route("/api/insert_category_into_database", methods=["POST"])
def insert_category_into_database(category_name):
    try:
        # Creating a cursor object using the cursor() method
        cursor = postgre_connection.cursor()
        # SQL statement for inserting a category into the Category table
        sql_insert_category = "INSERT INTO Category (name) VALUES (%s)"

        # Execute the SQL statement with the category name as parameter
        cursor.execute(sql_insert_category, (category_name,))

        # Commit the transaction
        postgre_connection.commit()

        # Return True to indicate successful insertion
        return True
    except psycopg2.Error as e:
        # Print the error message
        print("Error inserting category:", e)
        # Rollback the transaction in case of error
        postgre_connection.rollback()
        # Return False to indicate failure
        return False
    finally:
        # Close the cursor if it was successfully opened
        if cursor:
            cursor.close()
            print("PostgreSQL cursor is closed")

@app.route("/api/insertCategory", methods=["POST"])
def insert_category():
    try:
        # Get the category name from the POST request
        category_name = request.json.get('name')

        # Perform any necessary validation on the category_name

        # Insert the category into the database
        if insert_category_into_database(category_name):
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


@app.route("/api/updateTransaction", methods=["PUT"])
def update_transaction():
    try:
        cursor = postgre_connection.cursor()
        # Get data from a post request
        transactionID = request.form.get('trans_id')
        description = request.form.get('desc')
        categoryID = request.form.get('category')
        memberID = request.form.get('member')
        cursor = postgre_connection.cursor()

        if categoryID == "None":
            categoryID = None
        else:
            categoryID = int(categoryID)

        if memberID == "None":
            memberID = None
        else:
            memberID = int(memberID)

        cursor.execute('CALL update_transaction(%s,%s,%s,%s)', (
            transactionID, description, categoryID, memberID))

        return jsonify({'message': 'Transaction Updated'})
    except psycopg2.InterfaceError as error:
        error_message = str(error)
        return jsonify({'error': error_message})


@app.route("/api/getTransactionOnIdJoin/<trans_id>", methods=["GET"])
def get_transaction_on_id_join(trans_id):
    try:
        cursor = postgre_connection.cursor()

        cursor.execute('select * from full_join_view where transactionid = %s', (int(trans_id),))

        data = cursor.fetchall()

        return jsonify(data)
    except psycopg2.InterfaceError as error:
        error_message = str(error)
        return jsonify({'error': error_message})


@app.route("/api/searchKeyword/<keyword>", methods=["GET"])
def search_keyword(keyword):
    try:
        cursor = postgre_connection.cursor()

        # Call the search_table2 function with a search term
        cursor.execute("SELECT * FROM search_table2(%s)", (keyword,))

        # Fetch the results from the function call
        results = cursor.fetchall()
        return jsonify(results)
    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({'message': error})
