"""
Gather groups for a parser or subparser
"""
from typing import Any
from typing import Dict


def get(hub, raw_cli: Dict[str, Any], arg: str) -> Dict[str, Any]:
    comps = raw_cli[arg]

    if "group" not in comps:
        return {}

    group = comps["group"]

    return {"groups": [group]}
