from functools import wraps


from celery import Celery
from kombu import Queue
from queue import Empty

app = Celery('hello', broker='amqp://guest@localhost//')

task_queues = [
    Queue('github'),
    Queue('google')
]

# per minute rate
rate_limits = {
    'github': 60,
    'google': 100
}

# generating queues for all groups with limits, that we defined in dict above
task_queues += [Queue(name+'_tokens', max_length=2)
                for name, limit in rate_limits.items()]

app.conf.task_queues = task_queues


@app.task
def token():
    return 1


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # generating auto issuing of tokens for all lmited groups
    for name, limit in rate_limits.items():
        sender.add_periodic_task(
            60 / limit, token.signature(queue=name+'_tokens'))

# I really like decorators ;)


def rate_limit(task_group):
    def decorator_func(func):
        @wraps(func)
        def function(self, *args, **kwargs):
            with self.app.connection_for_read() as conn:
                # Here I used another higher level method
                # We are getting complete queue interface
                # but in return losing some perfomance because
                # under the hood there is additional work done
                with conn.SimpleQueue(task_group+'_tokens', no_ack=True, queue_opts={'max_length': 2}) as queue:
                    try:
                        # Another advantage is that we can use blocking call
                        # It can be more convenient than calling retry() all the time
                        # However, it depends on the specific case
                        queue.get(block=True, timeout=5)
                        return func(self, *args, **kwargs)
                    except Empty:
                        self.retry(countdown=1)
        return function
    return decorator_func

# much more beautiful and readable with decorators, agree?
@app.task(bind=True, max_retries=None)
@rate_limit('github')
def get_github_api1(self):
    print('Called github Api 1')


@app.task(bind=True, max_retries=None)
@rate_limit('github')
def get_github_api2(self):
    print('Called github Api 2')


@app.task(bind=True, max_retries=None)
@rate_limit('google')
def query_google_api1(self):
    print('Called Google Api 1')


@app.task(bind=True, max_retries=None)
@rate_limit('google')
def query_google_api2(self):
    print('Called Google Api 2')
