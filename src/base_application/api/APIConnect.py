import json
import xml.etree.ElementTree as ET
import xml.dom.minidom
from datetime import datetime
from json import JSONDecodeError

import psycopg2
from flask import jsonify, request, make_response, Flask, Response
from json2xml import json2xml
from bson import json_util, ObjectId
from bson.json_util import dumps as json_util_dumps

# Get instances of Flask App and MongoDB collection from dataBaseConnectionPyMongo file
from src.base_application.api import app, transactions_collection, postgre_connection, postgre_connection_user
from src.base_application.api.api_utils import validate_json, validate_member_json, validate_association_json, \
    validate_xml

def to_xml(data):
    """Converts dictionary data to an XML string."""
    xml_data = json2xml.Json2xml(data).to_xml()
    return xml_data

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
            }
        }
    }
    return make_response(jsonify(answer), 200)


@app.after_request
def add_headers(response):
    # Add whatever headers you want here, for example:
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # You can also set CORS headers if your API is accessed from different origins
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, OPTIONS, PATCH, POST, PUT'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    # Return the modified response
    return response


@app.route("/api/test")
def test_api():
    return jsonify("API works fine!")


@app.route("/api/transactions/count", methods=["GET"])
def get_transactions_count():
    count = transactions_collection.count_documents({})
    response_data = {"transactionsCount": count}
    if request.headers.get('Accept') == 'application/xml':
        xml_response = to_xml(response_data)
        return Response(xml_response, mimetype='application/xml')
    return jsonify(response_data)


@app.route("/api/transactions", methods=["GET"])
def get_all_transactions():
    transactions_cursor = transactions_collection.find()
    transactions_list = list(transactions_cursor)
    if request.headers.get('Accept') == 'application/xml':
        xml_response = to_xml(transactions_list)
        return Response(xml_response, mimetype='application/xml')
    return Response(response=json_util.dumps(transactions_list), status=200, mimetype='application/json')


@app.route("/api/transactions/sql", methods=["GET"])
def get_transactions_sql():
    try:
        cursor = postgre_connection.cursor()
        cursor.execute('SELECT * FROM select_all_transaction()')
        data = cursor.fetchall()
        cursor.close()  # Close cursor
        postgre_connection.commit()  # Commit to ensure the transaction is not left open

        if request.headers.get('Accept') == 'application/xml':
            xml_response = to_xml(data)
            return Response(xml_response, mimetype='application/xml')

        return jsonify(data)
    except psycopg2.InterfaceError as error:
        postgre_connection.rollback()  # Rollback in case of error
        error_message = str(error)
        return jsonify({'error': error_message}), 500


@app.route("/api/transactions", methods=["POST"])
def create_transaction():
    json_data = request.get_json()
    transactions_collection.insert_one(json_data)

    response_data = {'message': 'Transaction created successfully'}

    if request.headers.get('Accept') == 'application/xml':
        xml_response = json2xml.Json2xml(response_data).to_xml()
        return Response(xml_response, mimetype='application/xml', status=201)

    return jsonify(response_data), 201


@app.route("/api/transactions", methods=["PUT"])
def update_transaction():
    try:
        cursor = postgre_connection.cursor()
        # Get data from a POST request
        transactionID = request.form.get('trans_id')
        description = request.form.get('desc')
        categoryID = request.form.get('category')
        memberID = request.form.get('member')

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

        response_data = {'message': 'Transaction Updated'}

        if request.headers.get('Accept') == 'application/xml':
            xml_response = json2xml.Json2xml(response_data).to_xml()
            return Response(xml_response, mimetype='application/xml', status=200)

        return jsonify(response_data), 200

    except psycopg2.InterfaceError as error:
        error_message = str(error)
        response_data = {'error': error_message}

        if request.headers.get('Accept') == 'application/xml':
            xml_response = json2xml.Json2xml(response_data).to_xml()
            return Response(xml_response, mimetype='application/xml', status=500)

        return jsonify(response_data), 500


