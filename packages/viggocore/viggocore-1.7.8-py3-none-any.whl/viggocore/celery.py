from flask import Flask
from flask.globals import current_app
from celery import Celery

celery = Celery('viggocore')


def init_celery(app: Flask) -> Celery:
    celery.conf.update(broker_url=app.config['CELERY_BROKER_URL'])
    #    result_backend=app.config['CELERY_BACKEND_URL'])
    celery.conf.update(task_queue_max_priority=10)
    celery.conf.update(worker_prefetch_multiplier=16)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def decide_on_run(fn):
    def wrapper(*args, priority=None):
        should_use_worker = current_app.config['USE_WORKER']
        fn.priority = priority
        if should_use_worker:
            return fn.delay(*args)
        else:
            return fn(*args)
    return wrapper
