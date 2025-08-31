import functools
import types
from typing import *

__all__ = ["overloadable", "Overloadable"]


class Overloadable:

    __slots__ = ("dispatch", "lookup")
    dispatch: Any
    lookup: Any

    def __call__(self: Self, *args: Any, **kwargs: Any) -> Any:
        key: Any = self.dispatch(*args, **kwargs)
        value: Callable = self.lookup[key]
        ans: Any = value(*args, **kwargs)
        return ans

    def __get__(
        self: Self, *args: Any, **kwargs: Any
    ) -> types.FunctionType | types.MethodType:
        draft: Any = self.dispatch.__get__(*args, **kwargs)
        ans: Any
        try:
            obj: Any = draft.__self__
        except AttributeError:
            ans = self._deco(draft)
            return ans
        old: Callable
        try:
            old = draft.__func__
        except AttributeError:
            old = getattr(type(obj), draft.__name__)
        new: Any = self._deco(old)
        ans = types.MethodType(new, obj)
        return ans

    def __init__(self: Self, dispatch: Any) -> None:
        self.dispatch = dispatch
        self.lookup = dict()

    def _deco(self: Self, old: Callable) -> Any:
        return deco(old, lookup=dict(self.lookup))

    def overload(self: Self, key=None) -> functools.partial:
        return functools.partial(overload_, self, key)


overloadable = Overloadable


def deco(old: Callable, *, lookup: dict) -> types.FunctionType:
    def new(*args: Any, **kwargs: Any) -> Any:
        key: Any = old(*args, **kwargs)
        value: Any = lookup[key]
        ans: Any = value(*args, **kwargs)
        return ans

    ans: types.FunctionType
    try:
        ans = functools.wraps(old)(new)
    except:
        ans = new
    return ans


def overload_(master: Overloadable, key: Any, value: Callable, /) -> Overloadable:
    overload(value)
    master.lookup[key] = value
    return master
