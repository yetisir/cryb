from celery import Celery

app = Celery(
    'tasks', broker='pyamqp://default:default@localhost:5672/cryb', backend='rpc:///')


@app.task
def add(x, y):
    return x + y
