import json
import xml.etree.ElementTree as ET
import xml.dom.minidom
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
    """
       Define the route for the index endpoint ("/").
       When this endpoint is accessed, it returns a welcome message along with a list of available API endpoints.

       Returns:
           Response: A JSON response containing a welcome message and API endpoint details, with an HTTP status code of 200.
   """
    # Define the response data as a dictionary
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
    # Return the response as a JSON object with a status code of 200
    return make_response(jsonify(answer), 200)


# ----------------------- No SQL MongoDB functions of the API ---------------------------------

@app.route("/api/test")
def test():
    """
        Define the route for the test endpoint ("/api/test").
        When this endpoint is accessed, it returns a simple confirmation message.

        Returns:
            Response: A JSON response confirming that the API works.
    """
    return make_response(jsonify("API works fine!"))


# Define a route for getting the count of transactions
@app.route("/api/getTransactionsCount", methods=["GET"])
def get_transactions_count():
    """
        Define the route for getting the count of transactions ("/api/getTransactionsCount").
        When this endpoint is accessed, it returns the count of documents in the transactions collection.

        Returns:
            dict: A dictionary containing the count of transactions.
    """
    output = {"transactionsCount": transactions_collection.count_documents({})}
    return output


# Define a route for downloading all transactions as a JSON file
@app.route("/api/downloadJSON", methods=["GET"])
def downloadJSON():
    """
        Define the route for downloading all transactions as a JSON file ("/api/downloadJSON").
        When this endpoint is accessed, it retrieves all transactions from the database and returns them as a JSON file.

        Returns:
            Response: A response object containing the JSON data as an attachment.
    """
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
    """
        Define the route for downloading all transactions as an XML file ("/api/downloadXML").
        When this endpoint is accessed, it retrieves all transactions from the database, converts them to XML, validates the XML, and returns it as a downloadable file.

        Returns:
            Response: A response object containing the XML data as an attachment.
    """
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


