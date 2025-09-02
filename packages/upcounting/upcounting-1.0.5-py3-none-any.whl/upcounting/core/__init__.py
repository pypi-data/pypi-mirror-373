from typing import *

__all__ = ["count_up"]


def count_up(
    start: Any = 0, stop: Any = None, step: Any = 1
) -> Generator[Any, None, None]:
    "This generator counts upwards."
    ans: Any = start
    while True:
        if stop is None:
            pass
        elif callable(stop):
            if stop(ans):
                break
        else:
            if ans >= stop:
                break
        yield ans
        ans += step
