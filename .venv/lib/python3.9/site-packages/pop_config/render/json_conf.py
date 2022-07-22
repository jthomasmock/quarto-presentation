"""
Define the JSON loader interface
"""
import json

__virtualname__ = "json"


def __virtual__(hub):
    return True


def load(hub, path):
    """
    Use json to read in a file
    """
    try:
        with open(path) as fp_:
            ret = json.loads(fp_.read())
        return ret
    except FileNotFoundError:
        return {}


def render(hub, val):
    """
    Take the string and render it in json
    """
    return json.loads(val)
