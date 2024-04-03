import json
import xml.etree.ElementTree as ET
import xml.dom.minidom
from datetime import datetime

import psycopg2
from flask import jsonify, request, make_response, Flask, Response
from json2xml import json2xml
from bson import json_util, ObjectId
from bson.json_util import dumps as json_util_dumps

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
            "transactions": {
                "count": "/api/transactions/count",
                "all": "/api/transactions",
                "filter": "/api/transactions/filter",
                "byDate": "/api/transactions/byDate",
                "search": "/api/transactions/search/<keyword>",
                "id": "/api/transactions/<int:trans_id>",
                "update": "/api/transactions/<int:trans_id>",
            },
            "files": {
                "upload": "/api/files/upload",
                "all": "/api/files",
            },
            "associations": "/api/associations",
            "members": {
                "all": "/api/members",
                "id": "/api/members/<member_id>",
            },
            "categories": {
                "all": "/api/categories",
                "create": "/api/categories"
            },
            "downloads": {
                "JSON": "/api/downloads/json",
                "XML": "/api/downloads/xml",
                "transactionsByDate": "/api/downloads/transactionsByDate"
            }
        }
    }
    return make_response(jsonify(answer), 200)


@app.route("/api/test")
def test_api():
    return jsonify("API works fine!")


@app.route("/api/transactions/count", methods=["GET"])
def get_transactions_count():
    count = transactions_collection.count_documents({})
    return jsonify({"transactionsCount": count})


@app.route("/api/transactions", methods=["GET"])
def get_all_transactions():
    transactions_cursor = transactions_collection.find()
    transactions_list = list(transactions_cursor)
    return Response(response=json_util.dumps(transactions_list), status=200, mimetype='application/json')

@app.route("/api/transactions/sql", methods=["GET"])
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



@app.route("/api/transactions", methods=["POST"])
def create_transaction():
    json_data = request.get_json()
    transactions_collection.insert_one(json_data)
    return jsonify({'message': 'Transaction created successfully'})


@app.route("/api/transactions/filter", methods=["POST"])
def filter_transactions():
    data = request.get_json()
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')

    if not (start_date_str and end_date_str):
        return jsonify({'error': 'start_date and end_date are required'}), 400

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

        transactions_cursor = transactions_collection.find({
            "date": {
                "$gte": start_date,
                "$lte": end_date
            }
        })

        transactions = list(transactions_cursor)
        return jsonify(transactions)

    except ValueError as e:
        return jsonify({'error': 'Invalid date format'}), 400


@app.route("/api/transactions/byDate", methods=["GET"])
def download_transactions_by_date():
    date_str = request.args.get('date')

    if not date_str:
        return jsonify({'error': 'Date parameter is required'}), 400

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        transactions_cursor = transactions_collection.find({
            "date": date
        })
        transactions = list(transactions_cursor)

        return Response(
            response=json_util.dumps(transactions),
            status=200,
            mimetype='application/json'
        )

    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400


@app.route("/api/transactions/search/<keyword>", methods=["GET"])
def search_transactions(keyword):
    try:
        cursor = postgre_connection.cursor()

        # Call the search_table2 function with a search term
        cursor.execute("SELECT * FROM search_table2(%s)", (keyword,))

        # Fetch the results from the function call
        results = cursor.fetchall()
        return jsonify(results)
    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({'message': error})


# @app.route("/api/searchKeyword/<keyword>", methods=["GET"])
# def search_keyword(keyword):
#     transactions_cursor = transactions_collection.find({
#         "$text": {
#             "$search": keyword
#         }
#     })
#     transactions = list(transactions_cursor)
#     return Response(
#         response=json_util.dumps(transactions),
#         status=200,
#         mimetype='application/json'
#     )


@app.route("/api/files/upload", methods=["POST"])
def file_upload():
    file_data = request.json
    # Assuming the presence of a validation function and MongoDB insert
    # Validate JSON
    if not validate_json(file_data):  # Assuming validate_json() checks the schema/format
        return jsonify({'error': 'Invalid JSON format'}), 400

    transactions_collection.insert_one(file_data)
    return jsonify({'message': 'File uploaded successfully'})


