import random
import string
import time
from contextlib import contextmanager


def random_string(length: int) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


@contextmanager
def catchtime(stage_name: str):
    start_time = time.monotonic()
    yield
    duration = time.monotonic() - start_time
    print(f"Execution time [{stage_name}]: {duration:.3f} seconds")



def catchtime_deco(func):
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        duration = time.monotonic() - start_time
        print(f"Execution time [{func.__name__}]: {duration:.3f} seconds")
        return result

    return wrapper

