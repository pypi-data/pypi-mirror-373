import unittest
from typing import *

from overloadable.core import overloadable


class Bar:

    addon: Any

    def __init__(self: Self, addon: Any) -> None:
        self.addon = addon

    @overloadable
    def foo(self: Self, x: Any) -> Optional[str]:
        if type(x) is int:
            return "int"

    @foo.overload("int")
    def foo(self: Self, x: int) -> Any:
        return x * x + self.addon

    @foo.overload()  # key=None
    def foo(self: Self, x: Any) -> str:
        return str(x)[::-1]

    @overloadable
    @classmethod
    def baz(cls: type, x: Any) -> bool:
        return hasattr(x, "__iter__")

    @baz.overload(True)
    def baz(cls: type, x: Iterable) -> list:
        return list(x)[::-1]

    @baz.overload(False)
    def baz(cls: type, x: Any) -> str:
        return cls.__name__ + " " + str(x)

    @overloadable
    @staticmethod
    def qux(x: Any) -> bool:
        return isinstance(x, int)

    @qux.overload(True)
    @staticmethod
    def qux(x: Any) -> str:
        return "Even" if x % 2 == 0 else "Odd"

    @qux.overload(False)
    @staticmethod
    def qux(x: Any) -> str:
        return "Not an int"


class TestBar(unittest.TestCase):
    def test_foo(self: Self) -> None:
        bar: Bar = Bar(42)
        self.assertEqual(bar.foo(1), 43)
        self.assertEqual(bar.foo(3.14), "41.3")
        self.assertEqual(bar.foo("baz"), "zab")

    def test_baz(self: Self) -> None:
        bar: Bar = Bar(42)
        self.assertEqual(bar.baz({42}), [42])
        self.assertEqual(bar.baz("42"), ["2", "4"])
        self.assertEqual(bar.baz(3.14), "Bar 3.14")
        self.assertEqual(Bar.baz({42}), [42])
        self.assertEqual(Bar.baz("42"), ["2", "4"])
        self.assertEqual(Bar.baz(3.14), "Bar 3.14")
        self.assertEqual(Bar.baz(x={42}), [42])
        self.assertEqual(Bar.baz(x="42"), ["2", "4"])
        self.assertEqual(Bar.baz(x=3.14), "Bar 3.14")

    def test_qux(self: Self) -> None:
        self.assertEqual(Bar.qux(5), "Odd")
        self.assertEqual(Bar.qux(4), "Even")
        self.assertEqual(Bar.qux("not an int"), "Not an int")
        self.assertEqual(Bar.qux(15), "Odd")
        self.assertEqual(Bar.qux(100), "Even")


if __name__ == "__main__":
    unittest.main()
