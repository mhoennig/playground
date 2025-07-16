# inspired by https://github.com/indently/five_decorators/blob/main/decorators/001_retry.py

import time
from functools import wraps
from typing import Callable, Any
from time import sleep

def retry(retries: int = 3, delay: float = 1) -> Callable:
    """
    Calls the decorated function, if it fails, it retries with the specified delay.

    :param retries: The max number of retries, 1 means 1 try and 1 retry
    :param delay: The delay (in seconds) between each retry
    :return:
    """

    # check arguments
    if retries < 1 or delay <= 0:
        raise ValueError('retry must be => 1, delay must be > 0')

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            error = None
            try_number = 0
            while try_number <= retries:
                try:
                    print(f'{try_number}. try calling {func.__name__}():')
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f'"{func.__name__}()" failed with {repr(e)} after {retries} retries.')
                    error = e
                sleep(delay)
                try_number += 1
            raise error
        return wrapper

    return decorator

@retry(retries=3, delay=1)
def connect() -> None:
    time.sleep(1)
    raise Exception('Could not connect ...')

def main() -> None:
    connect()

if __name__ == '__main__':
    main()