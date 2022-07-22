import yaml

__virtualname__ = "yaml"


def display(hub, data):
    """
    Print the raw data
    """
    return yaml.safe_dump(data)
