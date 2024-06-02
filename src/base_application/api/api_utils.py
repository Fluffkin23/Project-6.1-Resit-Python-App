# This file is necessary for performing validation of JSON and XML data against predefined schemas.
# The validation process ensures that the data adheres to the specified structure and rules, which is crucial
# for maintaining data integrity and consistency in applications that handle complex data structures.
import json
from lxml import etree
import os
import jsonschema

# Define the paths to the schema files for JSON and XML validation
xml_schema_path = os.path.join(os.path.dirname(__file__), 'xmlSchema.xsd')
json_schema_path = os.path.join(os.path.dirname(__file__), 'mt_json_schema.json')
json_member_path_schema = os.path.join(os.path.dirname(__file__), 'insert_member_schema.json')
json_association_schema_path = os.path.join(os.path.dirname(__file__), 'association_json_schema.json')


def validate_json(json_inp):
    """
        Validate the input JSON against the predefined JSON schema.

        Args:
            json_inp (dict): The JSON object to validate.

        Returns:
            bool: True if the JSON is valid, False otherwise.
        """
    try:
        # Open and load the JSON schema
        with open(json_schema_path) as r:
            schema = json.load(r)
            # Validate the input JSON against the schema
            jsonschema.validate(json_inp, schema)
        return True
    except (Exception, jsonschema.ValidationError) as error:
        # Print the error message if validation fails
        print(str(error))
        return False


def validate_member_json(json_inp):
    """
        Validate the input JSON for a member against the predefined member JSON schema.

        Args:
            json_inp (dict): The JSON object to validate.

        Returns:
            bool: True if the JSON is valid, False otherwise.
        """
    try:
        # Open and load the member JSON schema
        with open(json_member_path_schema) as r:
            schema = json.load(r)
            # Validate the input JSON against the schema
            jsonschema.validate(json_inp, schema)
        return True
    except (Exception, jsonschema.ValidationError) as error:
        # Print the error message if validation fails
        print(error)
        return False


def validate_xml(xml_file):
    """
        Validate the input XML against the predefined XML schema.

        Args:
            xml_file (str): The XML string to validate.

        Returns:
            bool: True if the XML is valid, False otherwise.
        """
    # Open and parse the XML schema
    with open(xml_schema_path, 'r') as f:
        xsd = etree.parse(f)
    # Create an XML schema object
    schema = etree.XMLSchema(xsd)
    # Parse the input XML string
    xml_tree = etree.fromstring(xml_file)
    # Validate the XML tree against the schema
    is_valid = schema.validate(xml_tree)
    return is_valid


def validate_association_json(json_inp):
    """
        Validate the input JSON for an association against the predefined association JSON schema.

        Args:
            json_inp (dict): The JSON object to validate.

        Returns:
            bool: True if the JSON is valid, False otherwise.
    """
    try:
        # Open and load the association JSON schema
        with open(json_association_schema_path) as r:
            schema = json.load(r)
            # Validate the input JSON against the schema
            jsonschema.validate(json_inp, schema)
        return True
    except (Exception, jsonschema.ValidationError) as error:
        # Print the error message if validation fails
        print(error)
        return False
