import asyncio
import datetime
import time
import functools
import logging
import requests

import pycoingecko

import utils
import config


api = pycoingecko.CoinGeckoAPI()


class Queue(asyncio.Queue):

    def __init__(self):

        super().__init__()
        self.calls = []
        self.jobs = {}

        self.last_request = time.time()
        self.lock = asyncio.Lock()

        self.rate_limit = config.settings['rate_limit']
        self.rate_timeframe = config.settings['rate_timeframe']
        self.request_delay = self.rate_timeframe / self.rate_limit

    async def get(self):
        request = await super().get()

        cache_request = {
            'args': (request['method_name'], ) + request['args'],
            'kwargs': request['kwargs']
        }

        if utils.in_cache(cache_request):
            return request

        async with self.lock:
            request_diff = (time.time() - self.last_request)

            if request_diff < self.request_delay:
                await asyncio.sleep(self.request_delay - request_diff)

            self.last_request = time.time()

        now = time.time()
        self.calls.append(now)
        self.calls = [call for call in self.calls if (
            now - call) < self.rate_timeframe]
        rate = (
            len(self.calls) /
            (time.time() - self.calls[0]) * self.rate_timeframe
        )
        logging.info(
            f'API access rate: {rate} requests/{self.rate_timeframe}s')
        return request

    async def add(self, method_name, *args, attempt=1, **kwargs):
        item = {
            'method_name': method_name,
            'args': args,
            'kwargs': kwargs,
        }
        item['id'] = utils.json_hash(item)
        item['attempt'] = attempt

        self.put_nowait(item)

        self.jobs[item['id']] = {
            'event': asyncio.Event(),
            'response': None,
        }
        await self.jobs[item['id']]['event'].wait()

        return self.jobs[item['id']]['response']


class WorkerPool:
    queue = Queue()

    def __init__(self, workers=None):
        self.workers = workers

    async def worker(self):
        while True:
            request = await self.queue.get()

            loop = asyncio.get_event_loop()
            partial = functools.partial(
                api_request, request['method_name'], *request['args'], **request['kwargs'])
            response = await loop.run_in_executor(None, partial)
            self.queue.jobs[request['id']]['response'] = response
            self.queue.jobs[request['id']]['event'].set()

    async def run(self):
        await asyncio.gather(
            *[self.worker() for _ in range(self.workers)])


@utils.cache()
def api_request(method_name, *args, **kwargs):
    method = getattr(api, method_name)
    return method(*args, **kwargs)


async def run():
    workers = WorkerPool(config.settings['concurrent_requests'])
    await workers.run()


async def add(method_name, *args, **kwargs):
    return await WorkerPool.queue.add(method_name, *args, **kwargs)
