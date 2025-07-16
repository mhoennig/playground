import time
from functools import cache

@cache
def count_digits(text: str) -> int:
    """
    Counts all digits in the given text.

    :param text: the text to analyze
    :return: the number of digits in text as an integer
    """
    print(f'counting digits in: "{text}":')
    # simulate an expensive operation
    time.sleep(5)
    return sum(c.isdigit() for c in text)

def main() -> None:
    while True:
        text: str = input('Your text: ')

        if text == '@status':
            print('Status: ', count_digits.cache_info())
        elif text == '@reset':
            print('Cache reset.')
            count_digits.cache_clear()
        else:
            print(f'"{text}" contains {count_digits(text)} digits.')

if __name__ == '__main__':
    main()