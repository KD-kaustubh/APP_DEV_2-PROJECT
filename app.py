from flask import Flask
from application.database import db
from application.models import User, Role, UsersRoles
from application.config import LocalDevelopmentConfig
from flask_security import Security, SQLAlchemyUserDatastore,hash_password
from application.routes import main_bp
from application.celery_init import celery_init_app
# from application import celery
from celery.schedules import crontab
from application.task import monthly_report
from flask_caching import Cache 
from application import cache



def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)

    db.init_app(app)

    cache.init_app(app)
    app.cache = cache

    datastore= SQLAlchemyUserDatastore(db, User, Role)

    app.security = Security(app, datastore, register_blueprint=False)
    app.app_context().push()
    app.register_blueprint(main_bp)
    from application.resources import api  
    api.init_app(app)

    return app

app = create_app()


celery_app = celery_init_app(app)

# Import and setup celery periodic tasks
from application.celery_schedule import setup_periodic_tasks
with app.app_context():
    setup_periodic_tasks()


with app.app_context():
    db.create_all()

    app.security.datastore.find_or_create_role(name='admin', description='Superuser  of Application')
    app.security.datastore.find_or_create_role(name='user', description='Normal User of Application')
    db.session.commit()

    if not app.security.datastore.find_user(email='admin@gmail.com'):
        app.security.datastore.create_user(email='admin@gmail.com',uname='Admin', password=hash_password('admin@1234'), roles = ['admin'])
    
    if not app.security.datastore.find_user(email='user1@gmail.com'):
        app.security.datastore.create_user(email='user1@gmail.com',uname='User 1', password=hash_password('user@1234'), roles = ['user'])
    
    db.session.commit()

#hash pswd= bcypt(pwd,salt)

from application.routes import *

# @celery.on_after_finalise.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(
#         crontab(minute='*/2'), 
#         monthly_report.s())

if __name__ == '__main__':
    app.run()

