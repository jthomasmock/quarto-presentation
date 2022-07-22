from typing import Any
from typing import Dict


def sig_get(hub, raw_cli: Dict[str, Any], arg: str) -> Dict[str, Any]:
    ...


def post_get(hub, ctx):
    if ctx.ret is None:
        return {}
