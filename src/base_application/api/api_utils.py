import json
from lxml import etree
import os
import jsonschema
xml_schema_path = os.path.join(os.path.dirname(__file__), 'xmlSchema.xsd')
json_schema_path = os.path.join(os.path.dirname(__file__), 'mt_json_schema.json')
json_member_path_schema = os.path.join(os.path.dirname(__file__), 'insert_member_schema.json')
json_association_schema_path = os.path.join(os.path.dirname(__file__), 'association_json_schema.json')


def validate_json(json_inp):
    try:
        with open(json_schema_path) as r:
            schema = json.load(r)
            jsonschema.validate(json_inp, schema)
        return True
    except (Exception, jsonschema.ValidationError) as error:
        print(str(error))
        return False


def validate_member_json(json_inp):
    try:
        with open(json_member_path_schema) as r:
            schema = json.load(r)
            jsonschema.validate(json_inp, schema)
        return True
    except (Exception, jsonschema.ValidationError) as error:
        print(error)
        return False


def validate_xml(xml_file):
    with open(xml_schema_path, 'r') as f:
        xsd = etree.parse(f)
    schema = etree.XMLSchema(xsd)
    xml_tree = etree.fromstring(xml_file)
    is_valid = schema.validate(xml_tree)
    return is_valid


def validate_association_json(json_inp):
    try:
        with open(json_association_schema_path) as r:
            schema = json.load(r)
            jsonschema.validate(json_inp, schema)
        return True
    except (Exception, jsonschema.ValidationError) as error:
        print(error)
        return False
