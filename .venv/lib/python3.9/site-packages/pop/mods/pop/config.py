from typing import List

import pop.hub


def __virtual__(hub):
    hub.pop.sub.add(dyne_name="config")
    return hasattr(hub.config, "integrate"), "pop-config is not installed"


def load(
    hub: "pop.hub.Hub",
    sources: List[str],
    cli: str = None,
    dyne_name: str = None,
    loader: str = "yaml",
    parse_cli: bool = True,
    logs: bool = True,
):
    """
    Use the pop-config system to load up a fresh configuration for this project
    from the included conf.py file.
    """
    hub.config.integrate.load(sources, cli, dyne_name, loader, parse_cli, logs)
