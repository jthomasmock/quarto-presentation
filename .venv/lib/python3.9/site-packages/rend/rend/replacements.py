def _iterate_over(data):
    if isinstance(data, str):
        if "__PYTHON_NONE__" == data:
            return None
        elif "__PYTHON_NONE__" in data:
            return data.replace("__PYTHON_NONE__", "")
        else:
            return data
    elif isinstance(data, dict):
        ret = {}
        for key, value in data.items():
            key = _iterate_over(key)
            value = _iterate_over(value)
            ret[key] = value
        return ret
    elif isinstance(data, list):
        ret = []
        for item in data:
            ret.append(_iterate_over(item))
        return ret
    else:
        return data


def render(hub, data, params=None):
    return _iterate_over(data)
