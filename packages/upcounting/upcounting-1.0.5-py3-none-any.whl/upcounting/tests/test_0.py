import unittest
from typing import *

from upcounting.core import count_up


class TestCountUp(unittest.TestCase):
    def test_default_behavior(self: Self) -> None:
        gen: Generator[Any, None, None] = count_up()
        self.assertEqual(next(gen), 0)
        self.assertEqual(next(gen), 1)
        self.assertEqual(next(gen), 2)

    def test_stop_integer(self: Self) -> None:
        result: list = list(count_up(0, 5))
        self.assertEqual(result, [0, 1, 2, 3, 4])

    def test_custom_step(self: Self) -> None:
        result: list = list(count_up(0, 10, 2))
        self.assertEqual(result, [0, 2, 4, 6, 8])

    def test_negative_step(self: Self) -> None:
        result: list = list(count_up(10, 0, -2))
        self.assertEqual(result, [])

    def test_callable_stop(self: Self) -> None:
        result: list = list(count_up(0, lambda x: x > 3))
        self.assertEqual(result, [0, 1, 2, 3])

    def test_infinite_generator(self: Self) -> None:
        gen: list = count_up(5)
        x: int
        for x in range(5):
            next(gen)  # Should not raise StopIteration

    def test_stop_equal_start(self: Self) -> None:
        result: list = list(count_up(5, 5))
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
