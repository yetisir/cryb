from celery import Celery
from kombu import Queue

from .config import config
from . import connections, cache


def get_task_queues():
    task_queues = []
    for target in config.targets:
        task_queues.append(Queue(target.domain))
        if target.rate_limit:
            task_queues.append(
                Queue(
                    f'{target.domain}_tokens',
                    max_length=2,
                ))
    return task_queues


cache.setup()

celery = Celery(
    'cryb', broker=connections.rabbitmq(), backend=connections.redis())
celery.conf.task_queues = get_task_queues()
