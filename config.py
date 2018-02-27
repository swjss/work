class Config(object):
    SECRET_KEY = 'abcdefg'

class ProdConfig(Config):
    pass

class DevConfig(Config):
    debug = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"

