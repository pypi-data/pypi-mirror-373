from copy import deepcopy
from functools import reduce
from typing import Dict, Any


def deep_merge(*dicts: Dict[str, Any], update: bool = False) -> Dict[str, Any]:
    """
    Deeply merges multiple dictionaries.

    Parameters
    ----------
    *dicts : Dict[str, Any]
        Variable number of dictionaries to merge.
    update : bool, optional
        If True, updates the first dictionary in-place.
        If False, creates and returns a new merged dictionary. Default is False.

    Returns
    -------
    Dict[str, Any]
        The merged dictionary.

    Notes
    -----
    - If a key's value in two dictionaries is a dictionary, they are merged recursively.
    - If a key's value in two dictionaries is a list, values from the second list
      are added to the first, avoiding duplicates.
    - For all other types, the value from the latter dictionary overwrites the former.
    """

    def merge_into(d1: Dict[str, Any], d2: Dict[str, Any]) -> Dict[str, Any]:
        for key, value in d2.items():
            if key not in d1:
                d1[key] = deepcopy(value)
            elif isinstance(d1[key], dict) and isinstance(value, dict):
                d1[key] = merge_into(d1[key], value)
            elif isinstance(d1[key], list) and isinstance(value, list):
                existing_items = set(d1[key])
                d1[key].extend(x for x in value if x not in existing_items)
                existing_items.update(
                    value
                )  # Keep the set updated for further iterations
            else:
                d1[key] = deepcopy(value)  # Overwrite with the new value
        return d1

    if update:
        # Update the first dictionary in-place
        return reduce(merge_into, dicts[1:], dicts[0])
    else:
        # Create a new dictionary for the merged result
        return reduce(merge_into, dicts, {})
