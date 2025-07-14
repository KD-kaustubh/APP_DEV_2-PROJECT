class Config():
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class LocalDevelopmentConfig(Config):
    #configuration for local development
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///vpa.sqlite3'

    #config for security
    SECRET_KEY = 'this_is_a_secret_key' #hash user cred in sessions
    SECURITY_PASSWORD_HASH = 'bcrypt' #mech for hasing pswd
    SECURITY_PASSWORD_SALT = 'this_is_a_salt' # it hels in hash pswd
    WTF_CSRF_ENABLED = False #form protection
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'
