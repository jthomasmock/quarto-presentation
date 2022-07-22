from typing import Any
from typing import Dict

import dict_tools.update as dict_tool


def get(hub, raw_cli: Dict[str, Any], arg: str) -> Dict[str, Any]:
    raw_cli.get(arg, {}).copy()

    result = {
        "parser_kwargs": {},
        "parser_args": [],
        "groups": {},
        "ex_groups": {},
        "subcommands": [],
    }

    for sub in hub.comps._loaded:
        if sub == "init":
            continue
        ret = hub.comps[sub].get(raw_cli, arg)
        result = dict_tool.update(result, ret, merge_lists=True)

    return result
