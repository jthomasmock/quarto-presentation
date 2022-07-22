"""
Translate an options data structure into command line args
"""
import sys
from typing import Any
from typing import Dict


class DefaultArg:
    ...


def __init__(hub):
    hub.args.DEFAULT = DefaultArg()
    hub.args.PARSER = None
    hub.args.SUBPARSER = None
    hub.args.SUBPARSERS = {}


def keys(hub, opts):
    """
    Return the keys in the right order
    """
    return sorted(opts, key=lambda k: (opts[k].get("display_priority", sys.maxsize), k))


def setup(hub, raw_cli: Dict[str, Any]) -> Dict[str, Any]:
    """
    Take in a pre-defined dict and translate it to args

    opts dict:
        <arg>:
            [group]: foo
            [default]: bar
            [action]: store_true
            [options]: # arg will be turned into --arg
              - '-A'
              - '--cheese'
            [choices]:
              - foo
              - bar
              - baz
            [nargs]: +
            [type]: int
            [dest]: cheese
            help: Some great help message
    """
    parser_definition = []
    for arg in hub.args.init.keys(raw_cli):
        if arg in ("_argparser_",):
            continue

        # Pass the raw_cli and args through all the comps plugins
        ret = hub.comps.init.get(raw_cli, arg)
        parser_definition.append(ret)

    # Apply this config to the root parser
    hub.args.parser.apply(hub.args.PARSER, parser_definition)
