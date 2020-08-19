from abc import ABC, abstractmethod
import asyncio
import logging
import json

import requests

from . import tables
from .. import cache
from .. import worker
from ..config import config

logging.basicConfig(level=logging.DEBUG)


class Crawler(ABC):

    def __init__(self):
        super().__init__()
        cache.setup()
        tables.create_all()

    async def request(self, url, attempt=0):
        for target in config.targets:
            if target.domain in url:
                break
        else:
            target = None

        max_retries = target.max_retries if target else 10
        if attempt > max_retries:
            return 404

        if target and target.cache and cache.has_url(url):
            response = requests.get(url)
            if response.status_code == 200:
                return self.parse_response(response.text)
            else:
                return response.status_code

        loop = asyncio.get_event_loop()
        func = worker.request.apply_async(
            args=(url,),
            kwargs={
                'queue': target.domain,
            },
            queue=target.domain)
        try:
            response = await loop.run_in_executor(None, func.get)
        except Exception as exception:
            logging.warning(exception)
            logging.info(f'Celery error for url "{url}". Retrying.')
            return self.parse_response(await self.request(url, attempt=attempt+1))

        if isinstance(response, int):
            if response == 429:
                await asyncio.sleep(60)
            elif response == 404:
                return 404
            return self.parse_response(await self.request(url, attempt=attempt+1))

        return self.parse_response(response)

    def api_parameters(self, **parameters):
        parameter_list = [
            f'{parameter}={value}' for parameter, value in parameters.items()]
        parameter_url = '&'.join(parameter_list)
        return f'?{parameter_url}'.lower()

    def parse_response(self, string):
        try:
            return json.loads(string)
        except (TypeError, json.decoder.JSONDecodeError):
            return string
