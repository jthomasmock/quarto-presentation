from typing import Dict


def apply(
    hub,
    raw: Dict,
    raw_cli: Dict,
    cli: Dict,
    cli_args: Dict,
    os_vars: Dict,
    configs: Dict,
) -> Dict:
    """
    This assumes that we are using the namespace approach;
    This makes the config structure the easiest, meaning that components are namespaced by the user.
    Some other additional pattern could be added and this chunk could be made pluggable.
    Order of config loading:
    # Defaults (raw)
    # Config files (configs)
    # OS (os_vars)
    # CLI (cli_args)
    """
    ret = {}
    ret = hub.config.order.defaults(raw, ret)
    ret = hub.config.order.config(configs, ret)
    ret = hub.config.order.os_vars(os_vars, ret)
    ret = hub.config.order.cli_vars(raw_cli, cli_args, cli, ret)
    return ret


def defaults(hub, raw: Dict, ret: Dict) -> Dict:
    """
    Get the CONFIG values with defaults
    """
    for imp in raw:
        ret[imp] = {}
        for key, data in raw[imp]["CONFIG"].items():
            if "default" in data:
                ret[imp][key] = data["default"]
    return ret


def config(hub, configs, ret) -> Dict:
    """
    Get values from the config file
    """
    for imp in configs:
        if imp not in ret:
            ret[imp] = {}
        for key in configs[imp]:
            ret[imp][key] = configs[imp][key]
    return ret


def os_vars(hub, os_vars: Dict[str, Dict], ret: Dict[str, Dict]) -> Dict:
    """
    Read OS variables
    """
    for imp in os_vars:
        for key in os_vars[imp]:
            ret[imp][key] = os_vars[imp][key]
    return ret


def cli_vars(
    hub,
    raw_cli: Dict[str, Dict],
    cli_args: Dict[str, Dict],
    cli: Dict[str, Dict],
    ret: Dict,
) -> Dict:
    """
    Read CLI variables
    """
    for key in cli_args:
        if key in raw_cli:
            if "source" in raw_cli[key]:
                ret[raw_cli[key]["source"]][key] = cli_args[key]
            else:
                ret[cli][key] = cli_args[key]
    return ret
