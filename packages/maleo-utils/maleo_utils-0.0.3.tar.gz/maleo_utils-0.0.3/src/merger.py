from collections.abc import Mapping
from typing import Union
from maleo.types.base.dict import StringToAnyDict
from maleo.types.base.mapping import StringToAnyMapping


def merge_dicts(*obj: StringToAnyDict) -> StringToAnyDict:
    def _merge(
        a: Union[StringToAnyDict, StringToAnyMapping],
        b: Union[StringToAnyDict, StringToAnyMapping],
    ) -> StringToAnyDict:
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
