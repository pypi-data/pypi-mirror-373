import dataclasses
from datetime import datetime
from typing import Any, Iterable, Mapping, Union


POD = Union[None, str, int, frozenset['POD'], tuple['POD', ...], dict[str, 'POD']]


def PODify(x: Any) -> POD:
    if isinstance(x, (type(None), str, int)):
        return x
    if isinstance(x, (set, frozenset)):
        return frozenset(PODify(e) for e in x)
    if isinstance(x, Mapping):
        ret: dict[str, POD] = dict()
        for k, v in x.items():
            ret[str(k)] = PODify(v)
        return ret
    if isinstance(x, Iterable):
        return tuple(PODify(e) for e in x)
    if isinstance(x, datetime):
        return str(x)
    if dataclasses.is_dataclass(x) and not isinstance(x, type):
        return tuple(PODify(e) for e in dataclasses.astuple(x))
    raise ValueError
