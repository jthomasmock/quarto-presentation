"""
Tools to work with dicts
"""
import warnings

import dict_tools.data
import dict_tools.update

import pop.hub


def traverse(hub: "pop.hub.Hub", data, key, default=None, delimiter=":"):
    """
    Traverse a dict or list using a colon-delimited (or otherwise delimited,
    using the 'delimiter' param) target string. the target 'foo:bar:0' will
    return data['foo']['bar'][0] if this value exists, and will otherwise
    return the dict in the default argument.
    function will automatically determine the target type.
    the target 'foo:bar:0' will return data['foo']['bar'][0] if data like
    {'foo':{'bar':['baz']}} , if data like {'foo':{'bar':{'0':'baz'}}}
    then return data['foo']['bar']['0']
    """
    warnings.warn(
        "Use `dict_tools.data.traverse_dict_and_list()` instead", DeprecationWarning
    )
    return dict_tools.data.traverse_dict_and_list(data, key, default.delimiter)


def update(hub: "pop.hub.Hub", dest, upd, recursive_update=True, merge_lists=True):
    """
    Recursive version of the default dict.update

    Merges upd recursively into dest

    If recursive_update=false, will use the classic dict.update, or fall back
    on a manual merge (helpful for non-dict types like functionwrapper)

    If merge_lists=true, will aggregate list object types instead of replace.
    the list in ``upd`` is added to the list in ``dest``, so the resulting list
    is ``dest[key] + upd[key]``. This behavior is only activated when
    recursive_update=True. By default merge_lists=False.
    """
    warnings.warn(
        "Use `dict_tools.update.update()` instead", DeprecationWarning, stacklevel=1
    )
    return dict_tools.update.update(dest, upd, recursive_update, merge_lists)
