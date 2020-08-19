
import redis as redis_module

from .config import config


def redis():
    redis_config = config.connections.redis
    return (
        f'redis://:{redis_config.password}'
        f'@{redis_config.host}:{redis_config.port}'
        f'/{redis_config.database_number}'
    )


def redis_client():
    redis_config = config.connections.redis
    return redis_module.Redis(
        host=redis_config.host,
        port=redis_config.port,
        db=redis_config.database_number,
        password=redis_config.password,
    )


def memcached():
    memcached_config = config.connections.memcached
    return (
        f'cache+memcached://{memcached_config.host}:{memcached_config.port}/'
    )


def rpc():
    return 'rpc://'


def rabbitmq():
    rabbitmq_config = config.connections.rabbitmq
    return (
        f'pyamqp://{rabbitmq_config.user}:{rabbitmq_config.password}'
        f'@{rabbitmq_config.host}:{rabbitmq_config.port}'
        f'/{rabbitmq_config.virtualhost}'
    )


def postgresql():
    postgres_config = config.connections.postgres
    return (
        f'postgres+psycopg2://{postgres_config.user}:{postgres_config.password}'
        f'@{postgres_config.host}:{postgres_config.port}'
        f'/{postgres_config.database}'
    )
