import re
from sys import api_version

import rend.exc

__virtualname__ = "k8crd"

iregex = r"[^\W0-9][-\w]+"
api_version_regex = rf"^(?P<state>{iregex}(\.{iregex})*)\.(?P<plugin>{iregex})\.idem\.vmware\.com\/(?P<version>{iregex})$"
api_version_re = re.compile(api_version_regex)


def render(hub, data, params=None):
    if not isinstance(data, dict):
        raise rend.exc.RenderException("Invalid data type: dict was expected")

    for key, type in {"apiVersion": str, "kind": str, "metadata": dict}.items():
        if key not in data:
            raise rend.exc.RenderException(
                f"Render error: `{key}` is a mandatory attribute"
            )
        if not isinstance(data[key], type):
            raise rend.exc.RenderException(
                f"Render error: {key} type error: {type} expected"
            )

    api_version = data["apiVersion"]
    kind = data["kind"]
    meta = data["metadata"]

    if "name" not in meta or not isinstance(meta["name"], str):
        raise rend.exc.RenderException(
            "Render error: Proving a name in metadata is mandatory"
        )

    name = meta["name"]
    match = api_version_re.match(api_version)
    if match is None:
        raise rend.exc.RenderException("Render error: apiVersion string is invalid")

    plugin = match.group("plugin")
    state_ref = match.group("state").split(".")
    state_ref.append(plugin)
    state_ref.reverse()
    state_ref.append(kind)
    state_ref.append("present")
    state_ref = ".".join(state_ref).replace("-", "_")

    ret = {name: {state_ref: data["spec"] if "spec" in data else None}}

    return ret
