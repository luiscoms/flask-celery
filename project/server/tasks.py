import os
import random
import time

from celery import Celery, subtask, group

from celery.states import RECEIVED

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379')
celery.conf.result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')


@celery.task(name='create_task')
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return True


@celery.task(name='migrate')
def migrate(_id):
    time.sleep(random.randint(1, 10))
    return True


@celery.task(bind=True)
def long_task(self):
    # raise Exception
    self.update_state(state=RECEIVED)
    time.sleep(3)
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(10, 50)
    job = group([
        subtask(create_task).delay(1),
        subtask(create_task).delay(1),
    ])
    return job.apply_async()
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
