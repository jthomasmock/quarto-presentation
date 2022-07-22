import sys
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

import dict_tools.update


def get(hub, raw: Dict[str, Any], cli: str) -> Dict[str, Any]:
    """
    Gather the arguments that need to be parsed by the CLI
    """
    ret = {}
    main = raw.get(cli, {}).get("CLI_CONFIG")
    main_raw = raw.get(cli, {}).get("CONFIG")

    for key, data in main.items():
        ret[key] = {}
        dict_tools.update.update(ret[key], data)
        if key in main_raw:
            dict_tools.update.update(ret[key], main_raw[key])
        if "source" in data:
            src = raw.get(data["source"], {}).get("CONFIG", {}).get(key)
            if src is not None:
                dict_tools.update.update(ret[key], src)
        if "default" in ret[key]:
            ret[key]["default"] = hub.args.DEFAULT
    return ret


def gather(
    hub, raw: Dict[str, Any], cli: str, parse_cli: bool
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Return the cli arguments as they are parsed
    """
    if not parse_cli:
        return {}, {}
    hub.args.parser.init()
    hub.args.subcommands.parse(raw, cli)

    raw_cli = hub.args.cli.get(raw, cli)
    hub.args.init.setup(raw_cli)

    cli_args = hub.args.cli.parse(sys.argv[1:])
    hub.args.cli.render(cli_args, raw_cli)

    clean_args = hub.args.cli.clean_defaults(cli_args)
    return clean_args, raw_cli


def parse(
    hub,
    args: List[str],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Parse the command line options
    """
    opts = hub.args.PARSER.parse_args(args)
    opts_dict = opts.__dict__
    hub.SUBPARSER = opts_dict.get("_subparser_", None)

    # Parse the args of the subparser
    if hub.SUBPARSER:
        # Remove the subparser and re-parse what's left so that we can pick up anything that was missed
        args.remove(hub.SUBPARSER)
        sub_opts, _ = hub.args.SUBPARSERS[hub.SUBPARSER].parse_known_args(args)
        sub_opts_dict = sub_opts.__dict__
    else:
        sub_opts_dict = {}

    # If the subparser got any values that should have been passed to the root, then update the dict
    for k in opts_dict:
        if opts_dict[k] is hub.args.DEFAULT:
            sub_opt = sub_opts_dict.get(k, hub.args.DEFAULT)
            if sub_opt is not hub.args.DEFAULT:
                opts_dict[k] = sub_opt
    return opts_dict


def clean_defaults(hub, cli_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    If anyone did not pass in an argument then the key will match the
    bad default and needs to be removed
    """
    ret = {}
    for key, val in cli_args.items():
        if val is not hub.args.DEFAULT:
            ret[key] = val
    return ret


def render(hub, cli_args: Dict[str, Any], raw_cli: Dict[str, Any]):
    """
    For options specified as such, take the string passed into the cli and
    render it using the specified render flag
    """
    for key, val in raw_cli.items():
        if key not in cli_args:
            continue
        if "render" not in val:
            continue
        if val["default"] != cli_args[key]:
            # The value was changed, render it
            cli_args[key] = hub.render.init.process(val["render"], cli_args[key])
