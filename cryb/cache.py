import requests_cache

from . import connections


def setup():
    backend = requests_cache.backends.RedisCache(
        connection=connections.redis_client())
    requests_cache.install_cache(backend=backend)


def has_url(url):
    cache = requests_cache.get_cache()
    if not cache:
        return False

    return cache.has_url(url)
