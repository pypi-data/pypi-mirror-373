import json
import os

from marshmallow import ValidationError


def exists(filename):
    """Check a file exists"""
    if not os.path.exists(filename):
        raise ValidationError(f"File `{filename}` does not exist")


def exists_list(filenames):
    """Check a file exists"""
    for filename in filenames:
        if not os.path.exists(filename):
            raise ValidationError(f"File `{filename}` does not exist")


def exists_valid_json(filename):
    """Check a file exists, that it is a json file, and that the json is valid"""
    exists(filename)

    if not filename.endswith(".json"):
        raise ValidationError(f"File `{filename}` should be a json file")

    try:
        with open(filename) as f:
            json.load(f)
    except json.decoder.JSONDecodeError as ex:
        raise ValidationError(f"Could not decode JSON: {str(ex)}")
