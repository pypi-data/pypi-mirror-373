import time
from functools import wraps

from finter.settings import logger


# Define the timer decorator
def timer(func):
    @wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()  # Start time
        value = func(*args, **kwargs)  # Call the decorated function
        end_time = time.perf_counter()  # End time
        run_time = end_time - start_time  # Calculate the runtime
        logger.info(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value

    return wrapper_timer
