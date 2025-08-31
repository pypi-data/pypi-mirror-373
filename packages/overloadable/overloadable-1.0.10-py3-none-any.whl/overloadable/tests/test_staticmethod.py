import unittest
from typing import *

from overloadable.core import *


class Example:
    @Overloadable
    @staticmethod
    def hello(x: Any) -> type:
        return type(x)

    @hello.overload(int)
    def hello(x: int) -> int:
        return x**2

    @hello.overload(str)
    def hello(x: str) -> str:
        return x[::-1]

    @hello.overload(float)
    def hello(x: float) -> int:
        return round(x)


class TestBar(unittest.TestCase):
    def test_foo(self: Self) -> None:
        example: Example = Example()
        self.assertEqual(25, example.hello(5))
        self.assertEqual("dlrow", example.hello("world"))
        self.assertEqual(7, example.hello(6.7))
        self.assertEqual(25, Example.hello(5))
        self.assertEqual("dlrow", Example.hello("world"))
        self.assertEqual(7, Example.hello(6.7))


if __name__ == "__main__":
    unittest.main()
