import asyncio
import secrets

import rend.exc


def __init__(hub):
    hub.pop.sub.add(dyne_name="output")


def standalone(hub):
    """
    Execute the render system onto a single file, typically to test basic
    functionality
    """
    hub.pop.config.load("rend", cli="rend")
    hub.pop.loop.start(_standalone(hub))


async def _standalone(hub):
    outputter = hub.OPT.rend.output or "nested"
    ret = await hub.rend.init.parse(hub.OPT.rend.file, hub.OPT.rend.pipe)
    print(hub.output[outputter].display(ret))


async def render(hub, data, renderer: str, params):
    data = hub.rend[renderer].render(data, params)
    if asyncio.iscoroutine(data):
        data = await data
    return data


async def parse(hub, fn, pipe=None, params=None):
    """
    Pass in the render pipe to use to render the given file. If no pipe is
    passed in then the file will be checked for a render shebang line. If
    no render shebang line is present then the system will raise an
    Exception
    If a file defines a shebang render pipe and a pipe is passed in, the
    shebang render pipe line will be used
    """
    if params is None:
        params = {}
    with open(fn, "rb") as rfh:
        data = rfh.read()
    if data.startswith(b"#!"):
        dpipe = data[2 : data.index(b"\n")].split(b"|")
    elif pipe:
        dpipe = pipe.split("|")
    else:
        raise rend.exc.RendPipeException(
            f"File {fn} passed in without a render pipe defined"
        )
    for renderer in dpipe:
        if isinstance(renderer, bytes):
            renderer = renderer.decode()
        data = await hub.rend.init.render(data, renderer, params)

    return data


async def parse_bytes(hub, block, pipe=None, params=None):
    """
    Send in a block from a render file and render it using the named pipe
    """
    if params is None:
        params = {}
    if isinstance(pipe, str):
        pipe = pipe.split("|")
    if isinstance(pipe, bytes):
        pipe = pipe.split(b"|")
    fn = block.get("fn")
    ln = block.get("ln")
    data = block.get("bytes")
    pipe = block.get("pipe", pipe)
    if pipe is None:
        raise rend.exc.RendPipeException(
            f"File {fn} at block line {ln} passed in without a render pipe defined"
        )
    for renderer in pipe:
        if isinstance(renderer, bytes):
            renderer = renderer.decode()
        data = await hub.rend.init.render(data, renderer, params)
    return data


def blocks(hub, fn, content: bytes = None):
    """
    Pull the render blocks out of a bytes content along with the render metadata
    stored in shebang lines. If the content is None, it will be populated by reading the file fn.
    """
    bname = "raw"
    ret = {bname: {"ln": 0, "fn": fn, "bytes": b""}}
    bnames = [bname]
    rm_bnames = set()

    if content is None:
        with open(fn, "rb") as rfh:
            content = rfh.read()

    num = -1
    for line in content.splitlines(True):
        num += 1
        if line.startswith(b"#!"):
            # Found metadata tag
            root = line[2:].strip()
            if root == b"END":
                bnames.pop(-1)
                if not bnames:
                    raise rend.exc.RenderException(f"Unexpected End of file line {num}")
                bname = bnames[-1]
                continue
            else:
                bname = f"{fn}|{secrets.token_hex(2)}"
                ret[bname] = {"ln": num, "fn": fn, "keys": {}, "bytes": b""}
                bnames.append(bname)
            parts = root.split(b";")
            for ind, part in enumerate(parts):
                if b":" in part:
                    req = part.split(b":")
                    if len(req) < 2:
                        continue
                    ret[bname]["keys"][req[0].decode()] = req[1].decode()
                else:
                    if b"|" in part:
                        pipes = part.split(b"|")
                    else:
                        pipes = [part]
                    ret[bname]["pipe"] = pipes
        else:
            ret[bname]["bytes"] += line
    for bname, data in ret.items():
        if not data["bytes"]:
            rm_bnames.add(bname)
    for bname in rm_bnames:
        ret.pop(bname)
    return ret
