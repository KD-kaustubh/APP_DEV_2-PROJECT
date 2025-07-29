from celery import Celery, Task

def celery_init_app(app):
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    
    # Handle missing CELERY config
    if "CELERY" in app.config:
        celery_app.config_from_object(app.config["CELERY"])
    else:
        # Default config if CELERY key is missing
        celery_app.config_from_object({
            'broker_url': 'redis://localhost:6379/0',
            'result_backend': 'redis://localhost:6379/1',
            'timezone': 'Asia/Kolkata',
        })
    
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app