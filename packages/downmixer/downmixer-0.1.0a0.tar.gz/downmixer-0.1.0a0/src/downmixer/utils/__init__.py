from __future__ import annotations


def merge_dicts_with_priority(dict1: dict, dict2: dict | None) -> dict:
    """Merges two dictionaries with priority to `dict1`.

    All keys and values from `dict1` will be returned in the new dictionary, substituting keys with different
    values from `dict2`. Keys and values exclusive to `dict2` will be returned as well. The function is
    recursively called for all nested dictionaries.

    Args:
        dict1 (dict): Priority dictionary to merge. Values in dict1 are always in the returned dictionary.
        dict2 (dict): Secondary dictionary to merge.

    Returns:
        dict: Merged dictionary.
    """
    new_dict = dict1.copy()

    if dict2 is not None:
        for key, value in dict2.items():
            if (
                key in new_dict
                and isinstance(new_dict[key], dict)
                and isinstance(value, dict)
            ):
                new_dict[key] = merge_dicts_with_priority(new_dict[key], value)
            elif key not in new_dict:
                new_dict[key] = value

    return new_dict
