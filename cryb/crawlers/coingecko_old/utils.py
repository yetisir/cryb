import os
import pathlib
from functools import wraps
import hashlib
import pickle
import json


def cache(path=None, ignore_self=False):
    """Decorator to cache the results of large queries to a serialized file"""

    path = cache_path(path)

    def decorator(function):
        # TODO: migrate to redis

        # get list of cached reults
        if os.path.isdir(path):
            cache_hashes = os.listdir(path)
        else:
            os.makedirs(path)
            cache_hashes = []

        @wraps(function)
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
        return wrapper
    return decorator


def cache_path(path=None):
    if path is None:
        return pathlib.Path(os.getcwd()) / 'cache'
    else:
        return pathlib.Path(path)


def in_cache(json_args, path=None):
    path = cache_path(path)
    args_hash = json_hash(json_args)
    cache_hashes = os.listdir(path)
    return args_hash in cache_hashes


def json_hash(json_args):
    return hashlib.sha256(json.dumps(json_args).encode('utf-8')).hexdigest()
