import json
import os

import jsonschema

_SCHEMA = json.load(open(os.path.join(os.path.dirname(__file__), "schema.json"), encoding="utf-8"))["json_schema"]


def validate_output(text):
    """Return the parsed 4-key dict, or None if text is not a schema-valid JSON object."""
    try:
        obj = json.loads(text)
        jsonschema.validate(obj, _SCHEMA)
    except (ValueError, TypeError, jsonschema.ValidationError):
        return None
    return obj
