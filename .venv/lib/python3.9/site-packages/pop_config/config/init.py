def __init__(hub):
    """
    Load the subdirs for conf
    """
    for dyne in ("args", "comps", "log", "render"):
        hub.pop.sub.add(dyne_name=dyne)
    hub.config.ARGS = {}
    hub.config.SECTIONS = ("CONFIG", "CLI_CONFIG", "SUBCOMMANDS", "DYNE")
    hub.config.CONFIG_SECTIONS = ("CONFIG", "CLI_CONFIG")
