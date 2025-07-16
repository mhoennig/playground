# inspired by https://github.com/indently/five_decorators/blob/main/decorators/001_retry.py

import time
from functools import wraps
from typing import Callable, Any
from time import sleep

def retry(retries: int = 3, delay: float = 1) -> Callable:
    """
    Calls the decorated function, retrying on failure with specified delay.

    Args:
        retries: Maximum number of retries (must be >= 1)
        delay: Delay in seconds between retries (must be > 0)
    """
    if retries < 1 or delay <= 0:
        raise ValueError('retry must be >= 1, delay must be > 0')

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(retries + 1):
                try:
                    print(f'{attempt}. try calling {func.__name__}():')
                    return func(*args, **kwargs)
                except Exception as error:
                    print(f'"{func.__name__}()" failed with {repr(error)} after {retries} retries.')
                    if attempt == retries:
                        raise
                    sleep(delay)
            return None  # never reached but avoids warning
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