from functools import partial
from typing import Any


def maybe_bind_self(func: Any, target_self: Any):
    if "self" in func.__code__.co_varnames:
        return partial(func, target_self)
    return func
