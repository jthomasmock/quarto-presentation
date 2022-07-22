import argparse
from typing import Any
from typing import Dict
from typing import List

__func_alias__ = {"help_": "help"}


def init(hub):
    if hub.args.PARSER is None:
        hub.args.PARSER = argparse.ArgumentParser(conflict_handler="resolve")


def help_(hub) -> str:
    """
    Return the help text as a string
    """
    hub.args.parser.init()
    if hub.SUBPARSER:
        return hub.args.SUBPARSERS[hub.SUBPARSER].format_help()
    else:
        return hub.args.PARSER.format_help()


def context(hub) -> Dict[str, Dict[str, Any]]:
    return dict(existing_groups={}, existing_mutex_groups={}, subparser_contexts={})


def apply(
    hub,
    parser: argparse.ArgumentParser,
    arg_definitions: List[Dict[str, Any]],
    context: Dict[str, Any] = None,
):
    """
    :param hub:
    :param parser: An argument parser or subparser
    :param arg_definitions: A dictionary describing an argument
    :param context: values that should be tracked through recursive calls to this function
    """
    if context is None:
        context = hub.args.parser.context()

    for definition in arg_definitions:
        if definition.get("subcommands"):
            hub.args.subcommands.apply(
                root_parser=parser,
                definition=definition,
                context=context,
            )
        elif definition.get("ex_groups"):
            hub.args.parser.apply_ex_groups(parser, context, definition)
        elif definition.get("groups"):
            hub.args.parser.apply_groups(parser, context, definition)
        else:
            hub.args.parser.apply_default(parser, context, definition)


def apply_groups(hub, parser, context, definition):
    for g in definition["groups"]:
        if g not in context["existing_groups"]:
            context["existing_groups"][g] = parser.add_argument_group(g)
        context["existing_groups"][g].add_argument(
            *definition["parser_args"], **definition["parser_kwargs"]
        )


def apply_ex_groups(hub, parser, context, definition):
    for g in definition["ex_groups"]:
        if g not in context["existing_mutex_groups"]:
            context["existing_mutex_groups"][g] = parser.add_mutually_exclusive_group()
        context["existing_mutex_groups"][g].add_argument(
            *definition["parser_args"], **definition["parser_kwargs"]
        )


def apply_default(hub, parser, context, definition):
    parser.add_argument(*definition["parser_args"], **definition["parser_kwargs"])
