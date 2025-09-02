from typing import Any


def flattened_metadata_lookup(obj: dict, key_string: str = "") -> tuple[str, Any]:
    """
    allows to flatten in nested dictionary which can be used in a lookup query
    """
    if isinstance(obj, dict):
        key_string = key_string + "__" if key_string else key_string
        for k in obj:
            yield from flattened_metadata_lookup(obj[k], key_string + str(k))
    else:
        if isinstance(obj, list):
            yield key_string + "__contains", obj
        else:
            yield key_string, obj


def merge_nested_dict(dct: dict, nested_to_merge: dict):
    """
    allows to merge 2 nested dictionaries
    """
    for k, v in nested_to_merge.items():
        if k in dct:
            if isinstance(dct[k], dict) and isinstance(nested_to_merge[k], dict):  # noqa
                merge_nested_dict(dct[k], nested_to_merge[k])
            else:
                if not isinstance(dct[k], list):
                    dct[k] = [dct[k]]
                dct[k].append(nested_to_merge[k])
        else:
            dct[k] = nested_to_merge[k]


def flattened_dict_into_nested_dict(obj: dict) -> dict:
    """
    allows to nest a flattened dictionary
    """
    nested = {}
    for key, value in obj.items():
        keys = key.split(".")
        dct = {keys.pop(): value}
        while keys:
            dct = {keys.pop(): dct}
        merge_nested_dict(nested, dct)
    return nested
