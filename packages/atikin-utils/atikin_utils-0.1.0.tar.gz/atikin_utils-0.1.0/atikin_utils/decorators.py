import time
import functools


def timeit(func):
    """Decorator to measure execution time of a function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"[timeit] {func.__name__} took {end - start:.4f}s")
        return result
    return wrapper


def retry(tries=3, delay=1, exceptions=(Exception,)):
    """Retry decorator with delay."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, tries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    print(f"[retry] Attempt {attempt} failed: {e}")
                    time.sleep(delay)
            raise last_exc
        return wrapper
    return decorator
