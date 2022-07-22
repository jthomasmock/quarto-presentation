import json

import rend.exc


__virtualname__ = "json"


def render(hub, data, params=None):
    """
    Render the given json data
    """
    try:
        if isinstance(data, (str, bytes, bytearray)):
            ret = json.loads(data)
        else:
            ret = json.load(data)
    except json.decoder.JSONDecodeError as exc:
        if exc.msg and hasattr(exc, "lineno") and hasattr(exc, "colno"):
            problem = f"{exc.msg} on line: {exc.lineno} column: {exc.colno}"
        else:
            problem = exc.msg
        raise rend.exc.RenderException(f"Json render error: {problem}")
    return ret
