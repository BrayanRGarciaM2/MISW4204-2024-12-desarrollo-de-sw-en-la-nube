import time
from celery import Celery

celery = Celery('tasks', backend='redis://redis:6379/0', broker='redis://redis:6379/0')

@celery.task(name='tasks.test')
def add(x: int, y: int) -> int:
    time.sleep(5)
    return x + y