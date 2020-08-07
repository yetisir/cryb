import asyncio
import datetime
import time
import functools
import logging
import requests

import pycoingecko

import utils
import config


class Queue(asyncio.Queue):
    calls = []

    def __init__(self):

        super().__init__()
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


# TODO: handle globals better
api = pycoingecko.CoinGeckoAPI()
queue = Queue()
jobs = {}


async def add(method_name, *args, attempt=1, **kwargs):
    item = {
        'method_name': method_name,
        'args': args,
        'kwargs': kwargs,
    }
    item['id'] = utils.json_hash(item)
    item['attempt'] = attempt

    queue.put_nowait(item)

    jobs[item['id']] = {
        'event': asyncio.Event(),
        'response': None,
    }
    await jobs[item['id']]['event'].wait()

    return jobs[item['id']]['response']


@utils.cache()
def api_request(method_name, *args, **kwargs):
    method = getattr(api, method_name)
    return method(*args, **kwargs)


async def worker(name):
    while True:
        request = await queue.get()

        loop = asyncio.get_event_loop()
        partial = functools.partial(
            api_request, request['method_name'], *request['args'], **request['kwargs'])

        response = await loop.run_in_executor(None, partial)
        jobs[request['id']]['response'] = response
        jobs[request['id']]['event'].set()


async def run():
    tasks = []
    for i in range(config.settings['concurrent_requests']):
        tasks.append(worker(f'worker-{i}'))

    asyncio.gather(*tasks)

# async def request(method_name, *args, **kwargs):
#     method=getattr(self.api, method_name)
#     now=datetime.datetime.utcnow()
#     request_diff=now - self.last_request
#     if request_diff < datetime.timedelta(seconds = self.request_delay):
#         time.sleep(request_diff)
#     for _ in range(self.max_retries):
#         try:
#             result=method(*args, **kwargs)
#             time.sleep(self.request_delay)
#             self.last_request=datetime.datetime.utcnow()
#             return result
#         except:
#             time.sleep(self.request_delay)


# class Request:


#     queue=[]

#     def __init__(self, max_retries = 10, request_delay = 1):
#         if max_retries is None:
#             max_retries=config.settings['max_retries']
#         self.max_retries=max_retries

#         if request_delay is None:
#             request_delay=config.settings['request_delay']
#         self.request_delay=request_delay

#     def request(self, method_name, *args, **kwargs):
#         self.queue.append({
#             'method_name': method_name,
#             'args': args,
#             'kwargs': kwargs,
#         })

#     def send

#     @utils.cache(ignore_self = True)
#     def send_request(self, method_name, *args, **kwargs):
#         method=getattr(self.api, method_name)
#         now=datetime.datetime.utcnow()
#         request_diff=now - self.last_request
#         if request_diff < datetime.timedelta(seconds = self.request_delay):
#             time.sleep(request_diff)
#         for _ in range(self.max_retries):
#             try:
#                 result=method(*args, **kwargs)
#                 time.sleep(self.request_delay)
#                 self.last_request=datetime.datetime.utcnow()
#                 return result
#             except:
#                 time.sleep(self.request_delay)


# s


# async def worker(name, queue):
#     while True:
#         await  # request
#         queue.task_done()


# async def main(n):
#     queue = asyncio.Queue()
#     total_sleep_time = 0
#     for _ in range(20):
#         sleep_for = 1.5
#         total_sleep_top += sleep_for
#         queue.put_nowait(sleep_for)

#     tasks = []

#     for i in range(n):
#         task = asyncio.create_task(worker(f'worker-{i}', queue))
#         tasks.append(task)

#     started_at = time.monotonic()

#     await queue.join()
#     total_slept_for = time.monotonic() - started_at

#     await
