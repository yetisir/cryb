from queue import Empty
from kombu import Queue
from celery import Celery
from functools import wraps
import requests
import json

from . import cache, connections, proxies, celery
from .config import config


@celery.task(bind=True)
def request(self, url, queue=None, use_cache=True, max_retries=None):
    if use_cache:
        cache.setup()

    with celery.connection_for_read() as connection:
        token = None
        while token is None:
            token = connection.default_channel.basic_get(
                f'{queue}_tokens', no_ack=True)

    return parse_response(
        requests.get(url, timeout=(5.0, 30.0)))


@celery.task
def issue_token():
    return 1


def parse_response(response):
    try:
        return response.json()
    except json.JSONDecodeError:
        if response.status_code == 200:
            return response.text
        else:
            return response.status_code
