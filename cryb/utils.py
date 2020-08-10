import sys
import functools
import datetime


def cli_args(function):
    """Decorator to allow cli arguments to be parsed by function

    Args:
        function (func): function to be wrapped

    Returns:
        func: wrapped function
    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        if 'args' not in kwargs:
            return function(*args, **kwargs)

        if kwargs['args'] is None:
            kwargs['args'] = sys.argv[1:]
            return function(*args, **kwargs)

    return wrapper
