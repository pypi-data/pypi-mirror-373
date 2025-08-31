import unittest

from overloadable.core import overloadable


class Bar:
    def __init__(self, addon) -> None:
        self.addon = addon

    @overloadable
    def foo(self, x):
        if type(x) is int:
            return "int"

    @foo.overload("int")
    def foo(self, x):
        return x * x + self.addon

    @foo.overload()  # key=None
    def foo(self, x):
        return str(x)[::-1]

    @overloadable
    @classmethod
    def baz(cls, x):
        return hasattr(x, "__iter__")

    @baz.overload(True)
    def baz(cls, x):
        return list(x)[::-1]

    @baz.overload(False)
    def baz(cls, x):
        return cls.__name__ + " " + str(x)

    @overloadable
    @staticmethod
    def qux(x):
        return isinstance(x, int)

    @qux.overload(True)
    @staticmethod
    def qux(x):
        return "Even" if x % 2 == 0 else "Odd"

    @qux.overload(False)
    @staticmethod
    def qux(x):
        return "Not an int"


class TestBar(unittest.TestCase):
    def test_foo(self):
        bar = Bar(42)
        self.assertEqual(bar.foo(1), 43)
        self.assertEqual(bar.foo(3.14), "41.3")
        self.assertEqual(bar.foo("baz"), "zab")

    def test_baz(self):
        bar = Bar(42)
        self.assertEqual(bar.baz({42}), [42])
        self.assertEqual(bar.baz("42"), ["2", "4"])
        self.assertEqual(bar.baz(3.14), "Bar 3.14")
        self.assertEqual(Bar.baz({42}), [42])
        self.assertEqual(Bar.baz("42"), ["2", "4"])
        self.assertEqual(Bar.baz(3.14), "Bar 3.14")
        self.assertEqual(Bar.baz(x={42}), [42])
        self.assertEqual(Bar.baz(x="42"), ["2", "4"])
        self.assertEqual(Bar.baz(x=3.14), "Bar 3.14")

    def test_qux(self):
        self.assertEqual(Bar.qux(5), "Odd")
        self.assertEqual(Bar.qux(4), "Even")
        self.assertEqual(Bar.qux("not an int"), "Not an int")
        self.assertEqual(Bar.qux(15), "Odd")
        self.assertEqual(Bar.qux(100), "Even")


if __name__ == "__main__":
    unittest.main()
