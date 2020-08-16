from abc import ABC, abstractmethod
import asyncio
import logging

import requests

from .. import cache
from .. import worker
from ..config import config

logging.basicConfig(level=logging.DEBUG)


class Crawler(ABC):

    def __init__(self):
        super().__init__()
        cache.setup()

    async def request(self, url):
        if cache.has_url(url):
            return worker.parse_response(requests.get(url))

        for destination in config.destinations:
            if destination.domain in url:
                loop = asyncio.get_event_loop()
                func = worker.request.apply_async(
                    args=(url,),
                    kwargs={
                        'max_retries': config.max_retries,
                        'queue': destination.domain,
                    },
                    queue=destination.domain)
                try:
                    return await loop.run_in_executor(None, func.get)
                except Exception as e:
                    logging.warn(f'Celery error for url "{url}". Retyring.')
                    return await self.request(url)
        else:
            return worker.parse_response(requests.get(url))

    # @staticmethod
    # def parse_response(response):
    #     try:
    #         return response.json()
    #     except json.JSONDecodeError:
    #         if response.status_code == 200:
    #             return response.text
    #         else:
    #             return response.status_code()
