from collections.abc import Mapping
from maleo.soma.types.base.dict import StringToAnyDict
from maleo.soma.types.base.mapping import StringToAnyMapping


def merge_dicts(*obj: StringToAnyDict) -> StringToAnyDict:
    def _merge(a: StringToAnyMapping, b: StringToAnyMapping) -> StringToAnyDict:
        result = dict(a)  # create a mutable copy
        for key, value in b.items():
            if (
                key in result
                and isinstance(result[key], Mapping)
                and isinstance(value, Mapping)
            ):
                result[key] = _merge(result[key], value)
            else:
                result[key] = value
        return result

    merged: StringToAnyDict = {}
    for ob in obj:
        merged = _merge(merged, ob)
    return merged
