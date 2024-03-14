import hashlib
import json
import mt940
import re
# Make a regular expression for validating an Email
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'


def parse_mt940_file(file_path) -> dict:
    # Parse the contents of the MT940 file
    transactions = mt940.parse(file_path)

    # Convert the parsed transactions to a JSON string
    transactions = json.dumps(transactions, indent=4, sort_keys=True, cls=mt940.JSONEncoder)

    # Load the JSON string as a dictionary
    transactions = json.loads(transactions)

    # Return the dictionary containing the parsed transactions
    return transactions


def check_mt940_file(file_path):
    if check_tag(file_path) and check_file_extension(file_path):
        return True
    else:
        return False


def check_tag(file_path):
    tag_20 = ':20:'
    tag_25 = ':25:'
    tag_28c = ':28C:'
    tag_60 = ':60F:'
    tag_62 = ':62F:'
    tags = [':20:', ':25:', ':28C:', ':60F:', ':62F:']
    with open(file_path, 'r') as file:
        # read all content of a file
        content = file.read()
        # check if all the strings from tag array are present in the file
        if all(tag in content for tag in tags):
            isTag = True
        else:
            isTag = False
        if tag_20 not in content:
            print("Transaction Reference Number( tag 20 ) is missing")
        if tag_25 not in content:
            print("Account Identification ( tag 25 ) is missing")
        if tag_28c not in content:
            print("Statement number( tag 28C )  is missing")
        if tag_60 not in content:
            print("Opening Balance (tag 60F )is missing")
        if tag_62 not in content:
            print("Closing balance ( tag 62F ) is missing")
    return isTag


def check_file_extension(file_path):
    # check if the file name ends with .sta
    if file_path.endswith('.sta'):
        return True
    else:
        return False


def hash_password(password):
    # Convert the password string to bytes and hash it using SHA-256
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password


def check_email(email):
    # pass the regular expression and the string into the fullmatch() method
    if re.fullmatch(regex, email):
        return True
    else:
        return False
