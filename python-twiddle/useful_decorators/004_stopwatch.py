import random
from functools import wraps
from time import perf_counter, sleep
from typing import Callable, Any

def stopwatch(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:

        # Using the time of a single call can be misleading,
        # also check for the timeit module.
        started: float = perf_counter()
        result: Any = func(*args, **kwargs)
        end_time: float = perf_counter()

        print(f'calling "{func.__name__}()" took {end_time - started:.3f} seconds')
        return result

    return wrapper


@stopwatch
def inner_function() -> None:
    print('some inner time-consuming operation ...')
    sleep(random.uniform(0.1, 0.5))

@stopwatch
def outer_function() -> None:
    print('some outer time-consuming operation ...')
    for i in range(0, 10):
        inner_function()

def main() -> None:
    outer_function()

if __name__ == '__main__':
    main()