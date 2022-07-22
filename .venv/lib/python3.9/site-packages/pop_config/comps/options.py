"""
Gather groups for a parser or subparser
"""
from typing import Any
from typing import Dict


def get(hub, raw_cli: Dict[str, Any], arg: str) -> Dict[str, Any]:
    comps = raw_cli[arg]

    if comps.get("positional"):
        # The action will define the dest for positional args
        return {}

    args = [f"--{arg.replace('_', '-')}"]
    for o_str in comps.get("options", ()):
        if len(o_str) == 1:
            o_str = f"-{o_str}"
        elif not o_str.startswith("-"):
            o_str = f"--{o_str}"
        if o_str not in args:
            args.append(o_str)

    return {"parser_args": args}
