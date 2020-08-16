import sys
from functools import wraps


def cli_args(function):

    @wraps(function)
    def wrapper(*args, **kwargs):
        if 'args' not in kwargs:
            return function(*args, **kwargs)

        if kwargs['args'] is None:
            kwargs['args'] = sys.argv[1:]
            return function(*args, **kwargs)
