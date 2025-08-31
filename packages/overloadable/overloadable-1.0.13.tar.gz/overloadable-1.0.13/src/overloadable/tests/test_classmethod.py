import unittest
from typing import *

from overloadable.core import *


class Example:
    ref = "hi"

    @Overloadable
    @classmethod
    def hello(cls: type, x: Any) -> type:
        return type(x)

    @hello.overload(int)
    def hello(cls: type, x: int) -> int:
        return x**2

    @hello.overload(str)
    def hello(cls: type, x: str) -> str:
        return cls.ref + x

    @hello.overload(float)
    def hello(cls: type, x: float) -> int:
        return round(x)


class TestBar(unittest.TestCase):
    def test_foo(self: Self) -> None:
        example: Example = Example()
        self.assertEqual(25, example.hello(5))
        self.assertEqual("hiworld", example.hello("world"))
        self.assertEqual(7, example.hello(6.7))
        self.assertEqual(25, Example.hello(5))
        self.assertEqual("hiworld", Example.hello("world"))
        self.assertEqual(7, Example.hello(6.7))
        Example.ref = "42"
        self.assertEqual("42world", example.hello("world"))
        self.assertEqual("42world", Example.hello("world"))


if __name__ == "__main__":
    unittest.main()
