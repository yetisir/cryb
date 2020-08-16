from queue import Empty
from kombu import Queue
from celery import Celery
from functools import wraps
import requests
import json

from . import cache, connections, proxies, celery
from .config import config


# def run():
#     cache.setup()
#     requests.get(
#         'http://httpbin.org/ip')


# @celery.task(bind=True)
# def request(self, queue, url, max_retries=10):
#     # print('**************')
#     # acquiring broker connection from pool
#     with celery.connection_for_read() as connection:
#         print(connection, queue)
#         # getting token
#         msg = connection.default_channel.basic_get(
#             f'{queue}_tokens', no_ack=True)
#         print(msg)
#         # received None - queue is empty, no tokens
#         if msg is None:
#             # repeat task after 1 second
#             raise self.retry(countdown=1)

#         response = requests.get(url)

#         return response


@celery.task(bind=True)
def request(self, url, queue=None, max_retries=None):
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
            return response.status_code()
