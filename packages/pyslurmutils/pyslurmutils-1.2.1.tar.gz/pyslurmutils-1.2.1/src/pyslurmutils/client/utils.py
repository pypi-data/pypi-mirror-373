from typing import Mapping, Optional


def merge_mappings(d1: Optional[Mapping], d2: Optional[Mapping]) -> dict:
    """Same as `{**d1, **d2}` but then recursive"""
    if d1 is None:
        merged = dict()
    else:
        merged = dict(d1)
    if not d2:
        return merged
    for key, value2 in d2.items():
        value1 = merged.get(key)
        if isinstance(value1, Mapping) and isinstance(value2, Mapping):
            value2 = merge_mappings(value1, value2)
        merged[key] = value2
    return merged
