from celery import Celery
from kombu import Queue

from .config import config
from . import connections


def get_task_queues():
    task_queues = []
    for destination in config.destinations:
        task_queues.append(Queue(destination.domain))
        if destination.rate_limit:
            task_queues.append(
                Queue(f'{destination.domain}_tokens', max_length=2))
    return task_queues


celery = Celery('cryb', broker=connections.rabbitmq(), backend='rpc://')
# celery.conf.task_queues = get_task_queues()
