__virtualname__ = "auto"


def detect(hub):
    """
    Automatically determine which loop backend to use
    """
    try:
        loop_backend = hub.OPT.pop_loop.backend
    except (KeyError, AttributeError):
        loop_backend = "auto"
    if loop_backend != "auto":
        return loop_backend
    elif "uv" in hub.loop._loaded:
        # Use uvloop if it is available
        return "uv"
    elif "trio" in hub.loop._loaded:
        # Use trio if it is available
        return "trio"
    elif "proactor" in hub.loop._loaded:
        # Use proactor if we are on windows
        return "proactor"
    elif "selector" in hub.loop._loaded:
        # Default to the selector
        return "selector"
    else:
        # This should never happen, but if it does, we have a backup
        for plugin in hub.loop._loaded:
            if plugin not in ("auto", "init"):
                continue
            return plugin
        else:
            raise ValueError("Could not find any valid loop plugins")


def policy(hub):
    return hub.loop[hub.loop.auto.detect()].policy()


def executor(hub):
    return hub.loop[hub.loop.auto.detect()].executor()


def get(hub):
    return hub.loop[hub.loop.auto.detect()].get()
