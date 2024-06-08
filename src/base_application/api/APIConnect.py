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
    """
       This endpoint returns the count of transactions in the database.
       If the request's 'Accept' header is 'application/xml', the response is in XML format, otherwise, it is in JSON format.
   """
    count = transactions_collection.count_documents({})
    response_data = {"transactionsCount": count}
    if request.headers.get('Accept') == 'application/xml':
        xml_response = to_xml(response_data)
        return Response(xml_response, mimetype='application/xml')
    return jsonify(response_data)


@app.route("/api/transactions", methods=["GET"])
def get_all_transactions():
    """
        This endpoint retrieves all transactions from the database.
        If the request's 'Accept' header is 'application/xml', the response is in XML format, otherwise, it is in JSON format.
    """
    transactions_cursor = transactions_collection.find()
    transactions_list = list(transactions_cursor)
    if request.headers.get('Accept') == 'application/xml':
        xml_response = to_xml(transactions_list)
        return Response(xml_response, mimetype='application/xml')
    return Response(response=json_util.dumps(transactions_list), status=200, mimetype='application/json')


@app.route("/api/transactions/sql", methods=["GET"])
def get_transactions_sql():
    """
        This endpoint retrieves all transactions from a PostgreSQL database using a stored procedure.
        If the request's 'Accept' header is 'application/xml', the response is in XML format, otherwise, it is in JSON format.
    """
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
    """
        This endpoint creates a new transaction in the database.
        If the request's 'Accept' header is 'application/xml', the response is in XML format, otherwise, it is in JSON format.
    """
    json_data = request.get_json()
    transactions_collection.insert_one(json_data)

    response_data = {'message': 'Transaction created successfully'}

    if request.headers.get('Accept') == 'application/xml':
        xml_response = json2xml.Json2xml(response_data).to_xml()
        return Response(xml_response, mimetype='application/xml', status=201)

    return jsonify(response_data), 201


