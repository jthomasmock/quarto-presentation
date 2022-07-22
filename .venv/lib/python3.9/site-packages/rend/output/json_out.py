"""
Display data in JSON format
"""
import json

__virtualname__ = "json"


def display(hub, data):
    """
    Print the output data in JSON
    """
    try:
        indent = 4
        return json.dumps(data, default=repr, indent=indent)

    except UnicodeDecodeError as exc:
        return json.dumps(
            {"error": "Unable to serialize output to json", "message": str(exc)}
        )

    # Return valid JSON for unserializable objects
    return json.dumps({})
