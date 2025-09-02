import sys
import importlib.util

from functools import wraps
from halo import Halo


def is_notebook():
    """True => Halo not working"""
    try:
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return True
        elif shell == "TerminalInteractiveShell":
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter


def lazy_call(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        def inner_call(**late_kwargs):
            complete_kwargs = {**kwargs, **late_kwargs}
            return f(*args, **complete_kwargs)

        return inner_call

    return wrapper


def with_spinner(
    text="Processing...",
    msg_success="Completed!",
    msg_failed="An error occurred!",
    spinner_type="dots",
):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if is_notebook() is False:
                spinner = Halo(text=text, spinner=spinner_type)
                spinner.start()
                try:
                    result = func(*args, **kwargs)
                    spinner.succeed(msg_success)
                    spinner.stop()
                    return result
                except Exception as e:
                    spinner.fail(msg_failed)
                    raise e
            else:
                result = func(*args, **kwargs)
                return result

        return wrapper

    return decorator


def module_exists(module_name):
    """Check if a module is installed."""
    module_spec = importlib.util.find_spec(module_name)
    return module_spec is not None
