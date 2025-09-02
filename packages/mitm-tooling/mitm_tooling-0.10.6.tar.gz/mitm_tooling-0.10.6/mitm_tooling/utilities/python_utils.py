import itertools
from collections.abc import Callable, Hashable, Iterable, Mapping, Sequence
from typing import Any, Literal, overload


def i_th(i: int, result_constr: type | None = tuple):
    if result_constr:
        return lambda t: result_constr(map(lambda x: x[i], t))
    else:
        return lambda t: map(lambda x: x[i], t)


def identity[T](arg: T) -> T:
    return arg


def normalize_into_dict(arg: Iterable | dict) -> dict:
    return arg if isinstance(arg, dict) else {r: r for r in arg}


def take_first[T](iterable: Iterable[T]) -> T:
    return next(iter(iterable))


def unpack_singleton[K: Hashable, T](arg: dict[K, T]) -> tuple[K, T]:
    k, v = take_first(arg.items())
    return k, v


def unpack_inner[K: Hashable, T1, T2](
    arg: Iterable[dict[K, T1]], transform: Callable[[T1], T2] = identity
) -> list[tuple[K, T2]]:
    return [(k, transform(v)) for d in arg for k, v in d.items()]


def normalize_vals[K: Hashable, T](arg: dict[K, list[T] | dict[T, T]]):
    return {k: normalize_into_dict(v) for k, v in arg.items()}


def map_vals[K: Hashable, T1, T2](arg: dict[K, T1], func: Callable[[T1], T2]) -> dict[K, T2]:
    return {k: func(v) for k, v in arg.items()}


def normalize_list_of_mixed(arg: list[str | dict[str, Any]]) -> dict[str, Any]:
    res = {}
    for c in arg:
        if isinstance(c, str):
            res[c] = None
        elif isinstance(c, dict):
            k, v = next(iter(c.items()))
            res[k] = v
    return res


def combine_dicts(d1: dict, d2: dict, defaults: dict | None = None) -> dict:
    if defaults is None:
        defaults = {}
    res = dict(d1)
    for k, v in d2.items():
        if k not in res or v is not None:
            res[k] = v
        if res[k] is None:
            res[k] = defaults.get(k, None)
    return res


def elem_wise_eq(it1: Iterable, it2: Iterable) -> Iterable[bool]:
    return map(lambda elems: elems[0] == elems[1], zip(it1, it2, strict=False))


def grouped[K: Hashable, T](it: Iterable[tuple[K, T]]) -> dict[K, list[T]]:
    res = {}
    for k, v in it:
        if k not in res:
            res[k] = []
        res[k].append(v)
    return res


def inner_list_concat[K: Hashable](d1: dict[K, list[Any]], d2: dict[K, list[Any]]) -> dict[K, list[Any]]:
    res = {k: list(vs) for k, vs in d1.items()}
    for k, vs in d2.items():
        if k not in res:
            res[k] = []
        res[k].extend(vs)
    return res


def recursively_pick_from_mapping(arg: Any, path: tuple[str, ...] | None) -> Any | None:
    if not path:
        return arg
    elif isinstance(arg, Mapping):
        return recursively_pick_from_mapping(arg.get(path[0], None), path[1:])
    return None


@overload
def pick_from_mapping[K: Hashable, T](d: Mapping[K, T], keys: Sequence[K]) -> list[T]: ...


@overload
def pick_from_mapping[K: Hashable, T](
    d: Mapping[K, T], keys: Sequence[K], *, with_key: Literal[True]
) -> list[tuple[K, T]]: ...


@overload
def pick_from_mapping[K: Hashable, T](d: Mapping[K, T], keys: Sequence[K], *, with_key: Literal[False]) -> list[T]: ...


def pick_from_mapping[K: Hashable, T](
    d: Mapping[K, T], keys: Sequence[K], *, with_key: bool = False
) -> list[T] | list[tuple[K, T]]:
    if with_key:
        return [(k, d[k]) for k in keys]
    else:
        return [d[k] for k in keys]


def unique[T](*its: Iterable[T]) -> list[T]:
    return list(set(itertools.chain(*its)))


def deep_merge_dicts(*dicts: dict) -> dict:
    """
    Recursively merges multiple dictionaries and returns the result.
    Values in later dictionaries override values in earlier ones.
    """
    result = {}
    for d in dicts:
        for key, value in d.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge_dicts(result[key], value)
            else:
                result[key] = value
    return result


def notna_kwargs(**kwargs):
    return {k: v for k, v in kwargs.items() if v is not None}


class ExtraInfoExc(Exception):
    def __init__(self, msg=None):
        super().__init__()
        if msg is not None:
            self.add_note(msg)
