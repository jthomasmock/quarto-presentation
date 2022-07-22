"""
Render jinja data
"""
import base64
import os

import jinja2.ext

import rend.exc


async def render(hub, data, params=None):
    """
    Render the given data through Jinja2
    """
    if params is None:
        params = {}

    env_args = {"extensions": [], "loader": jinja2.FileSystemLoader(os.getcwd())}

    if hasattr(jinja2.ext, "do"):
        env_args["extensions"].append("jinja2.ext.do")
    if hasattr(jinja2.ext, "loopcontrols"):
        env_args["extensions"].append("jinja2.ext.loopcontrols")

    jinja_env = jinja2.Environment(
        undefined=jinja2.StrictUndefined, enable_async=True, **env_args
    )

    def base64encode(string):
        if string is None:
            return ""
        return base64.b64encode(string.encode()).decode()

    def base64decode(string):
        if string is None:
            return ""
        return base64.b64decode(string.encode()).decode()

    jinja_env.filters["b64encode"] = base64encode
    jinja_env.filters["b64decode"] = base64decode

    if isinstance(data, bytes):
        data = data.decode()

    try:
        template = jinja_env.from_string(data)
        ret = await template.render_async(params=params, hub=hub)
    except jinja2.exceptions.UndefinedError as exc:
        raise rend.exc.RenderException(f"Jinja variable: {exc.message}")
    except jinja2.exceptions.TemplateSyntaxError as exc:
        problem = []
        for arg in exc.args:
            if isinstance(arg, str):
                problem.append(arg)
            else:
                problem.append(str(arg))

        raise rend.exc.RenderException(f"Jinja syntax error: {' '.join(problem)}")
    return ret
