import inspect
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List

import pop.exc
import pop.hub
import pop.loader

NO_TYPE_ANNOTATION = object()


def contract(
    hub: "pop.hub.Hub",  # pylint: disable=unused-argument
    raws: Iterable["pop.loader.LoadedMod"],
    mod: "pop.loader.LoadedMod",
):
    """
    Verify module level contract - functions only
    :param hub: The redistributed pop central hub
    :param raws: A list of loaded modules with contracts
    :param mod: A loader module
    """
    sig_errs = []
    sig_miss = []
    for raw in raws:
        if isinstance(raw, pop.loader.LoadError):
            sig_errs.append(str(raw))
            continue
        else:
            for fun in raw._funcs:
                if fun.startswith("sig_"):
                    tfun = fun[4:]
                    if tfun not in mod._funcs:
                        sig_miss.append(
                            f"Function '{tfun}' is missing from {mod.__file__}"
                        )
                        continue
                    sig_errs.extend(sig(mod._funcs[tfun].func, raw._funcs[fun].func))
                    sig_errs.extend(sync(mod._funcs[tfun].func, raw._funcs[fun].func))
    if sig_errs or sig_miss:
        msg = ""
        if sig_errs:
            msg += f"Signature Errors in {mod.__file__}:\n"
            for err in sig_errs:
                msg += f"{err}\n"
        if sig_miss:
            msg += f"Signature Functions Missing in {mod.__file__}:\n"
            for err in sig_miss:
                msg += f"{err}\n"
        msg = msg.strip()
        raise pop.exc.ContractSigException(msg)


def sig_map(ver: Callable) -> Dict[str, Any]:
    """
    Generates the map dict for the signature verification
    """
    vsig = inspect.signature(ver)
    vparams = list(vsig.parameters.values())
    vdat = {"args": [], "v_pos": -1, "kw": [], "kwargs": False, "ann": {}}
    for ind in range(len(vparams)):
        param = vparams[ind]
        val = param.kind.value
        name = param.name
        if val == inspect._POSITIONAL_ONLY or val == inspect._POSITIONAL_OR_KEYWORD:
            vdat["args"].append(name)
            if param.default != inspect._empty:  # Is a KW, can be inside of **kwargs
                vdat["kw"].append(name)
        elif val == inspect._VAR_POSITIONAL:
            vdat["v_pos"] = ind
        elif val == inspect._KEYWORD_ONLY:
            vdat["kw"].append(name)
        elif val == inspect._VAR_KEYWORD:
            vdat["kwargs"] = ind
        if param.annotation != inspect._empty:
            vdat["ann"][name] = param.annotation
    return vdat


def sig(func: Callable, ver: Callable) -> List[str]:
    """
    Takes 2 functions, the first function is verified to have a parameter signature
    compatible with the second function
    """
    errors = []
    fsig = inspect.signature(func)
    fparams = list(fsig.parameters.values())
    vdat = sig_map(ver)
    arg_len = len(vdat["args"])
    v_pos = False
    f_name = getattr(func, "__name__", func.__class__.__name__)
    for ind in range(len(fparams)):
        param = fparams[ind]
        val = param.kind.value
        name = param.name
        has_default = param.default != inspect._empty
        ann = param.annotation

        vann = vdat["ann"].get(name, NO_TYPE_ANNOTATION)
        # Only enforce type if one is given in the signature, it won't be for *args and **kwargs
        if vann is not NO_TYPE_ANNOTATION and vann != ann:
            errors.append(f'{f_name}: Parameter "{name}" is type "{ann}" not "{vann}"')

        if val == inspect._POSITIONAL_ONLY or val == inspect._POSITIONAL_OR_KEYWORD:
            if ind >= arg_len:  # Past available positional args
                if not vdat["v_pos"] == -1:  # Has a *args
                    if ind >= vdat["v_pos"] and v_pos:
                        # Invalid unless it is a kw
                        if name not in vdat["kw"]:
                            # Is a kw
                            errors.append(f'Parameter "{name}" is invalid')
                        if vdat["kwargs"] is False:
                            errors.append(
                                f'{f_name}: Parameter "{name}" not defined as kw only'
                            )
                        continue
                elif vdat["kwargs"] is not False and not has_default:
                    errors.append(
                        f'{f_name}: Parameter "{name}" is past available positional params'
                    )
                elif vdat["kwargs"] is False:
                    errors.append(
                        f'{f_name}: Parameter "{name}" is past available positional params'
                    )
            else:
                v_param = vdat["args"][ind]
                if v_param != name:
                    errors.append(
                        f'{f_name}: Parameter "{name}" does not have the correct name: {v_param}'
                    )
        elif val == inspect._VAR_POSITIONAL:
            v_pos = True
            if vdat["v_pos"] == -1:
                errors.append(f"{f_name}: *args are not permitted as a parameter")
            elif ind < vdat["v_pos"]:
                errors.append(
                    f'{f_name}: Parameter "{name}" is not in the correct position for *args'
                )
        elif val == inspect._KEYWORD_ONLY:
            if name not in vdat["kw"] and not vdat["kwargs"]:
                errors.append(
                    f'{f_name}: Parameter "{name}" is not available as a kwarg'
                )
        elif val == inspect._VAR_KEYWORD:
            if vdat["kwargs"] is False:
                errors.append(f"{f_name}: **kwargs are not permitted as a parameter")
    return errors


def sync(func: Callable, ver: Callable) -> List[str]:
    """
    Compare two functions and make sure that they match in being synchronous or asynchronous
    """
    errors = []
    f_name = getattr(func, "__name__", func.__class__.__name__)

    f_type = func_type(func)
    v_type = func_type(ver)

    if "async" in v_type and "async" not in f_type:
        errors.append(f"{f_name}: Function must be asynchronous")
    if "gen" in v_type and "gen" not in f_type:
        errors.append(
            f"{f_name}: Function does not yield, generator required by signature"
        )

    return errors


def func_type(func: Callable) -> str:
    if inspect.iscoroutinefunction(func):
        return "asynchronous"
    elif inspect.isasyncgenfunction(func):
        return "asynchronous generator"
    elif inspect.isgenerator(func):
        return "generator"
    else:
        return "synchronous"
