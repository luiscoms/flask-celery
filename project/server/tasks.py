import os
import random
import time
from datetime import datetime

from celery import Celery, group
from celery.states import STARTED
from celery.utils.log import get_task_logger

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379')
celery.conf.result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')
celery.conf.worker_redirect_stdouts_level = 'DEBUG'

logger = get_task_logger(__name__)


@celery.task(bind=True, name='create_task')
def create_task(self, task_type):
    self.update_state(state=STARTED)
    logger.info('Start task')
    logger.error('Start task')
    time.sleep(int(task_type) * random.randint(1, 3))
    if bool(random.getrandbits(1)):
        exc = Exception('Error')
        logger.error(f'Will retry {exc}')
        raise exc
        # raise self.retry(exc=exc, max_retries=1, countdown=30)
    logger.info('Finished task')
    logger.error('Finished task')
    return True


@celery.task(name='migrate')
def migrate(_id):
    time.sleep(random.randint(1, 10))
    return True


@celery.task(bind=True)
def long_task(self):
    # raise Exception
    self.update_state(state=STARTED)
    # time.sleep(3)
    time.sleep(0.5)
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(10, 50)
    # job = group([
    #     create_task.s(1),
    #     create_task.s(1),
    # ])

    job = group([
        create_task.s(1),
        create_task.s(1),
    ])
    res = job.delay()
    completed = 0
    finished = False
    msg = ''
    # while not finished:
    while True:
        states = [s.state for s in res]
        # _finished = [state in ('SUCCESS', 'FAILURE') for state in states]
        _finished = [r.ready() for r in res]
        finished = all(_finished)

        completed = res.completed_count()

        msg = f'Completed {completed} {datetime.now()} {res} {states} ready:{res.ready()} finished:{finished}'
        self.update_state(state='PROGRESS', meta=msg)
        if res.ready():
            break
        time.sleep(0.7)

    if res.failed():
        raise Exception(msg)
    return msg

    return job.delay()
    # return job.apply_async()
    for i in range(total):
        # if not message or random.random() < 0.25:
        message = '{} of {} {} {} {}...'.format(i,
                                                total,
                                                random.choice(verb),
                                                random.choice(adjective),
                                                random.choice(noun))
        # self.update_state(state='PROGRESS',
        #                   meta={'current': i, 'total': total,
        #                         'status': message})
        self.update_state(state='PROGRESS',
                          meta=message)
        time.sleep(1)
    message = {'current': 100, 'total': 100, 'status': 'Task completed!',
               'result': 42}
    message = f'{total} of {total} Task completed!'
    return message
