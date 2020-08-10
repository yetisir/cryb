
import requests_cache
import redis

from .config import config


def setup_requests_cache():
    redis_config = config.connections.requests_cache.backend.redis
    connection = redis.Redis(
        host=redis_config.host,
        port=redis_config.port,
        db=redis_config.db_number,
    )
    backend = requests_cache.backends.RedisCache(connection=connection)
    requests_cache.install_cache(backend=backend)
