import os
import pathlib
from functools import wraps
import hashlib
import pickle
import json
import asyncio


def cache(path=None, ignore_self=False):
    """Decorator to cache the results of large queries to a serialized file"""

    if path is None:
        path = pathlib.Path(os.getcwd()) / 'cache'
    else:
        path = pathlib.Path(path)

    def decorator(function):
        # TODO: migrate to redis

        # get list of cached reults
        if os.path.isdir(path):
            cache_hashes = os.listdir(path)
        else:
            os.makedirs(path)
            cache_hashes = []

        def wrapper(*args, **kwargs):
            args_hash = json_hash({
                'args': args if not ignore_self else args[1:],
                'kwargs': kwargs
            })

            cache_file_path = path / args_hash

            # load the cache if it exists
            if args_hash in cache_hashes:
                with open(cache_file_path, 'rb') as cache_file:
                    return pickle.load(cache_file)

            # evaluate the decorated function
            result = function(*args, **kwargs)

            # cache and return the result
            with open(cache_file_path, 'wb') as cache_file:
                pickle.dump(result, cache_file)
            return result

        @wraps(function)
        def sync_wrapper(*args, **kwargs):
            return wrapper(*args, **kwargs)

        @wraps(function)
        async def async_wrapper(*args, **kwargs):
            return wrapper(*args, **kwargs)

        if asyncio.iscoroutinefunction(function):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def json_hash(json_args):
    return hashlib.sha256(json.dumps(json_args).encode('utf-8')).hexdigest()
