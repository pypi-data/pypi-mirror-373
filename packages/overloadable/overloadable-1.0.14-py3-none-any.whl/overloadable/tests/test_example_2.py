import unittest
from typing import *

from overloadable.core import Overloadable


class Bar:

    @Overloadable
    @staticmethod
    def foo(x: Any) -> int | str:
        return type(x)

    @foo.overload(int)
    def foo(x: int) -> int:
        return x**2

    @foo.overload(str)
    def foo(x: str) -> str:
        return str(x)[::-1]


class TestBar(unittest.TestCase):
    def test_foo(self: Self) -> None:
        bar: Bar = Bar()
        self.assertEqual(bar.foo(5), 25)
        self.assertEqual(bar.foo("baz"), "zab")
        self.assertEqual(Bar.foo(5), 25)
        self.assertEqual(Bar.foo("baz"), "zab")


if __name__ == "__main__":
    unittest.main()
