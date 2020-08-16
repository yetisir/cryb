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

        for target in config.targets:
            if target.domain in url:
                loop = asyncio.get_event_loop()
                func = worker.request.apply_async(
                    args=(url,),
                    kwargs={
                        'max_retries': config.max_retries,
                        'queue': target.domain,
                        'use_cache': target.cache,
                    },
                    queue=target.domain)
                try:
                    response = await loop.run_in_executor(None, func.get)
                except Exception as e:
                    logging.warning(e)
                    logging.info(f'Celery error for url "{url}". Retrying.')
                    return await self.request(url)

                if isinstance(response, int):
                    if response == 429:
                        await asyncio.sleep(60)
                    return await self.request(url)
                else:
                    return response

        else:
            return worker.parse_response(requests.get(url))
