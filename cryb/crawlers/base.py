from abc import ABC, abstractmethod
import asyncio

import requests

from .. import cache
from .. import worker
from ..config import config


class Crawler(ABC):

    def __init__(self):
        super().__init__()
        cache.setup()

    async def request(self, url):
        # if cache.has_url(url):
        #     return worker.parse_response(requests.get(url))

        for destination in config.destinations:
            if destination.domain in url:
                loop = asyncio.get_event_loop()
                func = worker.request.apply_async(
                    args=(url,),
                    kwargs={
                        'max_retries': config.max_retries,
                        'queue': destination.domain,
                    },
                    queue=destination.domain).wait
                return await loop.run_in_executor(None, func)
        else:
            return worker.parse_response(requests.get(url))
