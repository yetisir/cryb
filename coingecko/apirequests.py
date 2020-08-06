import asyncio
import datetime
import time

import pycoingecko

import utils
import config

# TODO: handle globals better
api = pycoingecko.CoinGeckoAPI()
queue = asyncio.Queue()
jobs = {}


class Timer():
    def __init__(self, request_delay=None):
        self.last_request = datetime.datetime.fromtimestamp(0)
        self.lock = False

        if request_delay is None:
            request_delay = config.settings['request_delay']
        self.request_delay = request_delay

    def limit_rate(self, worker):
        return
        # print(self.lock, worker)
        # if not self.lock:
        #     self.lock = worker
        #     if self.lock == worker:
        now = datetime.datetime.utcnow()
        request_diff = now - self.last_request
        self.last_request = datetime.datetime.utcnow()
        if request_diff < datetime.timedelta(self.request_delay):
            time.sleep(request_diff)
        #         self.lock = False

        #     else:
        #         self.lock = False
        #         self.limit_rate(worker)
        # else:
        #     self.lock = False
        #     self.limit_rate(worker)


timer = Timer()


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

    print('add', method_name, queue.qsize())
    await jobs[item['id']]['event'].wait()

    return jobs[item['id']]['response']


# @utils.cache()
async def api_request(method_name, *args, **kwargs):
    method = getattr(api, method_name)
    return method(*args, **kwargs)


async def worker(name):
    while True:
        print(name, queue.qsize())

        request = await queue.get()
        print(name, 'after', queue.qsize())
        timer.limit_rate(name)

        response = await api_request(request['method_name'], *request['args'], **request['kwargs'])
        print(name, 'after1')

        if response is None and request['attempt'] <= config.settings['max_retries']:
            loop = asyncio.get_event_loop()
            loop.create_task(
                add(request['method_name'], request['attempt'] +
                    1, *request['args'], **request['kwargs']))
        else:
            jobs[request['id']]['response'] = response
            jobs[request['id']]['event'].set()

        # queue.task_done()


async def run():
    tasks = []
    for i in range(config.settings['concurrent_requests']):
        loop = asyncio.get_event_loop()
        task = loop.create_task(worker(f'worker-{i}'))
        tasks.append(task)

    await queue.join()
    # print('test3')

    # for task in tasks:
    #     print('test5')
    #     task.cancel()

    # await asyncio.gather(*tasks, return_exceptions=True)


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
