"""
Gather actions for a parser or subparser
"""
import inspect
from typing import Any
from typing import Dict


def get(hub, raw_cli: Dict[str, Any], arg: str) -> Dict[str, Any]:
    comps = raw_cli[arg]
    kwargs = {}
    defaults = {}

    kwargs["action"] = action = comps.get("action", None)

    if action is None:
        # Non existing option defaults to a StoreAction in argparse
        action = hub.args.PARSER._registry_get("action", None)

    if isinstance(action, str):
        signature = inspect.signature(
            hub.args.PARSER._registry_get("action", action).__init__
        )
    else:
        signature = inspect.signature(action.__init__)

    if "dest" in signature.parameters:
        # This is the default for positional args
        kwargs["dest"] = comps.pop("dest", arg)
    if "help" in signature.parameters:
        kwargs["help"] = comps.pop("help", "THIS NEEDS SOME DOCUMENTATION!!")

    for comp in comps:
        if comp in signature.parameters:
            kwargs[comp] = comps[comp]

    return {"parser_kwargs": kwargs, "defaults": defaults}
