import time
from functools import wraps

def performance_counter(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        duration = time.perf_counter() - start
        print(f"{func.__name__} executed in {duration:.2f} seconds")
        return result

    return wrapper
