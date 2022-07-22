"""
Gather mutually exclusive groups for a parser or subparser
"""
from typing import Any
from typing import Dict


def get(hub, raw_cli: Dict[str, Any], arg: str) -> Dict[str, Any]:
    comps = raw_cli[arg]

    if "ex_group" not in comps:
        return {}

    group = comps["ex_group"]

    return {"ex_groups": [group]}
