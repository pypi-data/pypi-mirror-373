from copy import deepcopy
from typing import Any, Dict


def remove_none_value_keys(dict: Dict[Any, Any]):
    copy = deepcopy(dict)
    keys_to_remove = [k for k, v in dict.items() if v is None]

    for k in keys_to_remove:
        del copy[k]

    return copy
