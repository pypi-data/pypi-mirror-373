import unittest
from typing import *

from overloadable.core import *


class Example:
    def __init__(self: Self, addon: str = "hi") -> None:
        self.addon = addon

    @Overloadable
    def hello(self: Self, x: Any) -> type:
        return type(x)

    @hello.overload(int)
    def hello(self: Self, x: int) -> str:
        return self.addon * x

    @hello.overload(str)
    def hello(self: Self, x: str) -> str:
        return x + self.addon

    @hello.overload(bool)
    def hello(self: Self, x: bool) -> bool:
        return not x


class TestBar(unittest.TestCase):
    def test_foo(self: Self) -> None:
        example: Example = Example()
        self.assertEqual("hihihihihi", example.hello(5))
        self.assertEqual("worldhi", example.hello("world"))
        self.assertEqual(False, example.hello(True))
        self.assertEqual(False, Example.hello(None, True))
        self.assertEqual(False, Example.hello(42, True))


if __name__ == "__main__":
    unittest.main()
