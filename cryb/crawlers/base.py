from abc import ABC, abstractmethod

import requests

from .. import cache, celery
from .. import worker
from ..config import config


class Crawler(ABC):

    def __init__(self):
        super().__init__()
        cache.setup()

    def request(self, url):
        if cache.has_url(url):
            return requests.get(url)

        for destination in config.destinations:
            if url in destination.domain:
                return worker.request.apply_async(
                    args=(url,),
                    kwargs={
                        'max_retries': destination.max_retries,
                        'queue': destination.domain,
                    },
                    queue=destination.domain)
        else:
            return requests.get(url)
