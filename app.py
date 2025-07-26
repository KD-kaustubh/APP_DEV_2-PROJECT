from flask import Flask
from application.database import db
from application.models import User, Role, UsersRoles
from application.config import LocalDevelopmentConfig
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security import hash_password

def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    datastore= SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, datastore, register_blueprint=False)
    app.app_context().push()
    return app

app = create_app()

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

if __name__ == '__main__':
    app.run()

# It initializes the Flask app, configures it with the local development settings,sets up the database, and initializes Flask-Security for user authentication.
# The application uses Flask-SQLAlchemy for ORM and Flask-Security for user management.
# The app is configured to run in debug mode for local development.
# The database is initialized with the app context, and the security using SQLAlchemyUserDatastore which integrates Flask-Security with SQLAlchemy models.