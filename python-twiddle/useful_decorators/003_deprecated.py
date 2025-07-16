import warnings
from deprecated import deprecated # needs: pip install Deprecated

@deprecated("use sum(args) instead", version="1.0.0")
def add(x: int, y: int) -> int:
    return x + y

if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=DeprecationWarning) # try without
    print(add(5, 7))