from typing import Any
from typing import Dict

GLOBAL_SUBCOMMAND = "_global_"


def init(hub):
    hub.args.parser.init()
    if hub.args.SUBPARSER is None:
        hub.args.SUBPARSER = hub.args.PARSER.add_subparsers(dest="_subparser_")


def add(hub, arg: str, **kwargs):
    hub.args.subcommands.init()
    hub.args.SUBPARSERS[arg] = hub.args.SUBPARSER.add_parser(arg, **kwargs)


def parse(hub, raw: Dict[str, Any], cli: str):
    """
    Look over the data and extract and set up the subparsers for subcommands
    """
    subs = raw.get(cli, {}).get("SUBCOMMANDS")
    if not subs:
        return

    for arg in hub.args.init.keys(subs):
        if arg in ("_argparser_",):
            continue
        comps = subs[arg]
        kwargs = {}
        if "help" in comps:
            kwargs["help"] = comps["help"]
        if "desc" in comps:
            kwargs["description"] = comps["desc"]
        hub.args.subcommands.add(arg, **kwargs)


def apply(
    hub,
    root_parser,
    context: Dict[str, Any],
    definition: Dict[str, Any],
):
    for subcommand in definition.pop("subcommands"):
        if subcommand == GLOBAL_SUBCOMMAND:
            # Add it to the main parser first
            hub.args.parser.apply(
                parser=root_parser,
                context=context,
                arg_definitions=[definition],
            )

            # Add it to all subcommands
            for name in hub.args.SUBPARSERS:
                hub.args.subcommands.apply_single(
                    subparser=name, definition=definition, context=context
                )
        else:
            hub.args.subcommands.apply_single(
                subparser=subcommand, definition=definition, context=context
            )


def apply_single(hub, subparser: str, context, definition):
    if subparser not in hub.args.SUBPARSERS:
        return
    if subparser not in context["subparser_contexts"]:
        context["subparser_contexts"][subparser] = hub.args.parser.context()
    hub.args.parser.apply(
        parser=hub.args.SUBPARSERS[subparser],
        arg_definitions=[definition],
        context=context["subparser_contexts"][subparser],
    )
