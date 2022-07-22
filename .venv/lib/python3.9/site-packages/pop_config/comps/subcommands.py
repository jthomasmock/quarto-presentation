"""
Gather subcommands for a parser
"""
from typing import Any
from typing import Dict


def get(hub, raw_cli: Dict[str, Any], arg: str) -> Dict[str, Any]:
    comps = raw_cli[arg]

    subcommands = comps.get("subcommands", [])
    if not isinstance(subcommands, list):
        subcommands = [subcommands]

    return {"subcommands": subcommands}
