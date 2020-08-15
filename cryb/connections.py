
import redis as redis_module

from .config import config


def redis():
    redis_config = config.connections.requests_cache.backend.redis
    return redis_module.Redis(
        host=redis_config.host,
        port=redis_config.port,
        db=redis_config.db_number,
        password=redis_config.password,
    )


def rabbitmq():
    rabbitmq_config = config.connections.task_queue.broker.rabbitmq
    return (
        f'pyamqp://{rabbitmq_config.user}:{rabbitmq_config.password}'
        f'@{rabbitmq_config.host}:{rabbitmq_config.port}'
        f'/{rabbitmq_config.virtualhost}'
    )


def postgresql():
    # TODO
    return 'sqlite:///temp.sqlite'
