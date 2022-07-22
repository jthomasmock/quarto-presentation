"""
The render process for the cli does NOT use the rend project for a couple
of reasons
1. Config needs to be very early in the startup, therefore it cannot use
   asyncio, all rend funcs use asyncio
2. Config will not allow for template wrapping as the render is just a
   single command line render
"""
from typing import Any
from typing import List


def process(hub, renderer: str, value: str):
    """
    Take a renderer and a value, process it, and return the processed value

    This is intended to load a string through the config render system
    """
    return hub.render[renderer].render(value)


def pipe(hub, dpipe: List[str], data: Any):
    """
    Given a render pipe, render the given data
    """
    for render in dpipe:
        if isinstance(render, bytes):
            render = render.decode()
        data = hub.render.init.process(render, data)
    return data


def load_file(hub, renderer: str, file_name: str):
    """
    Load up a file with the passed renderer unless the file contains a
    renderer she-bang line
    """
    with open(file_name, "rb") as rfh:
        data = rfh.read()
    if not data:
        return {}
    if data.startswith(b"#!"):
        dpipe = data[2 : data.index(b"\n")].split(b"|")
        return hub.render.init.pipe(dpipe, data)
    else:
        return hub.render.init.process(renderer, data)