@app.route("/api/files", methods=["GET"])
def get_file():
    # This would typically fetch file metadata or contents from a database
    # For simplicity, assuming a function fetch_file_data() fetches file info
    files_cursor = postgre_connection.cursor()
    files_cursor.execute("SELECT * FROM select_all_file()")  # Assuming a table `files` exists
    files = files_cursor.fetchall()
    return jsonify(files)


@app.route("/api/associations", methods=["GET", "POST"])
def handle_associations():
    if request.method == "GET":
        # Fetch and return all associations
        cursor = postgre_connection.cursor()
        cursor.execute("SELECT * FROM select_all_association()")
        associations = cursor.fetchall()
        return jsonify(associations)
    elif request.method == "POST":
        # Create a new association
        data = request.get_json()
        if not validate_association_json(data):  # Assuming this validation function exists
            return jsonify({'error': 'Invalid association data'}), 400
        try:
            cursor = postgre_connection.cursor()
            cursor.execute("INSERT INTO associations (name, other_fields) VALUES (%s, %s) RETURNING id",
                           (data['name'], data['other_fields']))
            new_id = cursor.fetchone()[0]
            postgre_connection.commit()
            return jsonify({'message': 'Association created successfully', 'id': new_id}), 201
        except psycopg2.Error as e:
            return jsonify({'error': str(e)}), 500


@app.route("/api/members", methods=["GET"])
def get_members():
    cursor = postgre_connection.cursor()
    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()
    return jsonify(members)


@app.route("/api/members/<member_id>", methods=["DELETE"])
def delete_member(member_id):
    # Assuming function to delete member based on member_id
    cursor = postgre_connection.cursor()
    cursor.execute("DELETE FROM members WHERE id = %s RETURNING *", (member_id,))
    deleted_member = cursor.fetchone()
    postgre_connection.commit()

    if deleted_member:
        return jsonify({'message': 'Member deleted successfully'}), 200
    else:
        return jsonify({'error': 'Member not found'}), 404


@app.route("/api/categories", methods=["GET", "POST"])
def handle_categories():
    if request.method == "GET":
        cursor = postgre_connection.cursor()
        cursor.execute("SELECT * FROM categories")
        categories = cursor.fetchall()
        return jsonify(categories)
    elif request.method == "POST":
        data = request.get_json()
        # Validate data if needed
        try:
            cursor = postgre_connection.cursor()
            cursor.execute("INSERT INTO categories (name) VALUES (%s) RETURNING id", (data['name'],))
            category_id = cursor.fetchone()[0]
            postgre_connection.commit()
            return jsonify({'message': 'Category created successfully', 'id': category_id}), 201
        except psycopg2.Error as e:
            return jsonify({'error': str(e)}), 500


@app.route("/api/downloads/json", methods=["GET"])
def download_json():
    transactions_cursor = transactions_collection.find()
    transactions_list = list(transactions_cursor)
    json_data = json_util.dumps(transactions_list, indent=4)
    response = make_response(json_data)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = 'attachment; filename=transactions.json'
    return response


@app.route("/api/downloads/xml", methods=["GET"])
def download_xml():
    transactions_cursor = transactions_collection.find()
    transactions_list = list(transactions_cursor)
    json_data = json_util.dumps(transactions_list)
    data_dict = json.loads(json_data)
    xml_data = json2xml.Json2xml(data_dict).to_xml()
    response = make_response(xml_data)
    response.headers["Content-Type"] = "application/xml"
    response.headers["Content-Disposition"] = 'attachment; filename=transactions.xml'
    return response


@app.route("/api/transactions/<int:trans_id>", methods=["GET", "PUT"])
def transaction_by_id(trans_id):
    if request.method == "GET":
        transaction = transactions_collection.find_one({"_id": trans_id})
        if transaction:
            return Response(
                response=json_util.dumps(transaction),
                status=200,
                mimetype='application/json'
            )
        else:
            return jsonify({'error': 'Transaction not found'}), 404
    elif request.method == "PUT":
        updated_data = request.json
        result = transactions_collection.update_one({"_id": trans_id}, {"$set": updated_data})
        if result.matched_count:
            return jsonify({'message': 'Transaction updated successfully'}), 200
        else:
            return jsonify({'error': 'Transaction not found'}), 404


# Send a POST request with the file path to this function

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
