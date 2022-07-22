from typing import ByteString
from typing import Dict
from typing import Iterable
from typing import Mapping


def decode(value):
    if isinstance(value, ByteString):
        return value.decode()
    elif isinstance(value, str):
        return value
    elif isinstance(value, (Mapping, Dict)):
        return decode_dict(value)
    elif isinstance(value, Iterable):
        return value.__class__(decode(x) for x in value)
    else:
        return value


def decode_dict(data: Dict[bytes, bytes]) -> Dict[str, str]:
    """
    Recursively decode all byte-strings found in a dictionary
    """
    return {decode(key): decode(value) for key, value in data.items()}