@app.route("/api/getTransactions", methods=["GET"])
def get_all_transactions():
    """
        Define the route for retrieving all transactions ("/api/getTransactions").
        When this endpoint is accessed, it retrieves transactions from the database based on optional date range filters.

        Returns:
            Response: A response object containing the transactions data in JSON format.
    """
    # Get start and end dates from query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Initialize the query dictionary
    query = {}

    # Add date range filter to the query if both start and end dates are provided
    if start_date and end_date:
        query["transactions.date"] = {"$gte": start_date, "$lte": end_date}

    try:
        # Retrieve transactions from the database matching the query
        transactions_cursor = transactions_collection.find(query)
        transactions_list = list(transactions_cursor)
        # Return the transactions data as a JSON response
        return Response(
            response=json_util.dumps(transactions_list),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        # Print error message if there's an issue retrieving or serializing the data
        print("Error retrieving or serializing transactions:", e)
        # Return an error response in case of failure
        return Response(
            response=json_util.dumps({"error": "Internal Server Error"}),
            status=500,
            mimetype='application/json'
        )


# Send a POST request with the file path to this function
@app.route("/api/uploadFile", methods=["POST"])
def file_upload():
    """
        Define the route for uploading a JSON file ("/api/uploadFile").
        When this endpoint is accessed, it retrieves the JSON file from the POST request, validates it, and inserts it into the NoSQL database.

        Returns:
            Response: A JSON response indicating the status of the file upload.
    """

    # Get the JSON file from the POST request
    json_data = request.get_json()

    # Validate JSON
    if not validate_json(json_data):
        jsonify({'Error': 'Error Occured'})

    # Insert into No SQL Db
    transactions_collection.insert_one(json_data)

    return make_response(jsonify(status="File uploaded!"), 200)


# -------------------------- SQL PostGreSQL DB functions of the API ---------------------------
# Define a route for deleting a member
@app.route("/api/deleteMember", methods=["DELETE"])
def delete_member():
    """
        Define the route for deleting a member ("/api/deleteMember").
        When this endpoint is accessed, it deletes a member from the PostgreSQL database using the provided member ID.

        Returns:
            Response: A JSON response indicating the result of the deletion operation.
    """
    try:
        # Get the member ID from the query parameters
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


# Define a route for inserting an association with a hashed password
@app.route("/api/insertAssociation", methods=["POST"])
def insert_association():
    """
       Define the route for inserting an association ("/api/insertAssociation").
       When this endpoint is accessed, it retrieves the JSON data from the POST request, validates it, and inserts it into the PostgreSQL database.

       Returns:
           Response: A JSON response indicating the result of the insertion operation.
   """
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


# Define a route for inserting a new member
@app.route("/api/insertMemberSQL", methods=["POST"])
def insert_member():
    """
        Define the route for inserting a new member ("/api/insertMemberSQL").
        When this endpoint is accessed, it retrieves the JSON data from the POST request, validates it, and inserts it into the PostgreSQL database.

        Returns:
            Response: A JSON response indicating the result of the insertion operation.
    """
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


# Define a route for retrieving all associations
@app.route("/api/getAssociation", methods=["GET"])
def get_association():
    """
        Define the route for retrieving all associations ("/api/getAssociation").
        When this endpoint is accessed, it retrieves all associations from the PostgreSQL database.

        Returns:
            Response: A JSON response containing the association data.
    """
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
    """
       Define the route for inserting a transaction ("/api/insertTransaction").
       When this endpoint is accessed, it retrieves the JSON data from the POST request, validates it,
       and inserts the transaction details into the PostgreSQL database.

       Returns:
           Response: A JSON response indicating the result of the insertion operation.
   """
    try:
        # Get the JSON file from the POST request
        json_trans = request.get_json()

        # Validate JSON
        if not validate_json(json_trans):
            print("Validation failed")
            return jsonify({'Error': 'Error Occured'})

        bank_reference = str(json_trans["transaction_reference"])

        cursor = postgre_connection.cursor()

        # Iterate over each transaction in the JSON data
        for trans_set in json_trans["transactions"]:
            amount = trans_set["amount"]["amount"]
            currency = trans_set["amount"]["currency"]
            transaction_date = trans_set["date"]
            transaction_details = str(trans_set["transaction_details"])
            transaction_details = transaction_details.replace("/", "-")
            description = None
            typetransaction = trans_set["status"]

            # Call a stored procedure to insert the transaction
            cursor.execute('CALL insert_into_transaction(%s,%s,%s,%s,%s,%s,%s,%s,%s)', (
                bank_reference, transaction_details, description, amount, currency, transaction_date, None, None,
                typetransaction))
            # commit the transaction
            postgre_connection.commit()

        # close the cursor
        cursor.close()

        return jsonify({'message': 'File inserted successfully'})
    except (Exception, psycopg2.DatabaseError) as error:
        # Return an error message if an exception occurs
        error_message = str(error)
        return jsonify({'error': error_message})


# Define a route for inserting a file
@app.route("/api/insertFile", methods=["POST"])
def insert_file():
    """
        Define the route for inserting a file ("/api/insertFile").
        When this endpoint is accessed, it retrieves the JSON data from the POST request, validates it,
        and inserts the file details into the PostgreSQL database.

        Returns:
            Response: A JSON response indicating the result of the insertion operation.
    """
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


# Define a route for retrieving all transactions
@app.route("/api/getTransactionsSQL", methods=["GET"])
def get_transactions_sql():
    """
        Define the route for retrieving all transactions ("/api/getTransactionsSQL").
        When this endpoint is accessed, it retrieves all transactions from the PostgreSQL database.

        Returns:
            Response: A JSON response containing the transactions data.
    """
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
# Define a route for retrieving all files
@app.route("/api/getFile", methods=["GET"])
def get_file():
    """
        Define the route for retrieving all files ("/api/getFile").
        When this endpoint is accessed, it retrieves all files from the PostgreSQL database.

        Returns:
            Response: A JSON response containing the file data.
    """
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
    """
        Define the route for retrieving all members ("/api/getMembers").
        When this endpoint is accessed, it retrieves all members from the PostgreSQL database.

        Returns:
            Response: A JSON response containing the members data.
    """
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
    """
       Define the route for retrieving all categories ("/api/getCategory").
       When this endpoint is accessed, it retrieves all categories from the PostgreSQL database.

       Returns:
           Response: A JSON response containing the categories data.
   """
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


# Define a route for inserting a category into the database
@app.route("/api/insert_category_into_database", methods=["POST"])
def insert_category_into_database(category_name):
    """
        Define the route for inserting a category into the database ("/api/insert_category_into_database").
        When this endpoint is accessed, it inserts the provided category name into the PostgreSQL database.

        Args:
            category_name (str): The name of the category to insert.

        Returns:
            bool: True if the insertion was successful, False otherwise.
    """
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

# Define a route for inserting a category
@app.route("/api/insertCategory", methods=["POST"])
def insert_category():
    """
        Define the route for inserting a category ("/api/insertCategory").
        When this endpoint is accessed, it retrieves the category name from the POST request,
        validates it, and inserts it into the PostgreSQL database.

        Returns:
            Response: A JSON response indicating the result of the insertion operation.
    """
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

# Define a route for retrieving a transaction by ID
@app.route("/api/getTransactionOnId/<trans_id>", methods=["GET"])
def get_transaction_on_id(trans_id):
    """
        Define the route for retrieving a transaction by ID ("/api/getTransactionOnId/<trans_id>").
        When this endpoint is accessed, it retrieves the transaction with the specified ID from the PostgreSQL database.

        Args:
            trans_id (str): The ID of the transaction to retrieve.

        Returns:
            Response: A JSON response containing the transaction data.
    """
    try:
        cursor = postgre_connection.cursor()
        # Call a stored procedure to select a transaction by ID
        cursor.execute('SELECT * FROM select_transaction_on_id(%s)', (int(trans_id),))
        # Get all data from the stored procedure
        data = cursor.fetchall()
        # Return data in JSON format
        return jsonify(data)
    except psycopg2.InterfaceError as error:
        error_message = str(error)
        return jsonify({'error': error_message})

# Define a route for updating a transaction
@app.route("/api/updateTransaction", methods=["PUT"])
def update_transaction():
    """
        Define the route for updating a transaction ("/api/updateTransaction").
        When this endpoint is accessed, it retrieves the transaction data from the PUT request,
        validates it, and updates the corresponding transaction in the PostgreSQL database.

        Returns:
            Response: A JSON response indicating the result of the update operation.
    """
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

# Define a route for retrieving a transaction by ID with a join
@app.route("/api/searchKeyword/<keyword>", methods=["GET"])
def search_keyword(keyword):
    """
       Define the route for retrieving a transaction by ID with a join ("/api/getTransactionOnIdJoin/<trans_id>").
       When this endpoint is accessed, it retrieves the transaction with the specified ID from the PostgreSQL database using a join.

       Args:
           trans_id (str): The ID of the transaction to retrieve.

       Returns:
           Response: A JSON response containing the joined transaction data.
   """
    try:
        cursor = postgre_connection.cursor()

        # Call the search_table2 function with a search term
        cursor.execute("SELECT * FROM search_table2(%s)", (keyword,))

        # Fetch the results from the function call
        results = cursor.fetchall()
        return jsonify(results)
    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({'message': error})
