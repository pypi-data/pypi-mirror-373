import unittest
from typing import *

from overloadable.core import *


@Overloadable
def hello(x: Any) -> type:
    return type(x)


@hello.overload(int)
def hello(x: int) -> int:
    return x**2


@hello.overload(str)
def hello(x: str) -> str:
    return x[::-1]


class TestBar(unittest.TestCase):
    def test_foo(self: Self) -> None:
        self.assertEqual(25, hello(5))
        self.assertEqual("dlrow", hello("world"))


if __name__ == "__main__":
    unittest.main()