@app.route("/api/transactions/filter", methods=["GET"])
def filter_transactions():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = {}

    if start_date and end_date:
        query["transactions.date"] = {"$gte": start_date, "$lte": end_date}

    try:
        transactions_cursor = transactions_collection.find(query)
        transactions_list = list(transactions_cursor)

        if request.headers.get('Accept') == 'application/xml':
            xml_response = json2xml.Json2xml(transactions_list).to_xml()
            return Response(
                response=xml_response,
                status=200,
                mimetype='application/xml'
            )

        return Response(
            response=json_util.dumps(transactions_list),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        print("Error retrieving or serializing transactions:", e)
        error_response = {"error": "Internal Server Error"}

        if request.headers.get('Accept') == 'application/xml':
            xml_response = json2xml.Json2xml(error_response).to_xml()
            return Response(
                response=xml_response,
                status=500,
                mimetype='application/xml'
            )

        return Response(
            response=json_util.dumps(error_response),
            status=500,
            mimetype='application/json'
        )


@app.route("/api/transactions/search/<keyword>", methods=["GET"])
def search_transactions(keyword):
    try:
        cursor = postgre_connection.cursor()

        # Call the search_table2 function with a search term
        cursor.execute("SELECT * FROM search_table2(%s)", (keyword,))

        # Fetch the results from the function call
        results = cursor.fetchall()
        response_data = results

        if request.headers.get('Accept') == 'application/xml':
            xml_response = json2xml.Json2xml(response_data).to_xml()
            return Response(
                response=xml_response,
                status=200,
                mimetype='application/xml'
            )

        return jsonify(response_data)

    except (Exception, psycopg2.DatabaseError) as error:
        error_message = str(error)
        response_data = {'message': error_message}

        if request.headers.get('Accept') == 'application/xml':
            xml_response = json2xml.Json2xml(response_data).to_xml()
            return Response(
                response=xml_response,
                status=500,
                mimetype='application/xml'
            )

        return jsonify(response_data), 500


@app.route("/api/files/upload", methods=["POST"])
def file_upload():
    file_data = request.json

    # Validate JSON
    if not validate_json(file_data):  # Assuming validate_json() checks the schema/format
        response_data = {'error': 'Invalid JSON format'}
        if request.headers.get('Accept') == 'application/xml':
            xml_response = json2xml.Json2xml(response_data).to_xml()
            return Response(
                response=xml_response,
                status=400,
                mimetype='application/xml'
            )
        return jsonify(response_data), 400

    transactions_collection.insert_one(file_data)
    response_data = {'message': 'File uploaded successfully'}

    if request.headers.get('Accept') == 'application/xml':
        xml_response = json2xml.Json2xml(response_data).to_xml()
        return Response(
            response=xml_response,
            status=201,
            mimetype='application/xml'
        )

    return jsonify(response_data), 201


@app.route("/api/files", methods=["GET"])
def get_file():
    try:
        # Fetch file metadata or contents from the database
        files_cursor = postgre_connection.cursor()
        files_cursor.execute("SELECT * FROM select_all_file()")  # Assuming a table `files` exists
        files = files_cursor.fetchall()

        # Prepare the response data
        response_data = files

        # Check the Accept header to determine the response format
        if request.headers.get('Accept') == 'application/xml':
            xml_response = json2xml.Json2xml(response_data).to_xml()
            return Response(
                response=xml_response,
                status=200,
                mimetype='application/xml'
            )

        # Default to JSON response
        return jsonify(response_data)

    except Exception as error:
        error_message = str(error)
        response_data = {'error': 'Internal Server Error'}

        # Check the Accept header to determine the response format
        if request.headers.get('Accept') == 'application/xml':
            xml_response = json2xml.Json2xml(response_data).to_xml()
            return Response(
                response=xml_response,
                status=500,
                mimetype='application/xml'
            )

        # Default to JSON response
        return jsonify(response_data), 500

@app.route("/api/associations", methods=["GET", "POST"])
def handle_associations():
    if request.method == "GET":
        # Fetch and return all associations
        cursor = postgre_connection.cursor()
        cursor.execute("SELECT * FROM select_all_association()")
        associations = cursor.fetchall()
        return jsonify(associations)
    elif request.method == "POST":
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

            return jsonify({'message': 'Association inserted successfully'}), 200
        except (Exception, psycopg2.DatabaseError) as error:
            error_message = str(error)
            return jsonify({'error': error_message})


@app.route("/api/members", methods=["GET", "POST"])
def get_members():
    if request.method == "GET":
        try:
            cursor = postgre_connection.cursor()
            # Call a stored procedure
            cursor.execute('SELECT * FROM select_all_member()')

            # Get all data from the stored procedure
            data = cursor.fetchall()
            response_data = data

            # Check the Accept header to determine the response format
            if request.headers.get('Accept') == 'application/xml':
                xml_response = json2xml.Json2xml(response_data).to_xml()
                return Response(
                    response=xml_response,
                    status=200,
                    mimetype='application/xml'
                )

            # Default to JSON response
            return jsonify(response_data)

        except psycopg2.InterfaceError as error:
            error_message = str(error)
            response_data = {'error': error_message}

            # Check the Accept header to determine the response format
            if request.headers.get('Accept') == 'application/xml':
                xml_response = json2xml.Json2xml(response_data).to_xml()
                return Response(
                    response=xml_response,
                    status=500,
                    mimetype='application/xml'
                )

            # Default to JSON response
            return jsonify(response_data), 500

    elif request.method == "POST":
        try:
            # Get the JSON data from the POST request
            json_data = request.get_json()

            # Validate with schema
            if not validate_member_json(json_data):
                response_data = {'Error': 'Error Occurred'}
                if request.headers.get('Accept') == 'application/xml':
                    xml_response = json2xml.Json2xml(response_data).to_xml()
                    return Response(
                        response=xml_response,
                        status=400,
                        mimetype='application/xml'
                    )
                return jsonify(response_data), 400

            name = json_data['name']
            email = json_data['email']

            cursor = postgre_connection.cursor()

            # Call a stored procedure
            cursor.execute('CALL insert_into_member(%s,%s)', (name, email))

            # Commit the transaction
            postgre_connection.commit()

            # Close the cursor
            cursor.close()

            response_data = {'message': 'Member saved successfully'}

            # Check the Accept header to determine the response format
            if request.headers.get('Accept') == 'application/xml':
                xml_response = json2xml.Json2xml(response_data).to_xml()
                return Response(
                    response=xml_response,
                    status=201,
                    mimetype='application/xml'
                )

            # Default to JSON response
            return jsonify(response_data), 201

        except (Exception, psycopg2.DatabaseError) as error:
            error_message = str(error)
            response_data = {'error': error_message}

            # Check the Accept header to determine the response format
            if request.headers.get('Accept') == 'application/xml':
                xml_response = json2xml.Json2xml(response_data).to_xml()
                return Response(
                    response=xml_response,
                    status=500,
                    mimetype='application/xml'
                )

            # Default to JSON response
            return jsonify(response_data), 500

        except JSONDecodeError as error:
            # Handle JSONDecodeError gracefully
            response_data = {'error': 'Invalid JSON format'}

            # Check the Accept header to determine the response format
            if request.headers.get('Accept') == 'application/xml':
                xml_response = json2xml.Json2xml(response_data).to_xml()
                return Response(
                    response=xml_response,
                    status=400,
                    mimetype='application/xml'
                )

            # Default to JSON response
            return jsonify(response_data), 400


@app.route("/api/members/<member_id>", methods=["DELETE"])
def delete_member(member_id):
    try:
        cursor = postgre_connection.cursor()

        # Call a stored procedure
        cursor.execute('CALL delete_member(%s)', (member_id,))

        # Commit the procedure
        postgre_connection.commit()

        # Close the cursor
        cursor.close()

        response_data = {'message': 'Member removed'}

        # Check the Accept header to determine the response format
        if request.headers.get('Accept') == 'application/xml':
            xml_response = json2xml.Json2xml(response_data).to_xml()
            return Response(
                response=xml_response,
                status=200,
                mimetype='application/xml'
            )

        # Default to JSON response
        return jsonify(response_data), 200

    except (Exception, psycopg2.DatabaseError) as error:
        error_message = str(error)
        response_data = {'message': error_message}

        # Check the Accept header to determine the response format
        if request.headers.get('Accept') == 'application/xml':
            xml_response = json2xml.Json2xml(response_data).to_xml()
            return Response(
                response=xml_response,
                status=500,
                mimetype='application/xml'
            )

        # Default to JSON response
        return jsonify(response_data), 500


@app.route("/api/categories", methods=["GET", "POST"])
def handle_categories():
    if request.method == "GET":
        try:
            cursor = postgre_connection.cursor()
            cursor.execute("SELECT * FROM category")
            categories = cursor.fetchall()
            cursor.close()
            response_data = categories

            # Check the Accept header to determine the response format
            if request.headers.get('Accept') == 'application/xml':
                xml_response = json2xml.Json2xml(response_data).to_xml()
                return Response(
                    response=xml_response,
                    status=200,
                    mimetype='application/xml'
                )

            # Default to JSON response
            return jsonify(response_data), 200

        except psycopg2.Error as e:
            response_data = {'error': 'Failed to fetch categories'}

            # Check the Accept header to determine the response format
            if request.headers.get('Accept') == 'application/xml':
                xml_response = json2xml.Json2xml(response_data).to_xml()
                return Response(
                    response=xml_response,
                    status=500,
                    mimetype='application/xml'
                )

            # Default to JSON response
            return jsonify(response_data), 500

    elif request.method == "POST":
        try:
            # Extract category name from the POST request
            data = request.get_json()
            category_name = data.get('name')

            # Validate category_name
            if not category_name:
                response_data = {'error': 'Category name is required'}
                if request.headers.get('Accept') == 'application/xml':
                    xml_response = json2xml.Json2xml(response_data).to_xml()
                    return Response(
                        response=xml_response,
                        status=400,
                        mimetype='application/xml'
                    )
                return jsonify(response_data), 400

            # Attempt to insert the category into the database
            cursor = postgre_connection.cursor()
            sql_insert_category = "INSERT INTO Category (name) VALUES (%s)"
            cursor.execute(sql_insert_category, (category_name,))
            postgre_connection.commit()
            cursor.close()

            # Return success message
            response_data = {'message': 'Category added successfully'}
            if request.headers.get('Accept') == 'application/xml':
                xml_response = json2xml.Json2xml(response_data).to_xml()
                return Response(
                    response=xml_response,
                    status=201,
                    mimetype='application/xml'
                )
            return jsonify(response_data), 201

        except psycopg2.Error as e:
            # Rollback the transaction in case of error
            postgre_connection.rollback()
            response_data = {'error': 'Failed to add category to the database'}
            if request.headers.get('Accept') == 'application/xml':
                xml_response = json2xml.Json2xml(response_data).to_xml()
                return Response(
                    response=xml_response,
                    status=500,
                    mimetype='application/xml'
                )
            return jsonify(response_data), 500

        except Exception as e:
            response_data = {'error': str(e)}
            if request.headers.get('Accept') == 'application/xml':
                xml_response = json2xml.Json2xml(response_data).to_xml()
                return Response(
                    response=xml_response,
                    status=500,
                    mimetype='application/xml'
                )
            return jsonify(response_data), 500

# Update the /api/downloads endpoint to filter transactions based on date and return the correct format
@app.route("/api/downloads", methods=["GET"])
def download_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = {}
    if start_date and end_date:
        query["transactions.date"] = {"$gte": start_date, "$lte": end_date}

    transactions_cursor = transactions_collection.find(query)
    transactions_list = list(transactions_cursor)

    if request.headers.get('Accept') == 'application/xml':
        json_data = json_util.dumps(transactions_list)
        data_dict = json.loads(json_data)
        xml_data = json2xml.Json2xml(data_dict).to_xml()
        response = make_response(xml_data)
        response.headers['Content-Type'] = 'application/xml'
        response.headers['Content-Disposition'] = 'attachment; filename=transactions.xml'
    else:
        json_data = json_util.dumps(transactions_list, indent=4)
        response = make_response(json_data)
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = 'attachment; filename=transactions.json'

    return response


@app.route("/api/transactions/join/<int:trans_id>", methods=["GET"])
def transaction_by_id_join(trans_id):
    try:
        cursor = postgre_connection.cursor()

        cursor.execute('select * from full_join_view where transactionid = %s', (int(trans_id),))

        data = cursor.fetchall()

        return jsonify(data)
    except psycopg2.InterfaceError as error:
        error_message = str(error)
        return jsonify({'error': error_message})


@app.route("/api/transactions/<int:trans_id>", methods=["GET", "POST", "PUT"])
def transaction_by_id(trans_id):
    if request.method == "GET":
        try:
            cursor = postgre_connection.cursor()
            cursor.execute('SELECT * FROM select_transaction_on_id(%s)', (int(trans_id),))
            data = cursor.fetchall()
            response_data = data

            if request.headers.get('Accept') == 'application/xml':
                xml_response = to_xml(response_data)
                return Response(
                    response=xml_response,
                    status=200,
                    mimetype='application/xml'
                )

            return jsonify(response_data)
        except psycopg2.InterfaceError as error:
            error_message = str(error)
            response_data = {'error': error_message}
            if request.headers.get('Accept') == 'application/xml':
                xml_response = to_xml(response_data)
                return Response(
                    response=xml_response,
                    status=500,
                    mimetype='application/xml'
                )
            return jsonify(response_data), 500

    elif request.method in ["POST", "PUT"]:
        try:
            # Get data from the request
            data = request.get_json()
            description = data.get('desc')
            categoryID = data.get('category')
            memberID = data.get('member')

            cursor = postgre_connection.cursor()

            # Handle None values
            categoryID = int(categoryID) if categoryID != "None" else None
            memberID = int(memberID) if memberID != "None" else None

            cursor.execute('CALL update_transaction(%s,%s,%s,%s)', (
                trans_id, description, categoryID, memberID))

            response_data = {'message': 'Transaction Updated'}
            if request.headers.get('Accept') == 'application/xml':
                xml_response = to_xml(response_data)
                return Response(
                    response=xml_response,
                    status=200,
                    mimetype='application/xml'
                )
            return jsonify(response_data)
        except psycopg2.InterfaceError as error:
            error_message = str(error)
            response_data = {'error': error_message}
            if request.headers.get('Accept') == 'application/xml':
                xml_response = to_xml(response_data)
                return Response(
                    response=xml_response,
                    status=500,
                    mimetype='application/xml'
                )
            return jsonify(response_data), 500

# we need
@app.route("/api/insertFile", methods=["POST"])
def insert_file():
    try:
        # Get the JSON file from the POST request
        json_transactions = request.get_json()

        # Validate JSON
        if not validate_json(json_transactions):
            response_data = {'Error': 'Validation failed'}
            if request.headers.get('Accept') == 'application/xml':
                xml_response = to_xml(response_data)
                return Response(
                    response=xml_response,
                    status=400,
                    mimetype='application/xml'
                )
            return jsonify(response_data), 400

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

        # Commit the transaction
        postgre_connection.commit()

        # Close the cursor
        cursor.close()

        response_data = {'message': 'File inserted successfully'}
        if request.headers.get('Accept') == 'application/xml':
            xml_response = to_xml(response_data)
            return Response(
                response=xml_response,
                status=201,
                mimetype='application/xml'
            )
        return jsonify(response_data), 201

    except (Exception, psycopg2.DatabaseError) as error:
        error_message = str(error)
        response_data = {'message': error_message}
        if request.headers.get('Accept') == 'application/xml':
            xml_response = to_xml(response_data)
            return Response(
                response=xml_response,
                status=500,
                mimetype='application/xml'
            )
        return jsonify(response_data), 500

# this we need
@app.route("/api/insertTransaction", methods=["POST"])
def insert_transaction():
    try:
        # Get the JSON file from the POST request
        json_trans = request.get_json()

        # Validate JSON
        if not validate_json(json_trans):
            response_data = {'Error': 'Validation failed'}
            if request.headers.get('Accept') == 'application/xml':
                xml_response = to_xml(response_data)
                return Response(
                    response=xml_response,
                    status=400,
                    mimetype='application/xml'
                )
            return jsonify(response_data), 400

        bank_reference = str(json_trans["transaction_reference"])

        cursor = postgre_connection.cursor()

        for trans_set in json_trans["transactions"]:
            amount = trans_set["amount"]["amount"]
            currency = trans_set["amount"]["currency"]
            transaction_date = trans_set["date"]
            transaction_details = str(trans_set["transaction_details"]).replace("/", "-")
            description = None
            typetransaction = trans_set["status"]

            cursor.execute('CALL insert_into_transaction(%s,%s,%s,%s,%s,%s,%s,%s,%s)', (
                bank_reference, transaction_details, description, amount, currency, transaction_date, None, None,
                typetransaction))
            # commit the transaction
            postgre_connection.commit()

        # close the cursor
        cursor.close()

        response_data = {'message': 'File inserted successfully'}
        if request.headers.get('Accept') == 'application/xml':
            xml_response = to_xml(response_data)
            return Response(
                response=xml_response,
                status=201,
                mimetype='application/xml'
            )
        return jsonify(response_data), 201

    except (Exception, psycopg2.DatabaseError) as error:
        error_message = str(error)
        response_data = {'error': error_message}
        if request.headers.get('Accept') == 'application/xml':
            xml_response = to_xml(response_data)
            return Response(
                response=xml_response,
                status=500,
                mimetype='application/xml'
            )
        return jsonify(response_data), 500