@app.route("/api/transactions", methods=["PUT"])
def update_transaction():
    """
        This endpoint updates an existing transaction in the PostgreSQL database using a stored procedure.
        Data for the transaction is obtained from the POST request form.
        If the request's 'Accept' header is 'application/xml', the response is in XML format, otherwise, it is in JSON format.
    """
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
    """
        This endpoint filters transactions based on a date range provided as query parameters ('start_date' and 'end_date').
        - If both 'start_date' and 'end_date' are provided, it constructs a query to find transactions within that date range.
        - The transactions are retrieved from the database and converted to a list.
        - If the request's 'Accept' header is 'application/xml', the response is converted to XML format and returned with a 200 status.
        - Otherwise, the response is returned in JSON format with a 200 status.
        - If an error occurs during the retrieval or serialization of transactions, a 500 status with an error message is returned.
          The error message format is determined by the 'Accept' header of the request.
    """
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
    """
        This endpoint searches for transactions in the PostgreSQL database using a keyword.
        - The keyword is passed as a URL parameter and used to call the stored procedure 'search_table2'.
        - The results of the stored procedure are fetched and stored in 'response_data'.
        - If the request's 'Accept' header is 'application/xml', the response is converted to XML format and returned with a 200 status.
        - Otherwise, the response is returned in JSON format with a 200 status.
        - If an exception occurs during the database query, an error message is generated and returned with a 500 status.
          The error message format is determined by the 'Accept' header of the request.
    """
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
    """
        This endpoint handles the upload of a JSON file:
        - The JSON data is retrieved from the POST request.
        - The JSON is validated using the validate_json() function. If the JSON format is invalid, it returns a 400 status with an error message.
        - If the JSON is valid, it is inserted into the transactions_collection in the database.
        - A success message is returned with a 201 status if the insertion is successful.
        - The response format (XML or JSON) is determined by the 'Accept' header in the request.
    """
    file_data = request.json

    # Validate JSON
    if not validate_json(file_data):
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
    """
        This endpoint retrieves file metadata or contents from the database:
        - It queries the database using a stored procedure `select_all_file()` to fetch all file records.
        - The response data is prepared based on the results of the query.
        - The response format (XML or JSON) is determined by the 'Accept' header in the request.
          - If 'Accept' header is 'application/xml', the response is converted to XML format and returned with a 200 status.
          - Otherwise, the response is returned in JSON format with a 200 status.
        - If an error occurs during the process, a 500 status with an error message is returned.
          - The error message format is also determined by the 'Accept' header in the request.
    """
    try:
        # Fetch file metadata or contents from the database
        files_cursor = postgre_connection.cursor()
        files_cursor.execute("SELECT * FROM select_all_file()")
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
    """
        This endpoint handles GET and POST requests for associations:
        - For GET requests:
          - Fetches all associations from the database using a stored procedure `select_all_association()`.
          - Returns the results in JSON format.
        - For POST requests:
          - Parses JSON data from the request body.
          - Validates the JSON data (validation code is commented out).
          - Extracts `accountID`, `name`, and `password` from the JSON data.
          - Inserts a new association into the database using a stored procedure `insert_into_association()`.
          - Commits the transaction and closes the cursor.
          - Returns a success message in JSON format with a 200 status.
        - If an error occurs during the POST request, returns an error message in JSON format.
    """
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
    """
       This endpoint handles GET and POST requests for members:
       - For GET requests:
         - Fetches all members from the database using a stored procedure `select_all_member()`.
         - Returns the results in JSON format by default, or XML format if specified in the 'Accept' header.
         - In case of a database interface error, returns a 500 status with an error message in the format specified by the 'Accept' header.
       - For POST requests:
         - Parses JSON data from the request body.
         - Validates the JSON data using the `validate_member_json()` function.
         - If validation fails, returns a 400 status with an error message in the format specified by the 'Accept' header.
         - Extracts `name` and `email` from the JSON data and inserts a new member into the database using a stored procedure `insert_into_member()`.
         - Commits the transaction and closes the cursor.
         - Returns a success message in JSON format by default, or XML format if specified in the 'Accept' header, with a 201 status.
         - In case of a database error or JSON decode error, returns an appropriate status with an error message in the format specified by the 'Accept' header.
   """
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
    """
       This endpoint handles DELETE requests to remove a member by their ID:
       - Calls a stored procedure `delete_member(member_id)` to delete the member from the database.
       - Commits the transaction and closes the cursor.
       - Returns a success message in JSON format by default, or XML format if specified in the 'Accept' header, with a 200 status.
       - In case of a database error, returns a 500 status with an error message in the format specified by the 'Accept' header.
   """
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
    """
        This endpoint handles GET and POST requests for categories:
        - For GET requests:
          - Fetches all categories from the 'category' table in the database.
          - Returns the results in JSON format by default, or XML format if specified in the 'Accept' header, with a 200 status.
          - In case of a database error, returns a 500 status with an error message in the format specified by the 'Accept' header.
        - For POST requests:
          - Extracts the 'name' field from the JSON data in the request body.
          - Validates that the 'name' field is present. If not, returns a 400 status with an error message in the format specified by the 'Accept' header.
          - Inserts a new category into the 'category' table in the database.
          - Commits the transaction and closes the cursor.
          - Returns a success message in JSON format by default, or XML format if specified in the 'Accept' header, with a 201 status.
          - In case of a database error, rolls back the transaction and returns a 500 status with an error message in the format specified by the 'Accept' header.
          - In case of other exceptions, returns a 500 status with an error message in the format specified by the 'Accept' header.
    """
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
    """
       This endpoint allows downloading transactions filtered by a date range:
       - The date range is specified using 'start_date' and 'end_date' query parameters.
       - Filters transactions based on the specified date range.
       - Returns the transactions in JSON format by default, or XML format if specified in the 'Accept' header, as an attachment.
       - The filename of the attachment is 'transactions.json' for JSON responses and 'transactions.xml' for XML responses.
   """
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
    """
        This endpoint retrieves transaction details along with joined information from the database based on the transaction ID:
        - It queries the `full_join_view` view to get the transaction details where the `transactionid` matches the provided `trans_id`.
        - Returns the result in JSON format.
        - In case of a database interface error, returns a 500 status with an error message in JSON format.
    """
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
    """
        This endpoint handles GET, POST, and PUT requests for a specific transaction by its ID:
        - For GET requests:
          - Fetches the transaction details from the database using the `select_transaction_on_id` stored procedure.
          - Returns the result in JSON format by default, or XML format if specified in the 'Accept' header.
          - In case of a database interface error, returns a 500 status with an error message in the specified format.
        - For POST and PUT requests:
          - Parses JSON data from the request body to update a transaction.
          - Extracts `description`, `categoryID`, and `memberID` from the JSON data.
          - Converts `categoryID` and `memberID` to integers if they are not "None".
          - Calls the `update_transaction` stored procedure to update the transaction in the database.
          - Returns a success message in JSON format by default, or XML format if specified in the 'Accept' header, with a 200 status.
          - In case of a database interface error, returns a 500 status with an error message in the specified format.
    """
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
