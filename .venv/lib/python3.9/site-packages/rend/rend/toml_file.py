import toml

import rend.exc


__virtualname__ = "toml"


def render(hub, data, params=None):
    """
    Render the given toml data
    """
    if isinstance(data, bytes):
        data = data.decode()
    try:
        ret = toml.loads(data)
    except toml.TomlDecodeError as exc:
        if exc.msg and hasattr(exc, "lineno") and hasattr(exc, "colno"):
            problem = f"{exc.msg} on line: {exc.lineno} column: {exc.colno}"
        else:
            problem = exc.msg
        raise rend.exc.RenderException(f"Toml render error: {problem}")
    return ret
